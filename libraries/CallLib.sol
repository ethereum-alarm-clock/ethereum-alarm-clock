import "libraries/GroveLib.sol";


library CallLib {
        /*
         *  Address: 0x2746bcf29bffafcc7906752f639819171d18ce2b
         */
        struct Call {
                address contract_address;
                bytes4 abi_signature;
                bytes call_data;
                uint anchor_gas_price;
                uint suggested_gas;

                address bidder;
                uint bid_amount;
                uint bidder_deposit;

                bool was_successful;
                bool was_called;
                bool is_cancelled;
        }

        // The number of blocks that each caller in the pool has to complete their
        // call.
        uint constant CALL_WINDOW_SIZE = 16;

        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function extract_call_data(Call storage call, bytes data) public {
            call.call_data.length = data.length - 4;
            if (data.length > 4) {
                    for (uint i = 0; i < call.call_data.length; i++) {
                            call.call_data[i] = data[i + 4];
                    }
            }
        }

        function send_safe(address to_address, uint value) public returns (uint) {
                if (value > address(this).balance) {
                        value = address(this).balance;
                }
                if (value > 0) {
                        AccountingLib.sendRobust(to_address, value);
                        return value;
                }
                return 0;
        }

        function get_gas_scalar(uint base_gas_price, uint gas_price) constant returns (uint) {
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

        event CallExecuted(address indexed executor, uint gas_cost, uint payment, uint fee, bool success);

        event _CallAborted(address executor, bytes32 reason);
        function CallAborted(address executor, bytes32 reason) public {
            _CallAborted(executor, reason);
        }

        function execute(Call storage self, uint start_gas, address executor, uint overhead, uint extraGas) public {
            FutureCall call = FutureCall(this);

            // If the pre-execution checks do not pass, exit early.
            if (!call.before_execute(executor)) {
                return;
            }
            
            // Make the call
            self.was_successful = self.contract_address.call.gas(msg.gas - overhead)(self.abi_signature, self.call_data);
            self.was_called = true;

            // Compute the scalar (0 - 200) for the fee.
            uint gas_scalar = get_gas_scalar(self.anchor_gas_price, tx.gasprice);

            uint base_payment;
            if (self.bidder == 0x0) {
                base_payment = call.base_payment();
            }
            else {
                base_payment = self.bid_amount;
            }
            uint payment = self.bidder_deposit + base_payment * gas_scalar / 100; 
            uint fee = call.base_fee() * gas_scalar / 100;

            // zero out the deposit
            self.bidder_deposit = 0;

            // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
            // amount that represents the gas usage of the commands that
            // happen after this line.
            uint gas_cost = tx.gasprice * (start_gas - msg.gas + extraGas);

            // Now we need to pay the executor as well as keep fee.
            payment = send_safe(executor, payment + gas_cost);
            fee = send_safe(creator, fee);

            // Log execution
            CallExecuted(executor, gas_cost, payment, fee, self.was_successful);
        }

        event Cancelled(address indexed cancelled_by);

        function cancel(Call storage self, address sender) public {
                Cancelled(sender);
                if (self.bidder_deposit >= 0) {
                    send_safe(self.bidder, self.bidder_deposit);
                }
                var call = FutureCall(this);
                send_safe(call.scheduler_address(), address(this).balance);
                self.is_cancelled = true;
        }

        /*
         *  Bid API
         *  - Gas costs for this transaction are not covered so it
         *    must be up to the call executors to ensure that their actions
         *    remain profitable.  Any form of bidding war is likely to eat into
         *    profits.
         */
        event Claimed(address executor, uint bid_amount);

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
            /*
             *   [--growth-window--][--max-window--][--freeze-window--]
             *
             *
             */
            var call = FutureBlockCall(this);

            uint last_block = call.target_block() - BEFORE_CALL_FREEZE_WINDOW;
            
            // bid window has closed
            if (block_number > last_block) return call.base_payment();

            uint first_block = last_block - MAXIMUM_BID_WINDOW - BID_GROWTH_WINDOW;
            
            // bid window has not begun
            if (block_number < first_block) return 0;

            // in the maximum bid window.
            if (block_number > last_block - MAXIMUM_BID_WINDOW) return call.base_payment();

            uint x = block_number - first_block;

            return call.base_payment() * x / BID_GROWTH_WINDOW;
        }

        function claim(Call storage self, address executor, uint deposit_amount, uint base_payment) public returns (bool) {
                // Already claimed
                if (self.bidder != 0x0) return false;

                // Insufficient Deposit
                if (deposit_amount < 2 * base_payment) return false;

                var call = FutureCall(this);

                // Too early
                if (block.number < call.target_block() - BEFORE_CALL_FREEZE_WINDOW - MAXIMUM_BID_WINDOW - BID_GROWTH_WINDOW) return false;

                // Too late
                if (block.number > call.target_block() - BEFORE_CALL_FREEZE_WINDOW) return false;
                self.bid_amount = get_bid_amount_for_block(block.number);
                self.bidder = executor;
                self.bidder_deposit = deposit_amount;

                // Log the bid.
                Claimed(executor, self.bid_amount);
        }

        function check_execution_authorization(Call storage self, address executor, uint block_number) returns (bool) {
                /*
                 *  Check whether the given `executor` is authorized.
                 */
                var call = FutureCall(this);

                uint target_block = call.target_block();

                // Invalid, not in call window.
                if (block_number < target_block || block_number > target_block + call.grace_period()) throw;

                // Within the reserved call window so if there is a bidder, the
                // executor must be the biddor.
                if (block_number - target_block < CALL_WINDOW_SIZE) {
                    return (self.bidder == 0x0 || self.bidder == executor);
                }

                // Must be in the free-for-all period.
                return true;
        }
}


contract FutureCall {
        address public scheduler_address;

        uint public base_payment;
        uint public base_fee;

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
        function contract_address() constant returns (address) {
            return call.contract_address;
        }

        function abi_signature() constant returns (bytes4) {
            return call.abi_signature;
        }

        function call_data() constant returns (bytes) {
            return call.call_data;
        }

        function anchor_gas_price() constant returns (uint) {
            return call.anchor_gas_price;
        }

        function suggested_gas() constant returns (uint) {
            return call.suggested_gas;
        }

        function bidder() constant returns (address) {
            return call.bidder;
        }

        function bid_amount() constant returns (uint) {
            return call.bid_amount;
        }

        function bidder_deposit() constant returns (uint) {
            return call.bidder_deposit;
        }

        function was_successful() constant returns (bool) {
            return call.was_successful;
        }

        function was_called() constant returns (bool) {
            return call.was_called;
        }

        function is_cancelled() constant returns (bool) {
            return call.is_cancelled;
        }

        function get_bid_amount_for_block() constant returns (uint) {
            return CallLib.get_bid_amount_for_block(block.number);
        }

        function get_bid_amount_for_block(uint block_number) constant returns (uint) {
            return CallLib.get_bid_amount_for_block(block_number);
        }

        function () {
                // Fallback to allow sending funds to this contract.
                // Also allows call data registration.
                if (msg.sender == scheduler_address && msg.data.length > 0) {
                        if (call.call_data.length != 0) {
                            throw;
                        }
                        call.call_data = msg.data;
                }
        }

        modifier notcancelled { if (call.is_cancelled) throw; _ }

        modifier onlyscheduler { if (msg.sender == scheduler_address) _ }

        // The author (Piper Merriam) address.
        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function register_data() public onlyscheduler {
            if (call.call_data.length > 0) {
                // cannot write over call data
                throw;
            }
            CallLib.extract_call_data(call, msg.data);
        }

        function claim() public notcancelled returns (bool) {
            bool success = CallLib.claim(call, msg.sender, msg.value, base_payment);
            if (!success) {
                if (!AccountingLib.sendRobust(msg.sender, msg.value)) throw;
            }
            return success;
        }

        function check_execution_authorization(address executor, uint block_number) constant returns (bool) {
            return CallLib.check_execution_authorization(call, executor, block_number);
        }

        // API for inherited contracts
        function before_execute(address executor) public returns (bool);
        function after_execute(address executor) internal;
        function get_overhead() constant returns (uint);
        function get_extra_gas() constant returns (uint);

        function send_safe(address to_address, uint value) internal {
            CallLib.send_safe(to_address, value);
        }

        function execute() public notcancelled {
            uint start_gas = msg.gas;

            // Check that the call should be executed now.
            if (!before_execute(msg.sender)) return;

            // Execute the call
            CallLib.execute(call, start_gas, msg.sender, get_overhead(), get_extra_gas());

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

        function FutureBlockCall(address _scheduler_address, uint _target_block, uint8 _grace_period, address _contract_address, bytes4 _abi_signature, uint _suggested_gas, uint _base_payment, uint _base_fee) {
                // TODO: split this constructor across this contract and the
                // parent contract FutureCall
                scheduler_address = _scheduler_address;

                target_block = _target_block;
                grace_period = _grace_period;


                base_payment = _base_payment;
                base_fee = _base_fee;

                call.suggested_gas = _suggested_gas;
                call.anchor_gas_price = tx.gasprice;
                call.contract_address = _contract_address;
                call.abi_signature = _abi_signature;
        }

        function before_execute(address executor) public returns (bool) {
            if (block.number < target_block || block.number > target_block + grace_period) {
                // Not being called within call window.
                CallLib.CallAborted(executor, "NOT_IN_CALL_WINDOW");
                return false;
            }

            // If they are not authorized to execute the call at this time,
            // exit early.
            if (!CallLib.check_execution_authorization(call, executor, block.number)) {
                CallLib.CallAborted(executor, "NOT_AUTHORIZED");
                return;
            }

            return true;
        }

        function after_execute(address executor) internal {
            // Refund any leftover funds.
            CallLib.send_safe(scheduler_address, address(this).balance);
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

        function cancel() public onlyscheduler notcancelled {
                if ((block.number < target_block - BEFORE_CALL_FREEZE_WINDOW || block.number > target_block + grace_period) && !call.was_called) {
                        CallLib.cancel(call, scheduler_address);
                }
        }
}
