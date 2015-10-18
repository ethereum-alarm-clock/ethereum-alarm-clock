import "libraries/GroveLib.sol"
import "libraries/ResourcePoolLib.sol"
import "libraries/AccountingLib.sol"


library ScheduledCallLib {
    struct CallDatabase {
        bytes32 lastCallKey;
        bytes lastData;
        uint lastDataLength;
        bytes32 lastDataHash;

        ResourcePoolLib.Pool callerPool;
        GroveLib.Index callIndex;

        AccountingLib.Bank gasBank;

        mapping (bytes32 => Call) calls;
        mapping (bytes32 => bytes) data_registry;

        mapping (bytes32 => bool) accountAuthorizations;
    }

    struct Call {
            address contractAddress;
            address scheduledBy;
            uint calledAtBlock;
            uint targetBlock;
            uint8 gracePeriod;
            uint nonce;
            uint baseGasPrice;
            uint gasPrice;
            uint gasUsed;
            uint gasCost;
            uint payout;
            uint fee;
            address executedBy;
            bytes4 abiSignature;
            bool isCancelled;
            bool wasCalled;
            bool wasSuccessful;
            bytes32 dataHash;
    }

    /*
     *  Getter methods for `Call` information
     */
    function getCallContractAddress(CallDatabase storage self, bytes32 callKey) constant returns (address) {
            return self.data_registry[callKey].contractAddress;
    }

    function getCallScheduledBy(CallDatabase storage self, bytes32 callKey) constant returns (address) {
            return self.data_registry[callKey].scheduledBy;
    }

    function getCallCalledAtBlock(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].calledAtBlock;
    }

    function getCallGracePeriod(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].gracePeriod;
    }

    function getCallTargetBlock(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].targetBlock;
    }

    function getCallBaseGasPrice(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].baseGasPrice;
    }

    function getCallGasPrice(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].gasPrice;
    }

    function getCallGasUsed(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].gasUsed;
    }

    function getCallABISignature(CallDatabase storage self, bytes32 callKey) constant returns (bytes4) {
            return self.data_registry[callKey].abiSignature;
    }

    function checkIfCalled(CallDatabase storage self, bytes32 callKey) constant returns (bool) {
            return self.data_registry[callKey].wasCalled;
    }

    function checkIfSuccess(CallDatabase storage self, bytes32 callKey) constant returns (bool) {
            return self.data_registry[callKey].wasSuccessful;
    }

    function checkIfCancelled(CallDatabase storage self, bytes32 callKey) constant returns (bool) {
            return self.data_registry[callKey].isCancelled;
    }

    function getCallDataHash(CallDatabase storage self, bytes32 callKey) constant returns (bytes32) {
            return self.data_registry[callKey].dataHash;
    }

    function getCallPayout(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].payout;
    }

    function getCallFee(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            return self.data_registry[callKey].fee;
    }

    /*
     *  Scheduling Authorization API
     */

    function addAuthorization(CallDatabase storage self, address schedulerAddress, address contractAddress) public {
            self.accountAuthorizations[sha3(schedulerAddress, contractAddress)] = true;
    }

    function removeAuthorization(CallDatabase storage self, address schedulerAddress, address contractAddress) public {
            self.accountAuthorizations[sha3(schedulerAddress, contractAddress)] = false;
    }

    function checkAuthorization(CallDatabase storage self, address schedulerAddress, address contractAddress) constant returns (bool) {
            return self.accountAuthorizations[sha3(schedulerAddress, contractAddress)];
    }

    /*
     *  Data Registry API
     */
    function getLastDataHash(CallDatabase storage self) constant returns (bytes32) {
            return lastDataHash;
    }

    function getLastDataLength(CallDatabase storage self) constant returns (uint) {
            return lastDataLength;
    }

    function getLastData(CallDatabase storage self) constant returns (bytes) {
            return lastData;
    }

    function getCallData(CallDatabase storage self, bytes32 callKey) constant returns (bytes) {
            return self.data_registry[self.data_registry[callKey].dataHash];
    }

    /*
     *  Data registration API
     */
    event DataRegistered(CallDatabase storage self, bytes32 indexed dataHash);

    function registerData(CallDatabase storage self, bytes data) public {
            lastData.length = data.length - 4;
            if (data.length > 4) {
                    for (uint i = 0; i < lastData.length; i++) {
                            lastData[i] = data[i + 4];
                    }
            }
            self.data_registry[sha3(lastData)] = lastData;
            lastDataHash = sha3(lastData);
            lastDataLength = lastData.length;
            lastData = lastData;
    }

    /*
     *  Call execution API
     */
    // This number represents the constant gas cost of the addition
    // operations that occur in `doCall` that cannot be tracked with
    // msg.gas.
    uint constant EXTRA_CALL_GAS = 151098;

    // This number represents the overall overhead involved in executing a
    // scheduled call.
    uint constant CALL_OVERHEAD = 144982;

    event CallExecuted(address indexed executedBy, bytes32 indexed callKey);
    event CallAborted(address indexed executedBy, bytes32 indexed callKey, bytes18 reason);

    function doCall(CallDatabase storage self, bytes32 callKey) public {
            uint gasBefore = msg.gas;

            var call = self.data_registry[callKey];

            if (call.wasCalled) {
                    // The call has already been executed so don't do it again.
                    CallAborted(msg.sender, callKey, "ALREADY CALLED");
                    return;
            }

            if (call.isCancelled) {
                    // The call was cancelled so don't execute it.
                    CallAborted(msg.sender, callKey, "CANCELLED");
                    return;
            }

            if (call.contractAddress == 0x0) {
                    // This call key doesnt map to a registered call.
                    CallAborted(msg.sender, callKey, "UNKNOWN");
                    return;
            }

            if (block.number < call.targetBlock) {
                    // Target block hasnt happened yet.
                    CallAborted(msg.sender, callKey, "TOO EARLY");
                    return;
            }

            if (block.number > call.targetBlock + call.gracePeriod) {
                    // The blockchain has advanced passed the period where
                    // it was allowed to be called.
                    CallAborted(msg.sender, callKey, "TOO LATE");
                    return;
            }

            uint heldBalance = getCallMaxCost(callKey);

            if (accountBalances[call.scheduledBy] < heldBalance) {
                    // The scheduledBy's account balance is less than the
                    // current gasLimit and thus potentiall can't pay for
                    // the call.

                    // Mark it as called since it was.
                    call.wasCalled = true;
                    
                    // Log it.
                    CallAborted(msg.sender, callKey, "INSUFFICIENT_FUNDS");
                    return;
            }

            // Check if this caller is allowed to execute the call.
            if (callerPool.getPoolSize(callerPool.getActivePoolKey()) > 0) {
                    address poolCaller = callerPool.getDesignatedCaller(callKey, call.targetBlock, call.gracePeriod, block.number);
                    if (poolCaller != 0x0 && poolCaller != msg.sender) {
                            // This call was reserved for someone from the
                            // bonded pool of callers and can only be
                            // called by them during this block window.
                            CallAborted(msg.sender, callKey, "WRONG_CALLER");
                            return;
                    }

                    uint blockWindow = (block.number - call.targetBlock) / 4;
                    if (blockWindow > 0) {
                            // Someone missed their call so this caller
                            // gets to claim their bond for picking up
                            // their slack.
                            callerPool.awardMissedBlockBonus(msg.sender, callKey, call.targetBlock, call.gracePeriod);
                    }
            }

            // Log metadata about the call.
            call.gasPrice = tx.gasprice;
            call.executedBy = msg.sender;
            call.calledAtBlock = block.number;

            // Fetch the call data
            var data = getCallData(callKey);

            // During the call, we need to put enough funds to pay for the
            // call on hold to ensure they are available to pay the caller.
            _deductFunds(call.scheduledBy, heldBalance);

            // Mark whether the function call was successful.
            if (checkAuthorization(call.scheduledBy, call.contractAddress)) {
                    call.wasSuccessful = authorizedRelay.relayCall.gas(msg.gas - CALL_OVERHEAD)(call.contractAddress, call.abiSignature, data);
            }
            else {
                    call.wasSuccessful = unauthorizedRelay.relayCall.gas(msg.gas - CALL_OVERHEAD)(call.contractAddress, call.abiSignature, data);
            }

            // Add the held funds back into the scheduler's account.
            _addFunds(call.scheduledBy, heldBalance);

            // Mark the call as having been executed.
            call.wasCalled = true;

            // Log the call execution.
            CallExecuted(msg.sender, callKey);

            // Compute the scalar (0 - 200) for the fee.
            uint feeScalar = getCallFeeScalar(call.baseGasPrice, call.gasPrice);

            // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
            // amount that represents the gas usage of the commands that
            // happen after this line.
            call.gasUsed = (gasBefore - msg.gas + EXTRA_CALL_GAS);
            call.gasCost = call.gasUsed * call.gasPrice;

            // Now we need to pay the caller as well as keep fee.
            // callerPayout -> call cost + 1%
            // fee -> 1% of callerPayout
            call.payout = call.gasCost * feeScalar * 101 / 10000;
            call.fee = call.gasCost * feeScalar / 10000;

            AccountingLib._deductFunds(self.gasBank, call.scheduledBy, call.payout + call.fee);

            AccountingLib._addFunds(self.gasBank, msg.sender, call.payout);
            AccountingLib._addFunds(self.gasBank, owner, call.fee);
    }

    function getCallMaxCost(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            /*
             *  tx.gasprice * block.gaslimit
             *  
             */
            // call cost + 2%
            var call = self.data_registry[callKey];

            uint gasCost = tx.gasprice * block.gaslimit;
            uint feeScalar = getCallFeeScalar(call.baseGasPrice, tx.gasprice);

            return gasCost * feeScalar * 102 / 10000;
    }

    function getCallFeeScalar(uint baseGasPrice, uint gasPrice) constant returns (uint) {
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

    /*
     *  Call Scheduling API
     */

    // The result of `sha()` so that we can validate that people aren't
    // looking up call data that failed to register.
    bytes32 constant emptyDataHash = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;

    function getCallKey(address scheduledBy, address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) constant returns (bytes32) {
            return sha3(scheduledBy, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);
    }

    // Ten minutes into the future.
    uint constant MAX_BLOCKS_IN_FUTURE = 40;

    event CallScheduled(bytes32 indexed callKey);
    event CallRejected(bytes32 indexed callKey, bytes15 reason);

    function scheduleCall(CallDatabase storage self, address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public returns (bytes15) {
            /*
             * Primary API for scheduling a call.  Prior to calling this
             * the data should already have been registered through the
             * `registerData` API.
             */
            bytes32 callKey = getCallKey(msg.sender, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);

            if (dataHash != emptyDataHash && self.data_registry[dataHash].length == 0) {
                    // Don't allow registering calls if the data hash has
                    // not actually been registered.  The only exception is
                    // the *emptyDataHash*.
                    return "NO_DATA";
            }

            if (targetBlock < block.number + MAX_BLOCKS_IN_FUTURE) {
                    // Don't allow scheduling further than
                    // MAX_BLOCKS_IN_FUTURE
                    return "TOO_SOON";
            }
            var call = self.data_registry[callKey];

            if (call.contractAddress != 0x0) {
                    return "DUPLICATE";
            }

            if (gracePeriod < 16) {
                    return "GRACE_TOO_SHORT";
            }

            self.lastCallKey = callKey;

            call.contractAddress = contractAddress;
            call.scheduledBy = msg.sender;
            call.nonce = nonce;
            call.abiSignature = abiSignature;
            call.dataHash = dataHash;
            call.targetBlock = targetBlock;
            call.gracePeriod = gracePeriod;
            call.baseGasPrice = tx.gasprice;

            // Put the call into the grove index.
            GroveLib.insert(self.callIndex, self.lastCallKey, int(call.targetBlock));

            return 0x0;
    }

    event CallCancelled(bytes32 indexed callKey);

    // Two minutes
    uint constant MIN_CANCEL_WINDOW = 8;

    function cancelCall(CallDatabase storage self, bytes32 callKey) public returns (bool) {
            var call = self.data_registry[callKey];
            if (call.scheduledBy != msg.sender) {
                    // Nobody but the scheduler can cancel a call.
                    return false;
            }
            if (call.wasCalled) {
                    // No need to cancel a call that already was executed.
                    return false;
            }
            if (call.targetBlock - MIN_CANCEL_WINDOW <= block.number) {
                    // Call cannot be cancelled this close to execution.
                    return false;
            }
            call.isCancelled = true;
            return true;
    }
}
