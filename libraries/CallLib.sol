import "libraries/AccountingLib.sol";


library CallLib {
    /*
     *  Address: 0x8deb276d0abe47132849555a3449f26bd1872baa
     */
    struct Call {
        address contractAddress;
        bytes4 abiSignature;
        bytes callData;
        uint callValue;
        uint anchorGasPrice;
        uint requiredGas;
        uint16 requiredStackDepth;

        address claimer;
        uint claimAmount;
        uint claimerDeposit;

        bool wasSuccessful;
        bool wasCalled;
        bool isCancelled;
    }

    enum State {
        Pending,
        Unclaimed,
        Claimed,
        Frozen,
        Callable,
        Executed,
        Cancelled,
        Missed
    }

    function state(Call storage self) constant returns (State) {
        if (self.isCancelled) return State.Cancelled;
        if (self.wasCalled) return State.Executed;

        var call = FutureBlockCall(this);

        if (block.number + CLAIM_GROWTH_WINDOW + MAXIMUM_CLAIM_WINDOW + BEFORE_CALL_FREEZE_WINDOW < call.targetBlock()) return State.Pending;
        if (block.number + BEFORE_CALL_FREEZE_WINDOW < call.targetBlock()) {
            if (self.claimer == 0x0) {
                return State.Unclaimed;
            }
            else {
                return State.Claimed;
            }
        }
        if (block.number < call.targetBlock()) return State.Frozen;
        if (block.number < call.targetBlock() + call.gracePeriod()) return State.Callable;
        return State.Missed;
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

    uint constant GAS_PER_DEPTH = 700;

    function checkDepth(uint n) constant returns (bool) {
        if (n == 0) return true;
        return address(this).call.gas(GAS_PER_DEPTH * n)(bytes4(sha3("__dig(uint256)")), n - 1);
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
        *  Return a number between 0 - 200 to scale the donation based on the
        *  gas price set for the calling transaction as compared to the gas
        *  price of the scheduling transaction.
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

    event CallExecuted(address indexed executor, uint gasCost, uint payment, uint donation, bool success);

    bytes4 constant EMPTY_SIGNATURE = 0x0000;

    event CallAborted(address executor, bytes32 reason);

    function execute(Call storage self,
                     uint start_gas,
                     address executor,
                     uint overhead,
                     uint extraGas) public {
        FutureCall call = FutureCall(this);
        
        // Mark the call has having been executed.
        self.wasCalled = true;

        // Make the call
        if (self.abiSignature == EMPTY_SIGNATURE && self.callData.length == 0) {
            self.wasSuccessful = self.contractAddress.call.value(self.callValue).gas(msg.gas - overhead)();
        }
        else if (self.abiSignature == EMPTY_SIGNATURE) {
            self.wasSuccessful = self.contractAddress.call.value(self.callValue).gas(msg.gas - overhead)(self.callData);
        }
        else if (self.callData.length == 0) {
            self.wasSuccessful = self.contractAddress.call.value(self.callValue).gas(msg.gas - overhead)(self.abiSignature);
        }
        else {
            self.wasSuccessful = self.contractAddress.call.value(self.callValue).gas(msg.gas - overhead)(self.abiSignature, self.callData);
        }

        call.origin().call(bytes4(sha3("updateDefaultPayment()")));

        // Compute the scalar (0 - 200) for the donation.
        uint gasScalar = getGasScalar(self.anchorGasPrice, tx.gasprice);

        uint basePayment;
        if (self.claimer == executor) {
            basePayment = self.claimAmount;
        }
        else {
            basePayment = call.basePayment();
        }
        uint payment = self.claimerDeposit + basePayment * gasScalar / 100; 
        uint donation = call.baseDonation() * gasScalar / 100;

        // zero out the deposit
        self.claimerDeposit = 0;

        // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
        // amount that represents the gas usage of the commands that
        // happen after this line.
        uint gasCost = tx.gasprice * (start_gas - msg.gas + extraGas);

        // Now we need to pay the executor as well as keep donation.
        payment = sendSafe(executor, payment + gasCost);
        donation = sendSafe(creator, donation);

        // Log execution
        CallExecuted(executor, gasCost, payment, donation, self.wasSuccessful);
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

        uint cutoff = call.targetBlock() - BEFORE_CALL_FREEZE_WINDOW;
        
        // claim window has closed
        if (block_number > cutoff) return call.basePayment();

        cutoff -= MAXIMUM_CLAIM_WINDOW;

        // in the maximum claim window.
        if (block_number > cutoff) return call.basePayment();

        cutoff -= CLAIM_GROWTH_WINDOW;

        if (block_number > cutoff) {
            uint x = block_number - cutoff;

            return call.basePayment() * x / CLAIM_GROWTH_WINDOW;
        }

        return 0;
    }

    function lastClaimBlock() constant returns (uint) {
        var call = FutureBlockCall(this);
        return call.targetBlock() - BEFORE_CALL_FREEZE_WINDOW;
    }

    function maxClaimBlock() constant returns (uint) {
        return lastClaimBlock() - MAXIMUM_CLAIM_WINDOW;
    }

    function firstClaimBlock() constant returns (uint) {
        return maxClaimBlock() - CLAIM_GROWTH_WINDOW;
    }

    function claim(Call storage self, address executor, uint deposit_amount, uint basePayment) public returns (bool) {
        /*
         *  Warning! this does not check whether the function is already
         *  claimed or whether we are within the claim window.  This must be
         *  done at the contract level.
         */
        // Insufficient Deposit
        if (deposit_amount < 2 * basePayment) return false;

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

    function isCancellable(Call storage self, address caller) returns (bool) {
        var _state = state(self);
        var call = FutureBlockCall(this);

        if (_state == State.Pending && caller == call.schedulerAddress()) {
            return true;
        }

        if (_state == State.Missed) return true;

        return false;
    }

    function beforeExecuteForFutureBlockCall(Call storage self, address executor) returns (bool) {
        bytes32 reason;

        var call = FutureBlockCall(this);

        if (msg.gas < self.requiredGas) {
            // The executor has not provided sufficient gas
            reason = "NOT_ENOUGH_GAS";
        }
        else if (self.wasCalled) {
            // Not being called within call window.
            reason = "ALREADY_CALLED";
        }
        else if (block.number < call.targetBlock() || block.number > call.targetBlock() + call.gracePeriod()) {
            // Not being called within call window.
            reason = "NOT_IN_CALL_WINDOW";
        }
        else if (!checkExecutionAuthorization(self, executor, block.number)) {
            // Someone has claimed this call and they currently have exclusive
            // rights to execute it.
            reason = "NOT_AUTHORIZED";
        }
        else if (self.requiredStackDepth > 0 && executor != tx.origin && !checkDepth(self.requiredStackDepth)) {
            reason = "STACK_TOO_DEEP";
        }

        if (reason != 0x0) {
            CallAborted(executor, reason);
            return false;
        }

        return true;
    }
}


contract FutureCall {
    // The author (Piper Merriam) address.
    address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

    address public schedulerAddress;

    uint public basePayment;
    uint public baseDonation;

    CallLib.Call call;

    address public origin;

    function FutureCall(address _schedulerAddress,
                        uint _requiredGas,
                        uint16 _requiredStackDepth,
                        address _contractAddress,
                        bytes4 _abiSignature,
                        bytes _callData,
                        uint _callValue,
                        uint _basePayment,
                        uint _baseDonation)
    {
        origin = msg.sender;
        schedulerAddress = _schedulerAddress;

        basePayment = _basePayment;
        baseDonation = _baseDonation;

        call.requiredGas = _requiredGas;
        call.requiredStackDepth = _requiredStackDepth;
        call.anchorGasPrice = tx.gasprice;
        call.contractAddress = _contractAddress;
        call.abiSignature = _abiSignature;
        call.callData = _callData;
        call.callValue = _callValue;
    }

    enum State {
        Pending,
        Unclaimed,
        Claimed,
        Frozen,
        Callable,
        Executed,
        Cancelled,
        Missed
    }

    modifier in_state(State _state) { if (state() == _state) _ }

    function state() constant returns (State) {
        return State(CallLib.state(call));
    }

    /*
     *  API for FutureXXXXCalls to implement.
     */
    function beforeExecute(address executor) public returns (bool);
    function afterExecute(address executor) internal;
    function getOverhead() constant returns (uint);
    function getExtraGas() constant returns (uint);

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

    function callValue() constant returns (uint) {
        return call.callValue;
    }

    function anchorGasPrice() constant returns (uint) {
        return call.anchorGasPrice;
    }

    function requiredGas() constant returns (uint) {
        return call.requiredGas;
    }

    function requiredStackDepth() constant returns (uint16) {
        return call.requiredStackDepth;
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

    /*
     *  Claim API helpers
     */
    function getClaimAmountForBlock() constant returns (uint) {
        return CallLib.getClaimAmountForBlock(block.number);
    }

    function getClaimAmountForBlock(uint block_number) constant returns (uint) {
        return CallLib.getClaimAmountForBlock(block_number);
    }

    /*
     *  Call Data registration
     */
    function () returns (bool) {
        /*
         * Fallback to allow sending funds to this contract.
         * (also allows registering raw call data)
         */
        // only scheduler can register call data.
        if (msg.sender != schedulerAddress) return false;
        // cannot write over call data
        if (call.callData.length > 0) return false;

        var _state = state();
        if (_state != State.Pending && _state != State.Unclaimed && _state != State.Claimed) return false;

        call.callData = msg.data;
        return true;
    }

    function registerData() public returns (bool) {
        // only scheduler can register call data.
        if (msg.sender != schedulerAddress) return false;
        // cannot write over call data
        if (call.callData.length > 0) return false;

        var _state = state();
        if (_state != State.Pending && _state != State.Unclaimed && _state != State.Claimed) return false;

        CallLib.extractCallData(call, msg.data);
    }

    function firstClaimBlock() constant returns (uint) {
        return CallLib.firstClaimBlock();
    }

    function maxClaimBlock() constant returns (uint) {
        return CallLib.maxClaimBlock();
    }

    function lastClaimBlock() constant returns (uint) {
        return CallLib.lastClaimBlock();
    }

    function claim() public in_state(State.Unclaimed) returns (bool) {
        bool success = CallLib.claim(call, msg.sender, msg.value, basePayment);
        if (!success) {
            if (!AccountingLib.sendRobust(msg.sender, msg.value)) throw;
        }
        return success;
    }

    function checkExecutionAuthorization(address executor, uint block_number) constant returns (bool) {
        return CallLib.checkExecutionAuthorization(call, executor, block_number);
    }

    function sendSafe(address to_address, uint value) internal {
        CallLib.sendSafe(to_address, value);
    }

    function execute() public in_state(State.Callable) {
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

    uint constant CALL_API_VERSION = 2;

    function callAPIVersion() constant returns (uint) {
        return CALL_API_VERSION;
    }

    function FutureBlockCall(address _schedulerAddress,
                             uint _targetBlock,
                             uint8 _gracePeriod,
                             address _contractAddress,
                             bytes4 _abiSignature,
                             bytes _callData,
                             uint _callValue,
                             uint _requiredGas,
                             uint16 _requiredStackDepth,
                             uint _basePayment,
                             uint _baseDonation)
        FutureCall(_schedulerAddress, _requiredGas, _requiredStackDepth, _contractAddress, _abiSignature, _callData, _callValue, _basePayment, _baseDonation)
    {
        // parent contract FutureCall
        schedulerAddress = _schedulerAddress;

        targetBlock = _targetBlock;
        gracePeriod = _gracePeriod;
    }

    uint constant GAS_PER_DEPTH = 700;

    function __dig(uint n) constant returns (bool) {
        if (n == 0) return true;
        if (!address(this).callcode(bytes4(sha3("__dig(uint256)")), n - 1)) throw;
    }


    function beforeExecute(address executor) public returns (bool) {
        return CallLib.beforeExecuteForFutureBlockCall(call, executor);
    }

    function afterExecute(address executor) internal {
        // Refund any leftover funds.
        CallLib.sendSafe(schedulerAddress, address(this).balance);
    }

    uint constant GAS_OVERHEAD = 100000;

    function getOverhead() constant returns (uint) {
            return GAS_OVERHEAD;
    }

    uint constant EXTRA_GAS = 77000;

    function getExtraGas() constant returns (uint) {
            return EXTRA_GAS;
    }

    uint constant CLAIM_GROWTH_WINDOW = 240;
    uint constant MAXIMUM_CLAIM_WINDOW = 15;
    uint constant BEFORE_CALL_FREEZE_WINDOW = 10;

    function isCancellable() constant public returns (bool) {
        return CallLib.isCancellable(call, msg.sender);
    }

    function cancel() public {
        if (CallLib.isCancellable(call, msg.sender)) {
            CallLib.cancel(call, msg.sender);
        }
    }
}
