import "libraries/GroveLib.sol"
import "libraries/ResourcePoolLib.sol"
import "libraries/ScheduledCallLib.sol"
import "libraries/AccountingLib.sol"

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


/*
 *  Version 0.4.0-rc1
 *
 *  address: TODO
 */
contract Alarm {
        /*
         *  Constructor
         *
         *  - sets up relays
         *  - configures the caller pool.
         */
        function Alarm() {
                unauthorizedRelay = new Relay();
                authorizedRelay = new Relay();

                callDatabase.callerPool.freezePeriod = 40;
                callDatabase.callerPool.rotationDelay = 40;
                callDatabase.callerPool.overlapSize = 40;
                // TODO: how to deal with this being a fixed amount.
                callDatabase.callerPool.minimumBond = 1 ether;
        }

        ScheduledCallLib.CallDatabase callDatabase;

        // The author (Piper Merriam) address.
        address constant owner = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        /*
         *  Account Management API
         */
        function deposit() public {
                deposit(msg.sender);
        }

        function deposit(address accountAddress) public {
                /*
                 *  Public API for depositing funds in a specified account.
                 */
                AccountingLib.deposit(callDatabase.gasBank, accountAddress, msg.value);
                Deposit(msg.sender, accountAddress, msg.value);
        }

        function withdraw(uint value) public {
                /*
                 *  Public API for withdrawing funds.
                 */
                if (AccountingLib.withdraw(callDatabase.gasBank, msg.sender, value)) {
                        AccountingLib.Withdraw(msg.sender, value);
                }
                else {
                        AccountingLib.InsufficientFunds(msg.sender, value, callDatabase.gasBank.accountBalances[msg.sender]);
                }
        }

        function() {
                /*
                 *  Fallback function that allows depositing funds just by
                 *  sending a transaction.
                 */
                deposit(msg.sender);
        }

        /*
         *  Scheduling Authorization API
         */
        Relay unauthorizedRelay;
        Relay authorizedRelay;

        function unauthorizedAddress() constant returns (address) {
                return address(unauthorizedRelay);
        }

        function authorizedAddress() constant returns (address) {
                return address(authorizedRelay);
        }

        function addAuthorization(address schedulerAddress) public {
                return ScheduledCallLib.addAuthorization(callDatabase, schedulerAddress, msg.sender);
        }

        function removeAuthorization(address schedulerAddress) public {
                accountAuthorizations[sha3(schedulerAddress, msg.sender)] = false;
        }

        function checkAuthorization(address schedulerAddress, address contractAddress) constant returns (bool) {
                return accountAuthorizations[sha3(schedulerAddress, contractAddress)];
        }

        /*
         *  Caller bonding
         */
        function getMinimumBond() constant returns (uint) {
                // TODO: how to do this with new library.
                return tx.gasprice * block.gaslimit;
        }

        function depositBond() public {
                ResourcePoolLib._addToBond(callDatabase.callerPool, msg.sender, msg.value);
        }

        function withdrawBond(uint value) public {
                ResourcePoolLib.withdrawBond(callDatabase.callerPool, msg.sender, value)
        }

        /*
         *  API used by Alarm service
         */

        // TODO: these functions should be put in the ScheduledCallLib and
        // reworked since they used to be in the CallerPool contract.

        function getDesignatedCaller(bytes32 callKey, uint targetBlock, uint8 gracePeriod, uint blockNumber) constant returns (address) {
                /*
                 *  Returns the caller from the current call pool who is
                 *  designated as the executor of this call.
                 */
                if (blockNumber < targetBlock || blockNumber > targetBlock + gracePeriod) {
                        // blockNumber not within call window.
                        return 0x0;
                }

                // Pool used is based on the starting block for the call.  This
                // allows us to know that the pool cannot change for at least
                // POOL_FREEZE_NUM_BLOCKS which is kept greater than the max
                // grace period.
                uint poolNumber = getPoolKeyForBlock(targetBlock);
                if (poolNumber == 0) {
                        // No pool currently in operation.
                        return 0x0;
                }
                var pool = callDatabase.callerPool[poolNumber];

                uint numWindows = gracePeriod / 4;
                uint blockWindow = (blockNumber - targetBlock) / 4;

                if (blockWindow + 2 > numWindows) {
                        // We are within the free-for-all period.
                        return 0x0;
                }

                uint offset = uint(callKey) % pool.length;
                return pool[(offset + blockWindow) % pool.length];
        }

        event AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed poolNumber, bytes32 callKey, uint blockNumber, uint bonusAmount);

        function _doBondBonusTransfer(address fromCaller, address toCaller) internal returns (uint) {
                uint bonusAmount = getMinimumBond();
                uint bondBalance = callerBonds[fromCaller];

                // If the bond balance is lower than the award
                // balance, then adjust the reward amount to
                // match the bond balance.
                if (bonusAmount > bondBalance) {
                        bonusAmount = bondBalance;
                }

                // Transfer the funds fromCaller => toCaller
                _deductFromBond(fromCaller, bonusAmount);
                _addToBond(toCaller, bonusAmount);

                return bonusAmount;
        }

        function awardMissedBlockBonus(address toCaller, bytes32 callKey, uint targetBlock, uint8 gracePeriod) public {
                if (msg.sender != operator) {
                        return;
                }

                uint poolNumber = getPoolKeyForBlock(targetBlock);
                var pool = callDatabase.callerPool[poolNumber];
                uint i;
                uint bonusAmount;
                address fromCaller;

                uint numWindows = gracePeriod / 4;
                uint blockWindow = (block.number - targetBlock) / 4;

                // Check if we are within the free-for-all period.  If so, we
                // award from all pool members.
                if (blockWindow + 2 > numWindows) {
                        address firstCaller = getDesignatedCaller(callKey, targetBlock, gracePeriod, targetBlock);
                        for (i = targetBlock; i <= targetBlock + gracePeriod; i += 4) {
                                fromCaller = getDesignatedCaller(callKey, targetBlock, gracePeriod, i);
                                if (fromCaller == firstCaller && i != targetBlock) {
                                        // We have already gone through all of
                                        // the pool callers so we should break
                                        // out of the loop.
                                        break;
                                }
                                if (fromCaller == toCaller) {
                                        continue;
                                }
                                bonusAmount = _doBondBonusTransfer(fromCaller, toCaller);

                                // Log the bonus was awarded.
                                AwardedMissedBlockBonus(fromCaller, toCaller, poolNumber, callKey, block.number, bonusAmount);
                        }
                        return;
                }

                // Special case for single member and empty pools
                if (pool.length < 2) {
                        return;
                }

                // Otherwise the award comes from the previous caller.
                for (i = 0; i < pool.length; i++) {
                        // Find where the member is in the pool and
                        // award from the previous pool members bond.
                        if (pool[i] == toCaller) {
                                fromCaller = pool[(i + pool.length - 1) % pool.length];

                                bonusAmount = _doBondBonusTransfer(fromCaller, toCaller);

                                // Log the bonus was awarded.
                                AwardedMissedBlockBonus(fromCaller, toCaller, poolNumber, callKey, block.number, bonusAmount);

                                // Remove the caller from the next pool.
                                if (getNextPoolKey() == 0) {
                                        // This is the first address to modify the
                                        // current pool so we need to setup the next
                                        // pool.
                                        _initiateNextPool();
                                }
                                _removeFromPool(fromCaller, getNextPoolKey());
                                return;
                        }
                }
        }

        /*
         *  Pool Management
         */
        function getGenerationForCall(bytes32 callKey) constant returns (uint) {
                // TODO
        }

        function getGenerationSize(uint generationId) constant returns (uint) {
                return callDatabase.callerPool.generations[generationId].members.length;
        }

        function getCurrentGenerationId() constant returns (uint) {
                return ResourcePoolLib.getCurrentGenerationId(callDatabase.callerPool);
        }

        function getNextGenerationId() constant returns (uint) {
                return ResourcePoolLib.getNextGenerationId(callDatabase.callerPool);
        }

        function isInPool(address callerAddress) constant returns (bool) {
                return ResourcePoolLib.isInPool(callDatabase.callerPool, callerAddress);
        }

        /*
         *  Pool Meta information
         */
        function getPoolFreezePeriod() constant returns (uint) {
                return callDatabase.callerPool.freezePeriod;
        }

        function getPoolOverlapSize() constant returns (uint) {
                return callDatabase.callerPool.overlapSize;
        }

        function getPoolRotationDelay() constant returns (uint) {
                return callDatabase.callerPool.rotationDelay;
        }

        /*
         *  Pool Membership
         */
        function canEnterPool(address callerAddress) constant returns (bool) {
                return ResourcePoolLib.canEnterPool(callDatabase.callerPool, callerAddress, getMinimumBond())
        }

        function canExitPool(address callerAddress) constant returns (bool) {
                return ResourcePoolLib.canExitPool(callDatabase.callerPool, callerAddress);
        }

        function enterPool() public {
                uint generationId = ResourcePoolLib.enterPool(callDatabase.callerPool, callerAddress, getMinimumBond());
                ResourcePoolLib.AddedToPool(callerAddress, generationId);
        }

        function exitPool() public {
                uint generationId = ResourcePoolLib.exitPool(callDatabase.callerPool, callerAddress);
                ResourcePoolLib.RemovedFromPool(callerAddress, generationId);
        }

        /*
         *  Call Information API
         */

        function getLastCallKey() constant returns (bytes32) {
                return callDatabase.lastCallKey;
        }

        /*
         *  Getter methods for `Call` information
         */
        function getCallContractAddress(bytes32 callKey) constant returns (address) {
                return ScheduledCallLib.getCallContractAddress(callDatabase, callKey);
        }

        function getCallScheduledBy(bytes32 callKey) constant returns (address) {
                return ScheduledCallLib.getCallScheduledBy(callDatabase, callKey);
        }

        function getCallCalledAtBlock(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallCalledAtBlock(callDatabase, callKey);
        }

        function getCallGracePeriod(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallGracePeriod(callDatabase, callKey);
        }

        function getCallTargetBlock(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallTargetBlock(callDatabase, callKey);
        }

        function getCallBaseGasPrice(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallBaseGasPrice(callDatabase, callKey);
        }

        function getCallGasPrice(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallGasPrice(callDatabase, callKey);
        }

        function getCallGasUsed(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallGasUsed(callDatabase, callKey);
        }

        function getCallABISignature(bytes32 callKey) constant returns (bytes4) {
                return ScheduledCallLib.getCallABISignature(callDatabase, callKey);
        }

        function checkIfCalled(bytes32 callKey) constant returns (bool) {
                return ScheduledCallLib.checkIfCalled(callDatabase, callKey);
        }

        function checkIfSuccess(bytes32 callKey) constant returns (bool) {
                return ScheduledCallLib.checkIfSuccess(callDatabase, callKey);
        }

        function checkIfCancelled(bytes32 callKey) constant returns (bool) {
                return ScheduledCallLib.checkIfCancelled(callDatabase, callKey);
        }

        function getCallDataHash(bytes32 callKey) constant returns (bytes32) {
                return ScheduledCallLib.getCallDataHash(callDatabase, callKey);
        }

        function getCallPayout(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallPayout(callDatabase, callKey);
        }

        function getCallFee(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallFee(callDatabase, callKey);
        }

        /*
         *  Data Registry API
         */
        function getLastDataHash() constant returns (bytes32) {
                return lastDataHash;
        }

        function getLastDataLength() constant returns (uint) {
                return lastDataLength;
        }

        function getLastData() constant returns (bytes) {
                return lastData;
        }

        function getCallData(bytes32 callKey) constant returns (bytes) {
                return callDatabase.data_registry[callDatabase.calls[callKey].dataHash];
        }

        /*
         *  Data registration API
         */
        function registerData() public {
                ScheduledCallLib.registerData(msg.data);
                ScheduledCallLib.DataRegistered(lastDataHash);
        }

        /*
         *  Call execution API
         */
        function doCall(bytes32 callKey) public {
                bytes18 reason = ScheduledCallLib.doCall(callDatabase, callKey);
                if (reason != 0x0) {
                        ScheduledCallLib.CallAborted(msg.sender, callKey, reason);
                }
                else {
                        ScheduledCallLib.CallExecuted(msg.sender, callKey);
                }
        }

        function getCallMaxCost(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallMaxCost(callDatabase, callKey);
        }

        /*
         *  Call Scheduling API
         */
        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock) public {
                /*
                 *  Schedule call with gracePeriod defaulted to 255 and nonce
                 *  defaulted to 0.
                 */
                ScheduledCallLib.scheduleCall(callDatabase, contractAddress, abiSignature, dataHash, targetBlock, 255, 0);
        }

        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod) public {
                /*
                 *  Schedule call with nonce defaulted to 0.
                 */
                ScheduledCallLib.scheduleCall(callDatabase, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, 0);
        }

        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public {
                /*
                 * Primary API for scheduling a call.  Prior to calling this
                 * the data should already have been registered through the
                 * `registerData` API.
                 */
                bytes15 reason = ScheduledCallLib.scheduleCall(callDatabase, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);
                bytes32 callKey = ScheduledCallLib.getCallKey(msg.sender, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);

                if (reason != 0x0) {
                        ScheduledCallLib.CallRejected(callKey, reason);
                }
                else {
                        ScheduledCallLib.CallScheduled(callKey);
                }
        }

        function cancelCall(bytes32 callKey) public {
                if (ScheduledCallLib.cancelCall(callDatabase, callKey) {
                        ScheduledCallLib.CallCancelled(callDatabase, callKey);
                }
        }

        /*
         *  Next Call API
         */
        function getNextCall(uint blockNumber) {
                // TODO: tests
                return GroveLib.query(callIndex, ">=", int(blockNumber));
        }

        function getNextCallSibling(bytes32 callKey) {
                // TODO: tests
                return GroveLib.getNextNode(callIndex, callKey);
        }
}
