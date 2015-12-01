import "libraries/GroveLib.sol";


library CallLib {
        /*
         *  Address: 0x2746bcf29bffafcc7906752f639819171d18ce2b
         */
        struct Call {
                address contractAddress;
                bytes4 abiSignature;
                bytes callData;
                uint anchorGasPrice;
                uint suggestedGas;

                uint numBids;
                GroveLib.Index bids;
                mapping (address => uint) deposits;
        }

        // The number of blocks that each caller in the pool has to complete their
        // call.
        uint constant CALL_WINDOW_SIZE = 16;

        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function extractCallData(Call storage call, bytes data) public {
            call.callData.length = data.length - 4;
            if (data.length > 4) {
                    for (uint i = 0; i < call.callData.length; i++) {
                            call.callData[i] = data[i + 4];
                    }
            }
        }

        function sendSafe(address toAddress, uint value) public returns (uint) {
                if (value > address(this).balance) {
                        value = address(this).balance;
                }
                if (value > 0) {
                        AccountingLib.sendRobust(toAddress, value);
                        return value;
                }
                return 0;
        }

        function getGasScalar(uint baseGasPrice, uint gasPrice) constant returns (uint) {
                /*
                 *  Return a number between 0 - 200 to scale the fee based on
                 *  the gas price set for the calling transaction as compared
                 *  to the gas price of the scheduling transaction.
                 *
                 *  - number approaches zero as the transaction gas price goes
                 *  above the gas price recorded when the call was scheduled.
                 *
                 *  - the number approaches 200 as the transaction gas price
                 *  drops under the price recorded when the call was scheduled.
                 *
                 *  This encourages lower gas costs as the lower the gas price
                 *  for the executing transaction, the higher the payout to the
                 *  caller.
                 */
                if (gasPrice > baseGasPrice) {
                        return 100 * baseGasPrice / gasPrice;
                }
                else {
                        return 200 - 100 * baseGasPrice / (2 * baseGasPrice - gasPrice);
                }
        }

        event CallExecuted(address indexed executor, uint gasCost, uint payment, uint fee, bool success);

        event _CallAborted(address executor, bytes32 reason);
        function CallAborted(address executor, bytes32 reason) public {
            _CallAborted(executor, reason);
        }

        function execute(Call storage call, uint startGas, address executor, uint basePayment, uint baseFee, uint overhead, uint extraGas) public {
            FutureCall _call = FutureCall(this);

            if (!_call.checkExecutionAuthorization(executor, block.number)) {
                return;
            }

            if (!_call.beforeExecute(executor)) {
                return;
            }
            
            // Make the call
            bool success = call.contractAddress.call.gas(msg.gas - overhead)(call.abiSignature, call.callData);

            // Compute the scalar (0 - 200) for the fee.
            uint gasScalar = getGasScalar(call.anchorGasPrice, tx.gasprice);

            uint payment = basePayment * gasScalar / 100; 
            uint fee = baseFee * gasScalar / 100;

            // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
            // amount that represents the gas usage of the commands that
            // happen after this line.
            uint gasCost = tx.gasprice * (startGas - msg.gas + extraGas);

            // Now we need to pay the executor as well as keep fee.
            payment = sendSafe(executor, payment + gasCost);
            fee = sendSafe(creator, fee);

            // Log execution
            CallExecuted(executor, gasCost, payment, fee, success);
        }

        event Cancelled(address indexed cancelledBy);

        function cancel(address sender) public {
                Cancelled(sender);
                // TODO: remove suicide.
                suicide(sender);
        }

        /*
         *  Bid API
         *  - Gas costs for this transaction are not covered so it
         *    must be up to the call executors to ensure that their actions
         *    remain profitable.  Any form of bidding war is likely to eat into
         *    profits.
         */
        event Bid(address executor, uint bidAmount);

        function bid(Call storage self, address executor, uint bidAmount, uint depositAmount, uint basePayment) public returns (bool) {
                // Insufficient Deposit
                if (depositAmount < 2 * basePayment) return false;

                // Bid is over the declared basePayment.
                if (bidAmount > basePayment) return false;

                // Overflow, must be castable to an `int` so that Grove can
                // track it.
                if (bidAmount > 2 ** 128 - 1) return false;

                // Already Bid.
                if (GroveLib.exists(self.bids, bytes32(executor))) {
                        // Get the amount that was previously bid.
                        uint refund = uint(GroveLib.getNodeValue(self.bids, bytes32(executor)));

                        // Cannot increase bid.
                        if (refund >= bidAmount) return false;
                        AccountingLib.sendRobust(executor, refund);
                }
                else {
                        // Already reached the maximum number of bidders.
                        if (self.numBids >= getMaximumBidders()) return false;

                        // New bidder so increment the number of bids.
                        self.numBids += 1;
                }
                // Register the bid.
                GroveLib.insert(self.bids, bytes32(executor), int(bidAmount));
                self.deposits[executor] += depositAmount;
                // Log the bid.
                Bid(executor, bidAmount);
        }

        function checkBid(Call storage self, address bidder) returns (uint) {
                return uint(GroveLib.getNodeValue(self.bids, bytes32(bidder)));
        }

        function getMaximumBidders() constant returns (uint) {
                var call = FutureCall(this);
                return call.gracePeriod() / CALL_WINDOW_SIZE;
        }

        function getNthBidder(Call storage self, uint n) constant returns (address) {
                /*
                 *  Return the nth bidder (0 indexed).  Returns 0x0 if there is
                 *  no bidder in that position.
                 */
                address bidder = address(GroveLib.query(self.bids, ">=", 0));

                for (uint i=0; i < n; i++) {
                        if (bidder == 0x0) break;
                        bidder = address(GroveLib.getNextNode(self.bids, bytes32(bidder)));
                }

                return bidder;
        }

        function checkExecutionAuthorization(Call storage self, address executor, uint blockNumber) returns (bool) {
                /*
                 *  Check whether the address executing this call is
                 *  authorized.  Must be one of:
                 *  - in free-for-all window.
                 *  - no bids
                 *  - bid position is correct for call window.
                 */
                var call = FutureCall(this);

                uint8 numWindows = uint8(call.gracePeriod() / CALL_WINDOW_SIZE);
                uint8 callWindow = uint8((blockNumber - call.targetBlock()) / CALL_WINDOW_SIZE);

                if (callWindow + 2 > numWindows) {
                        // In the free-for-all period.
                        return true;
                }

                // Query for the lowest bidder.
                address bidder = getNthBidder(self, callWindow);
                if (bidder == 0x0) {
                        // No caller at that position
                        return true;
                }

                // Check that the bidder is the executor.
                return bidder == executor;
        }
}


contract FutureCall {
        address public schedulerAddress;

        uint public basePayment;
        uint public baseFee;

        // TODO: These *should* live on FutureBlockCall but I haven't figured
        // the modularity part out quite yet.  For now I'm going to muddle
        // these two concepts together for the sake of progress and pay this
        // debt down later.
        uint public targetBlock;
        uint8 public gracePeriod;

        CallLib.Call call;

        /*
         *  Data accessor functions.
         */
        function contractAddress() constant returns (address) {
                return call.contractAddress;
        }

        function abiSignature() constant returns (bytes4) {
                return call.abiSignature;
        }

        function callData() constant returns (bytes) {
                return call.callData;
        }

        function anchorGasPrice() constant returns (uint) {
                return call.anchorGasPrice;
        }

        function suggestedGas() constant returns (uint) {
                return call.suggestedGas;
        }

        function () {
                // Fallback to allow sending funds to this contract.
                // Also allows call data registration.
                if (msg.sender == schedulerAddress && msg.data.length > 0) {
                        if (call.callData.length != 0) {
                            throw;
                        }
                        call.callData = msg.data;
                }
        }

        modifier onlyscheduler { if (msg.sender == schedulerAddress) _ }

        // The author (Piper Merriam) address.
        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function registerData() public onlyscheduler {
                if (call.callData.length > 0) {
                        // cannot write over call data
                        throw;
                }
                CallLib.extractCallData(call, msg.data);
        }

        function bid(uint bidAmount) public returns (bool) {
                bool success = CallLib.bid(call, msg.sender, bidAmount, msg.value, basePayment);
                if (!success) {
                        if (!AccountingLib.sendRobust(msg.sender, msg.value)) throw;
                }
                return success;
        }

        function checkBid() constant returns (uint) {
                return checkBid(msg.sender);
        }

        function checkBid(address bidder) constant returns (uint) {
                return CallLib.checkBid(call, bidder);
        }

        function checkExecutionAuthorization(address executor, uint blockNumber) constant returns (bool) {
                return CallLib.checkExecutionAuthorization(call, executor, blockNumber);
        }

        // API for inherited contracts
        function beforeExecute(address executor) public returns (bool);
        function afterExecute(address executor) internal;
        function getOverhead() constant returns (uint);
        function getExtraGas() constant returns (uint);

        function sendSafe(address toAddress, uint value) internal {
                CallLib.sendSafe(toAddress, value);
        }

        function execute() public {
            uint startGas = msg.gas;

            // Check that the call should be executed now.
            if (!beforeExecute(msg.sender)) return;

            // Execute the call
            CallLib.execute(call, startGas, msg.sender, basePayment, baseFee, getOverhead(), getExtraGas());

            // Any logic that needs to occur after the call has executed should
            // go in afterExecute
            afterExecute(msg.sender);
        }
}


contract FutureBlockCall is FutureCall {
        // TODO: This it the *appropriate* place for these to live, but for
        // unfortunate reasons, they are present on the FutureCall contract
        // class.
        //uint public targetBlock;
        //uint8 public gracePeriod;

        function FutureBlockCall(address _schedulerAddress, uint _targetBlock, uint8 _gracePeriod, address _contractAddress, bytes4 _abiSignature, uint _suggestedGas, uint _basePayment, uint _baseFee) {
                // TODO: split this constructor across this contract and the
                // parent contract FutureCall
                schedulerAddress = _schedulerAddress;

                targetBlock = _targetBlock;
                gracePeriod = _gracePeriod;


                basePayment = _basePayment;
                baseFee = _baseFee;

                call.suggestedGas = _suggestedGas;
                call.anchorGasPrice = tx.gasprice;
                call.contractAddress = _contractAddress;
                call.abiSignature = _abiSignature;
        }

        function beforeExecute(address executor) public returns (bool) {
                // TODO: check if executor is designated to call during this window.
                if (block.number < targetBlock || block.number > targetBlock + gracePeriod) {
                        // Not being called within call window.
                        CallLib.CallAborted(executor, "NOT_IN_CALL_WINDOW");
                        return false;
                }

                return true;
        }

        function afterExecute(address executor) internal {
            // TODO: Remove suicide
            suicide(schedulerAddress);
        }

        function getOverhead() constant returns (uint) {
                // TODO real numbers
                return 46000;
        }

        function getExtraGas() constant returns (uint) {
                // TODO real numbers
                return 17000;
        }

        uint constant BEFORE_CALL_FREEZE_WINDOW = 10;

        function cancel() public {
                if ((block.number < targetBlock - BEFORE_CALL_FREEZE_WINDOW && msg.sender == schedulerAddress) || block.number > targetBlock + gracePeriod) {
                        CallLib.cancel(schedulerAddress);
                }
        }

        function getMaximumBidders() constant returns (uint) {
                return CallLib.getMaximumBidders();
        }
}

