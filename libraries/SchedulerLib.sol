import "libraries/GroveLib.sol";
import "libraries/ResourcePoolLib.sol";
import "libraries/AccountingLib.sol";
import "libraries/CallLib.sol";


library SchedulerLib {
    /*
     *  Address: 0x873bf63c898791e57fa66e7b9261ea81df0b8044
     */
    struct CallDatabase {
        ResourcePoolLib.Pool callerPool;
        GroveLib.Index callIndex;

        AccountingLib.Bank gasBank;
    }

    // The number of blocks that each caller in the pool has to complete their
    // call.
    uint constant CALL_WINDOW_SIZE = 16;

    function getGenerationIdForCall(CallDatabase storage self, address callAddress) constant returns (uint) {
            FutureBlockCall call = FutureBlockCall(callAddress);
            return ResourcePoolLib.getGenerationForWindow(self.callerPool, call.targetBlock(), call.targetBlock() + call.gracePeriod());
    }

    function getDesignatedCaller(CallDatabase storage self, uint leftBound, uint rightBound, uint blockNumber) constant returns (bool, address) {
            /*
             *  Returns the caller from the current call pool who is
             *  designated as the executor of this call.
             */
            if (leftBound > rightBound || blockNumber < leftBound ||  blockNumber > rightBound) {
                    // Invalid call parameters.  blockNumber has to be
                    // contained in the call window and the call window has to
                    // be valid.
                    throw;
            }


            // Lookup the pool that full contains the call window for this
            // call.
            uint generationId = ResourcePoolLib.getGenerationForWindow(self.callerPool, leftBound, rightBound);
            if (generationId == 0) {
                    // No pool currently in operation.
                    return (false, 0x0);
            }

            var generation = self.callerPool.generations[generationId];
            if (generation.members.length == 0) {
                    // Current pool is empty
                    return (false, 0x0);
            }

            // Check if we are in free-for-all window.
            uint numWindows = (rightBound - leftBound) / CALL_WINDOW_SIZE;
            uint blockWindow = (blockNumber - leftBound) / CALL_WINDOW_SIZE;

            if (blockWindow + 2 > numWindows) {
                    // We are within the free-for-all period.
                    return (true, 0x0);
            }

            uint offset = uint(sha3(leftBound, rightBound, generationId, generation.members)) % generation.members.length;
            return (true, generation.members[(offset + blockWindow) % generation.members.length]);
    }

    event AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed generationId, address callAddress, uint blockNumber, uint bonusAmount);

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

    function awardMissedBlockBonus(CallDatabase storage self, address toCaller, address callAddress) public {
            FutureBlockCall call = FutureBlockCall(callAddress);

            var generation = self.callerPool.generations[ResourcePoolLib.getGenerationForWindow(self.callerPool, call.targetBlock(), call.targetBlock() + call.gracePeriod())];
            uint i;
            uint bonusAmount;
            address fromCaller;

            uint numWindows = call.gracePeriod() / CALL_WINDOW_SIZE;
            uint blockWindow = (block.number - call.targetBlock()) / CALL_WINDOW_SIZE;

            // Check if we are within the free-for-all period.  If so, we
            // award from all pool members.
            if (blockWindow + 2 > numWindows) {
                    address firstCaller;
                    (,firstCaller) = getDesignatedCaller(self, call.targetBlock(), call.targetBlock() + call.gracePeriod(), call.targetBlock());
                    for (i = call.targetBlock(); i <= call.targetBlock() + call.gracePeriod(); i += CALL_WINDOW_SIZE) {
                            (,fromCaller) = getDesignatedCaller(self, call.targetBlock(), call.targetBlock() + call.gracePeriod(), i);
                            if (fromCaller == firstCaller && i != call.targetBlock()) {
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
                            AwardedMissedBlockBonus(fromCaller, toCaller, generation.id, callAddress, block.number, bonusAmount);
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
                            AwardedMissedBlockBonus(fromCaller, toCaller, generation.id, callAddress, block.number, bonusAmount);

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
    // Ten minutes into the future.
    uint constant MAX_BLOCKS_IN_FUTURE = 40;

    // The minimum gas required to execute a scheduled call on a function that
    // does almost nothing.  This is an approximation and assumes the worst
    // case scenario for gas consumption.
    // 
    // Measured Minimum is closer to 150,000
    uint constant MINIMUM_CALL_GAS = 200000;

    event CallScheduled(address callAddress);

    event CallRejected(address indexed schedulerAddress, bytes32 reason);

    function getCallWindowSize() constant returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function getMinimumGracePeriod() constant returns (uint) {
        return 4 * CALL_WINDOW_SIZE;
    }

    function getMinimumCallGas() constant returns (uint) {
        return MINIMUM_CALL_GAS;
    }

    function getMinimumCallCost(uint basePayment) constant returns (uint) {
        return getMinimumCallCost(basePayment, basePayment);
    }

    function getMinimumCallCost(uint basePayment, uint baseFee) constant returns (uint) {
        return 2 * (baseFee + basePayment) + MINIMUM_CALL_GAS * tx.gasprice;
    }

    function isKnownCall(CallDatabase storage self, address callAddress) constant returns (bool) {
        return GroveLib.exists(self.callIndex, bytes32(callAddress));
    }

    function scheduleCall(CallDatabase storage self, address schedulerAddress, address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment, uint baseFee, uint endowment) public returns (address) {
        /*
        * Primary API for scheduling a call.
        *
        * - No sooner than MAX_BLOCKS_IN_FUTURE
        * - Grace Period must be longer than the minimum grace period.
        * - msg.value must be >= MIN_GAS * tx.gasprice + 2 * (baseFee + basePayment)
        */
        bytes32 reason;

        if (targetBlock < block.number + MAX_BLOCKS_IN_FUTURE) {
            // Don't allow scheduling further than
            // MAX_BLOCKS_IN_FUTURE
            reason = "TOO_SOON";
        }
        else if (gracePeriod < getMinimumGracePeriod()) {
            reason = "GRACE_TOO_SHORT";
        }
        else if (endowment < 2 * (baseFee + basePayment) + MINIMUM_CALL_GAS * tx.gasprice) {
            reason = "INSUFFICIENT_FUNDS";
        }

        if (reason != 0x0) {
            CallRejected(schedulerAddress, reason);
            AccountingLib.sendRobust(schedulerAddress, endowment);
            return;
        }

        var call = new FutureBlockCall.value(endowment)(schedulerAddress, targetBlock, gracePeriod, contractAddress, abiSignature, suggestedGas, basePayment, baseFee);

        // Put the call into the grove index.
        GroveLib.insert(self.callIndex, bytes32(address(call)), int(call.targetBlock()));

        CallScheduled(address(call));

        return address(call);
    }

    function execute(CallDatabase storage self, uint startGas, address callAddress, address executor) {
        if (!isKnownCall(self, callAddress)) {
                CallLib.CallAborted(executor, "UNKNOWN_ADDRESS");
                return;
        }

        FutureBlockCall call = FutureBlockCall(callAddress);

        if (!call.isAlive()) {
                CallLib.CallAborted(executor, "SUICIDED_ALREADY");
                return;
        }
        
        bool isDesignated;
        address designatedCaller;

        (isDesignated, designatedCaller) = getDesignatedCaller(self, call.targetBlock(), call.targetBlock() + call.gracePeriod(), block.number);
        if (isDesignated && designatedCaller != 0x0 && designatedCaller != executor) {
                // Wrong caller
                CallLib.CallAborted(executor, "WRONG_CALLER");
                return;
        }

        if (!call.beforeExecute(executor)) {
                return;
        }

        if (isDesignated) {
            uint blockWindow = (block.number - call.targetBlock()) / getCallWindowSize();
            if (blockWindow > 0) {
                // Someone missed their call so this caller
                // gets to claim their bond for picking up
                // their slack.
                awardMissedBlockBonus(self, executor, callAddress);
            }
        }
        call.execute(startGas, executor);
    }
}
