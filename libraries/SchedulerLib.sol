import "libraries/GroveLib.sol";
import "libraries/ResourcePoolLib.sol";
import "libraries/AccountingLib.sol";


contract Relay {
        address operator;

        function Relay() {
                operator = msg.sender;
        }

        function relayCall(address contractAddress, bytes4 abiSignature, bytes data) public returns (bool) {
                if (msg.sender != operator) {
                        throw;
                }
                return contractAddress.call(abiSignature, data);
        }
}


library SchedulerLib {
    /*
     *  Address: 0x5c3623dcef2d5168dbe3e8cc538788cd8912d898
     */
    struct CallDatabase {
        Relay unauthorizedRelay;
        Relay authorizedRelay;

        bytes32 lastCallKey;

        ResourcePoolLib.Pool callerPool;
        GroveLib.Index callIndex;

        AccountingLib.Bank gasBank;

        mapping (bytes32 => address) calls;

        mapping (bytes32 => bool) accountAuthorizations;
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
     *  API used by Alarm service
     */
    // The number of blocks that each caller in the pool has to complete their
    // call.
    uint constant CALL_WINDOW_SIZE = 16;

    function getGenerationIdForCall(CallDatabase storage self, bytes32 callKey) constant returns (uint) {
            FutureBlockCall call = FutureBlockCall(self.calls[callKey]);
            return ResourcePoolLib.getGenerationForWindow(self.callerPool, call.targetBlock(), call.targetBlock() + call.gracePeriod());
    }

    function getDesignatedCaller(CallDatabase storage self, bytes32 callKey, uint blockNumber) constant returns (address) {
            /*
             *  Returns the caller from the current call pool who is
             *  designated as the executor of this call.
             */
            FutureBlockCall call = FutureBlockCall(self.calls[callKey]);
            if (blockNumber < call.targetBlock() || blockNumber > call.targetBlock() + call.gracePeriod()) {
                    // blockNumber not within call window.
                    return 0x0;
            }

            // Check if we are in free-for-all window.
            uint numWindows = call.gracePeriod() / CALL_WINDOW_SIZE;
            uint blockWindow = (blockNumber - call.targetBlock()) / CALL_WINDOW_SIZE;

            if (blockWindow + 2 > numWindows) {
                    // We are within the free-for-all period.
                    return 0x0;
            }

            // Lookup the pool that full contains the call window for this
            // call.
            uint generationId = ResourcePoolLib.getGenerationForWindow(self.callerPool, call.targetBlock(), call.targetBlock() + call.gracePeriod());
            if (generationId == 0) {
                    // No pool currently in operation.
                    return 0x0;
            }
            var generation = self.callerPool.generations[generationId];

            uint offset = uint(address(call)) % generation.members.length;
            return generation.members[(offset + blockWindow) % generation.members.length];
    }

    event _AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed generationId, bytes32 callKey, uint blockNumber, uint bonusAmount);
    function AwardedMissedBlockBonus(address fromCaller, address toCaller, uint generationId, bytes32 callKey, uint blockNumber, uint bonusAmount) public {
        _AwardedMissedBlockBonus(fromCaller, toCaller, generationId, callKey, blockNumber, bonusAmount);
    }

    function getMinimumBond() constant returns (uint) {
            return tx.gasprice * block.gaslimit;
    }

    function doBondBonusTransfer(CallDatabase storage self, address fromCaller, address toCaller) internal returns (uint) {
            uint bonusAmount = getMinimumBond();
            uint bondBalance = self.callerPool.bonds[fromCaller];

            // If the bond balance is lower than the award
            // balance, then adjust the reward amount to
            // match the bond balance.
            if (bonusAmount > bondBalance) {
                    bonusAmount = bondBalance;
            }

            // Transfer the funds fromCaller => toCaller
            ResourcePoolLib.deductFromBond(self.callerPool, fromCaller, bonusAmount);
            ResourcePoolLib.addToBond(self.callerPool, toCaller, bonusAmount);

            return bonusAmount;
    }

    function awardMissedBlockBonus(CallDatabase storage self, address toCaller, bytes32 callKey) public {
            var call = self.calls[callKey];

            var generation = self.callerPool.generations[ResourcePoolLib.getGenerationForWindow(self.callerPool, call.targetBlock, call.targetBlock + call.gracePeriod)];
            uint i;
            uint bonusAmount;
            address fromCaller;

            uint numWindows = call.gracePeriod / CALL_WINDOW_SIZE;
            uint blockWindow = (block.number - call.targetBlock) / CALL_WINDOW_SIZE;

            // Check if we are within the free-for-all period.  If so, we
            // award from all pool members.
            if (blockWindow + 2 > numWindows) {
                    address firstCaller = getDesignatedCaller(self, callKey, call.targetBlock);
                    for (i = call.targetBlock; i <= call.targetBlock + call.gracePeriod; i += CALL_WINDOW_SIZE) {
                            fromCaller = getDesignatedCaller(self, callKey, i);
                            if (fromCaller == firstCaller && i != call.targetBlock) {
                                    // We have already gone through all of
                                    // the pool callers so we should break
                                    // out of the loop.
                                    break;
                            }
                            if (fromCaller == toCaller) {
                                    continue;
                            }
                            bonusAmount = doBondBonusTransfer(self, fromCaller, toCaller);

                            // Log the bonus was awarded.
                            AwardedMissedBlockBonus(fromCaller, toCaller, generation.id, callKey, block.number, bonusAmount);
                    }
                    return;
            }

            // Special case for single member and empty pools
            if (generation.members.length < 2) {
                    return;
            }

            // Otherwise the award comes from the previous caller.
            for (i = 0; i < generation.members.length; i++) {
                    // Find where the member is in the pool and
                    // award from the previous pool members bond.
                    if (generation.members[i] == toCaller) {
                            fromCaller = generation.members[(i + generation.members.length - 1) % generation.members.length];

                            bonusAmount = doBondBonusTransfer(self, fromCaller, toCaller);

                            // Log the bonus was awarded.
                            AwardedMissedBlockBonus(fromCaller, toCaller, generation.id, callKey, block.number, bonusAmount);

                            // Remove the caller from the next pool.
                            if (ResourcePoolLib.getNextGenerationId(self.callerPool) == 0) {
                                    // This is the first address to modify the
                                    // current pool so we need to setup the next
                                    // pool.
                                    ResourcePoolLib.createNextGeneration(self.callerPool);
                            }
                            ResourcePoolLib.removeFromGeneration(self.callerPool, ResourcePoolLib.getNextGenerationId(self.callerPool), fromCaller);
                            return;
                    }
            }
    }

    /*
     *  Call Scheduling API
     */
    function computeCallKey(address scheduledBy, address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) constant returns (bytes32) {
            return sha3(scheduledBy, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);
    }

    // Ten minutes into the future.
    uint constant MAX_BLOCKS_IN_FUTURE = 40;

    event _CallScheduled(address indexed callAddress);
    function CallScheduled(address callAddress) public {
        _CallScheduled(callAddress);
    }
    event _CallRejected(address indexed callAddress, bytes15 reason);
    function CallRejected(address callAddress, bytes15 reason) public {
        _CallRejected(callAddress, reason);
    }

    function getCallWindowSize() public returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function getMinimumGracePeriod() public returns (uint) {
        return 4 * CALL_WINDOW_SIZE;
    }

    function scheduleCall(CallDatabase storage self, address schedulerAddress, address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint suggestedGas, uint basePayment, uint baseFee) public returns (bytes15) {
            /*
             * Primary API for scheduling a call.  Prior to calling this
             * the data should already have been registered through the
             * `registerData` API.
             */
            if (targetBlock < block.number + MAX_BLOCKS_IN_FUTURE) {
                    // Don't allow scheduling further than
                    // MAX_BLOCKS_IN_FUTURE
                    return "TOO_SOON";
            }

            if (gracePeriod < getMinimumGracePeriod()) {
                    return "GRACE_TOO_SHORT";
            }

            FutureBlockCall call = new FutureBlockCall(address(this), schedulerAddress, targetBlock, gracePeriod, contractAddress, abiSignature, suggestedGas, basePayment, baseFee);

            // Put the call into the grove index.
            GroveLib.insert(self.callIndex, bytes32(address(call)), int(call.targetBlock));

            return 0x0;
    }
}

