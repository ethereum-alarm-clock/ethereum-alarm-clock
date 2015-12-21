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

                address claimer;
                uint claimAmount;
                uint claimerDeposit;

                bool wasSuccessful;
                bool wasCalled;
                bool isCancelled;
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

        function sendSafe(address to_address, uint value) public returns (uint) {
                if (value > address(this).balance) {
                        value = address(this).balance;
                }
                if (value > 0) {
                        AccountingLib.sendRobust(to_address, value);
                        return value;
                }
                return 0;
        }

        function getGasScalar(uint base_gas_price, uint gas_price) constant returns (uint) {
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
                if (gas_price > base_gas_price) {
                        return 100 * base_gas_price / gas_price;
                }
                else {
                        return 200 - 100 * base_gas_price / (2 * base_gas_price - gas_price);
                }
        }

        event CallExecuted(address indexed executor, uint gasCost, uint payment, uint fee, bool success);

        event _CallAborted(address executor, bytes32 reason);
        function CallAborted(address executor, bytes32 reason) public {
            _CallAborted(executor, reason);
        }

        function execute(Call storage self, uint start_gas, address executor, uint overhead, uint extraGas) public {
            FutureCall call = FutureCall(this);

            // If the pre-execution checks do not pass, exit early.
            if (!call.beforeExecute(executor)) {
                return;
            }
            
            // Mark the call has having been executed.
            self.wasCalled = true;
            // Make the call
            self.wasSuccessful = self.contractAddress.call.gas(msg.gas - overhead)(self.abiSignature, self.callData);

            // Compute the scalar (0 - 200) for the fee.
            uint gasScalar = getGasScalar(self.anchorGasPrice, tx.gasprice);

            uint basePayment;
            if (self.claimer == executor) {
                basePayment = self.claimAmount;
            }
            else {
                basePayment = call.basePayment();
            }
            uint payment = self.claimerDeposit + basePayment * gasScalar / 100; 
            uint fee = call.baseFee() * gasScalar / 100;

            // zero out the deposit
            self.claimerDeposit = 0;

            // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
            // amount that represents the gas usage of the commands that
            // happen after this line.
            uint gasCost = tx.gasprice * (start_gas - msg.gas + extraGas);

            // Now we need to pay the executor as well as keep fee.
            payment = sendSafe(executor, payment + gasCost);
            fee = sendSafe(creator, fee);

            // Log execution
            CallExecuted(executor, gasCost, payment, fee, self.wasSuccessful);
        }

        event Cancelled(address indexed cancelled_by);

        function cancel(Call storage self, address sender) public {
                Cancelled(sender);
                if (self.claimerDeposit >= 0) {
                    sendSafe(self.claimer, self.claimerDeposit);
                }
                var call = FutureCall(this);
                sendSafe(call.schedulerAddress(), address(this).balance);
                self.isCancelled = true;
        }

        /*
         *  Bid API
         *  - Gas costs for this transaction are not covered so it
         *    must be up to the call executors to ensure that their actions
         *    remain profitable.  Any form of bidding war is likely to eat into
         *    profits.
         */
        event Claimed(address executor, uint claimAmount);

        // The duration (in blocks) during which the maximum claim will slowly rise
        // towards the basePayment amount.
        uint constant CLAIM_GROWTH_WINDOW = 240;

        // The duration (in blocks) after the CLAIM_WINDOW that claiming will
        // remain open.
        uint constant MAXIMUM_CLAIM_WINDOW = 15;

        // The duration (in blocks) before the call's target block during which
        // all actions are frozen.  This includes claiming, cancellation,
        // registering call data.
        uint constant BEFORE_CALL_FREEZE_WINDOW = 10;

        /*
         *  The maximum allowed claim amount slowly rises across a window of
         *  blocks CLAIM_GROWTH_WINDOW prior to the call.  No claimer is
         *  allowed to claim above this value.  This is intended to prevent
         *  bidding wars in that each caller should know how much they are
         *  willing to execute a call for.
         */
        function getClaimAmountForBlock(uint block_number) constant returns (uint) {
            /*
             *   [--growth-window--][--max-window--][--freeze-window--]
             *
             *
             */
            var call = FutureBlockCall(this);

            uint last_block = call.targetBlock() - BEFORE_CALL_FREEZE_WINDOW;
            
            // claim window has closed
            if (block_number > last_block) return call.basePayment();

            uint first_block = last_block - MAXIMUM_CLAIM_WINDOW - CLAIM_GROWTH_WINDOW;
            
            // claim window has not begun
            if (block_number < first_block) return 0;

            // in the maximum claim window.
            if (block_number > last_block - MAXIMUM_CLAIM_WINDOW) return call.basePayment();

            uint x = block_number - first_block;

            return call.basePayment() * x / CLAIM_GROWTH_WINDOW;
        }

        function claim(Call storage self, address executor, uint deposit_amount, uint basePayment) public returns (bool) {
                // Already claimed
                if (self.claimer != 0x0) return false;

                // Insufficient Deposit
                if (deposit_amount < 2 * basePayment) return false;

                var call = FutureBlockCall(this);

                // Too early
                if (block.number < call.targetBlock() - BEFORE_CALL_FREEZE_WINDOW - MAXIMUM_CLAIM_WINDOW - CLAIM_GROWTH_WINDOW) return false;

                // Too late
                if (block.number > call.targetBlock() - BEFORE_CALL_FREEZE_WINDOW) return false;
                self.claimAmount = getClaimAmountForBlock(block.number);
                self.claimer = executor;
                self.claimerDeposit = deposit_amount;

                // Log the claim.
                Claimed(executor, self.claimAmount);
        }

        function checkExecutionAuthorization(Call storage self, address executor, uint block_number) returns (bool) {
                /*
                 *  Check whether the given `executor` is authorized.
                 */
                var call = FutureBlockCall(this);

                uint targetBlock = call.targetBlock();

                // Invalid, not in call window.
                if (block_number < targetBlock || block_number > targetBlock + call.gracePeriod()) throw;

                // Within the reserved call window so if there is a claimer, the
                // executor must be the claimdor.
                if (block_number - targetBlock < CALL_WINDOW_SIZE) {
                    return (self.claimer == 0x0 || self.claimer == executor);
                }

                // Must be in the free-for-all period.
                return true;
        }
}


contract FutureCall {
        address public schedulerAddress;

        uint public basePayment;
        uint public baseFee;

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

        function claimer() constant returns (address) {
            return call.claimer;
        }

        function claimAmount() constant returns (uint) {
            return call.claimAmount;
        }

        function claimerDeposit() constant returns (uint) {
            return call.claimerDeposit;
        }

        function wasSuccessful() constant returns (bool) {
            return call.wasSuccessful;
        }

        function wasCalled() constant returns (bool) {
            return call.wasCalled;
        }

        function isCancelled() constant returns (bool) {
            return call.isCancelled;
        }

        function getClaimAmountForBlock() constant returns (uint) {
            return CallLib.getClaimAmountForBlock(block.number);
        }

        function getClaimAmountForBlock(uint block_number) constant returns (uint) {
            return CallLib.getClaimAmountForBlock(block_number);
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

        modifier notcancelled { if (call.isCancelled) throw; _ }

        // The author (Piper Merriam) address.
        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function registerData() public notcancelled {
            if (msg.sender != schedulerAddress || call.callData.length > 0) {
                // cannot write over call data
                throw;
            }
            CallLib.extractCallData(call, msg.data);
        }

        function claim() public notcancelled returns (bool) {
            bool success = CallLib.claim(call, msg.sender, msg.value, basePayment);
            if (!success) {
                if (!AccountingLib.sendRobust(msg.sender, msg.value)) throw;
            }
            return success;
        }

        function checkExecutionAuthorization(address executor, uint block_number) constant returns (bool) {
            return CallLib.checkExecutionAuthorization(call, executor, block_number);
        }

        // API for inherited contracts
        function beforeExecute(address executor) public returns (bool);
        function afterExecute(address executor) internal;
        function getOverhead() constant returns (uint);
        function getExtraGas() constant returns (uint);

        function sendSafe(address to_address, uint value) internal {
            CallLib.sendSafe(to_address, value);
        }

        function execute() public notcancelled {
            uint start_gas = msg.gas;

            // Check that the call should be executed now.
            if (!beforeExecute(msg.sender)) return;

            // Execute the call
            CallLib.execute(call, start_gas, msg.sender, getOverhead(), getExtraGas());

            // Any logic that needs to occur after the call has executed should
            // go in afterExecute
            afterExecute(msg.sender);
        }
}


contract FutureBlockCall is FutureCall {
        uint public targetBlock;
        uint8 public gracePeriod;

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
            if (call.wasCalled) {
                // Not being called within call window.
                CallLib.CallAborted(executor, "ALREADY_CALLED");
                return false;
            }

            if (block.number < targetBlock || block.number > targetBlock + gracePeriod) {
                // Not being called within call window.
                CallLib.CallAborted(executor, "NOT_IN_CALL_WINDOW");
                return false;
            }

            // If they are not authorized to execute the call at this time,
            // exit early.
            if (!CallLib.checkExecutionAuthorization(call, executor, block.number)) {
                CallLib.CallAborted(executor, "NOT_AUTHORIZED");
                return;
            }

            return true;
        }

        function afterExecute(address executor) internal {
            // Refund any leftover funds.
            CallLib.sendSafe(schedulerAddress, address(this).balance);
        }

        uint constant GAS_OVERHEAD = 100000;

        function getOverhead() constant returns (uint) {
                return GAS_OVERHEAD;
        }

        uint constant EXTRA_GAS = 73000;

        function getExtraGas() constant returns (uint) {
                return EXTRA_GAS;
        }

        uint constant CLAIM_GROWTH_WINDOW = 240;
        uint constant MAXIMUM_CLAIM_WINDOW = 15;
        uint constant BEFORE_CALL_FREEZE_WINDOW = 10;

        function cancel() public notcancelled {
            // Before the claim window
            if (block.number < targetBlock - BEFORE_CALL_FREEZE_WINDOW - MAXIMUM_CLAIM_WINDOW - CLAIM_GROWTH_WINDOW) {
                // already cancelled
                if (msg.sender != schedulerAddress) throw;
                CallLib.cancel(call, msg.sender);
                return;
            }
            if (block.number > targetBlock + gracePeriod) {
                // already called
                if (call.wasCalled) throw;
                CallLib.cancel(call, msg.sender);
                return;
            }
            throw;
        }
}
