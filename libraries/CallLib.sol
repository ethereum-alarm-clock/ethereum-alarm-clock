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

                address bidder;
                uint bid_amount;
                uint bidder_deposit;
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

        function get_gas_scalar(uint baseGasPrice, uint gasPrice) constant returns (uint) {
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

            if (!_call.before_execute(executor)) {
                return;
            }
            
            // Make the call
            bool success = call.contractAddress.call.gas(msg.gas - overhead)(call.abiSignature, call.callData);

            // Compute the scalar (0 - 200) for the fee.
            uint gas_scalar = get_gas_scalar(call.anchorGasPrice, tx.gasprice);

            uint payment = basePayment * gas_scalar / 100; 
            uint fee = baseFee * gas_scalar / 100;

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

        // The duration (in blocks) during which the maximum bid will slowly rise
        // towards the base_payment amount.
        uint constant BID_GROWTH_WINDOW = 240;

        // The duration (in blocks) after the BID_WINDOW that bidding will
        // remain open.
        uint constant MAXIMUM_BID_WINDOW = 15;

        // The duration (in blocks) before the call's target block during which
        // all actions are frozen.  This includes bidding, cancellation,
        // registering call data.
        uint constant BEFORE_CALL_FREEZE_WINDOW = 10;

        /*
         *  The maximum allowed bid slowly rises across a window of blocks
         *  BID_GROWTH_WINDOW prior to the call.  No bidder is allowed to bid
         *  above this value.  This is intended to prevent bidding wars in that
         *  each caller should know how much they are willing to execute a call
         *  for.
         */
        function get_bid_amount_for_block(uint block_number) constant returns (uint) {
            var _call = FutureBlockCall(this);

            uint last_block = _call.target_block() - BEFORE_CALL_FREEZE_WINDOW;
            
            // bid window has closed
            if (block_number > last_block) return _call.basePayment();

            uint first_block = last_block - MAXIMUM_BID_WINDOW - BID_GROWTH_WINDOW;
            
            // bid window has not begun
            if (block_number < first_block) return 0;

            // in the maximum bid window.
            if (block_number > last_block - MAXIMUM_BID_WINDOW) return _call.basePayment();

            uint x = block_number - first_block;

            return 100 * x / BID_GROWTH_WINDOW;
        }

        function claim(Call storage self, address executor, uint deposit_amount, uint base_payment) public returns (bool) {
                // Already claimed
                if (self.bidder != 0x0) return false;

                // Insufficient Deposit
                if (deposit_amount < 2 * base_payment) return false;

                self.bid_amount = get_maximum_bid_for_block(block.number);
                self.bidder = executor;
                self.bidder_deposit = deposit_amount;

                // Log the bid.
                Bid(executor, self.bid_amount);
        }

        function check_execution_authorization(Call storage self, address executor, uint block_number) returns (bool) {
                /*
                 *  Check whether the given `executor` is authorized.
                 */
                var call = FutureCall(this);

                uint target_block = call.target_block();

                // Call window hasn't started
                if (block_number < target_block) return false;

                if (block_number - target_block < CALL_WINDOW_SIZE) {
                    return (self.bidder == 0x0 || self.bidder == executor);
                }

                if (block_number > target_block + call.grace_period()) return false;

                return true;
        }
}


contract FutureCall {
        address public scheduler_address;

        uint public basePayment;
        uint public baseFee;

        // TODO: These *should* live on FutureBlockCall but I haven't figured
        // the modularity part out quite yet.  For now I'm going to muddle
        // these two concepts together for the sake of progress and pay this
        // debt down later.
        uint public target_block;
        uint8 public grace_period;

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
                if (msg.sender == scheduler_address && msg.data.length > 0) {
                        if (call.callData.length != 0) {
                            throw;
                        }
                        call.callData = msg.data;
                }
        }

        modifier onlyscheduler { if (msg.sender == scheduler_address) _ }

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
        function before_execute(address executor) public returns (bool);
        function after_execute(address executor) internal;
        function get_overhead() constant returns (uint);
        function get_extra_gas() constant returns (uint);

        function sendSafe(address toAddress, uint value) internal {
                CallLib.sendSafe(toAddress, value);
        }

        function execute() public {
            uint startGas = msg.gas;

            // Check that the call should be executed now.
            if (!before_execute(msg.sender)) return;

            // Execute the call
            CallLib.execute(call, startGas, msg.sender, basePayment, baseFee, get_overhead(), get_extra_gas());

            // Any logic that needs to occur after the call has executed should
            // go in after_execute
            after_execute(msg.sender);
        }
}


contract FutureBlockCall is FutureCall {
        // TODO: This it the *appropriate* place for these to live, but for
        // unfortunate reasons, they are present on the FutureCall contract
        // class.
        //uint public target_block;
        //uint8 public grace_period;

        function FutureBlockCall(address _scheduler_address, uint _target_block, uint8 _grace_period, address _contractAddress, bytes4 _abiSignature, uint _suggestedGas, uint _basePayment, uint _baseFee) {
                // TODO: split this constructor across this contract and the
                // parent contract FutureCall
                scheduler_address = _scheduler_address;

                target_block = _target_block;
                grace_period = _grace_period;


                basePayment = _basePayment;
                baseFee = _baseFee;

                call.suggestedGas = _suggestedGas;
                call.anchorGasPrice = tx.gasprice;
                call.contractAddress = _contractAddress;
                call.abiSignature = _abiSignature;
        }

        function before_execute(address executor) public returns (bool) {
                // TODO: check if executor is designated to call during this window.
                if (block.number < target_block || block.number > target_block + grace_period) {
                        // Not being called within call window.
                        CallLib.CallAborted(executor, "NOT_IN_CALL_WINDOW");
                        return false;
                }

                return true;
        }

        function after_execute(address executor) internal {
            // TODO: Remove suicide
            suicide(scheduler_address);
        }

        function get_overhead() constant returns (uint) {
                // TODO real numbers
                return 46000;
        }

        function get_extra_gas() constant returns (uint) {
                // TODO real numbers
                return 17000;
        }

        uint constant BEFORE_CALL_FREEZE_WINDOW = 10;

        function cancel() public {
                if ((block.number < target_block - BEFORE_CALL_FREEZE_WINDOW && msg.sender == scheduler_address) || block.number > target_block + grace_period) {
                        CallLib.cancel(scheduler_address);
                }
        }
}
