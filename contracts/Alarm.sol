import "libraries/GroveLib.sol";
import "libraries/ResourcePoolLib.sol";
import "libraries/ScheduledCallLib.sol";
import "libraries/AccountingLib.sol";


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
                callDatabase.unauthorizedRelay = new Relay();
                callDatabase.authorizedRelay = new Relay();

                callDatabase.callerPool.freezePeriod = 80;
                callDatabase.callerPool.rotationDelay = 80;
                callDatabase.callerPool.overlapSize = 256;
        }

        ScheduledCallLib.CallDatabase callDatabase;

        // The author (Piper Merriam) address.
        address constant owner = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        /*
         *  Account Management API
         */
        function getAccountBalance(address accountAddress) constant public returns (uint) {
                return callDatabase.gasBank.accountBalances[accountAddress];
        }

        function deposit() public {
                deposit(msg.sender);
        }

        function deposit(address accountAddress) public {
                /*
                 *  Public API for depositing funds in a specified account.
                 */
                AccountingLib.deposit(callDatabase.gasBank, accountAddress, msg.value);
                AccountingLib.Deposit(msg.sender, accountAddress, msg.value);
        }

        function withdraw(uint value) public {
                /*
                 *  Public API for withdrawing funds.
                 */
                if (AccountingLib.withdraw(callDatabase.gasBank, msg.sender, value)) {
                        AccountingLib.Withdrawal(msg.sender, value);
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
        function unauthorizedAddress() constant returns (address) {
                return address(callDatabase.unauthorizedRelay);
        }

        function authorizedAddress() constant returns (address) {
                return address(callDatabase.authorizedRelay);
        }

        function addAuthorization(address schedulerAddress) public {
                ScheduledCallLib.addAuthorization(callDatabase, schedulerAddress, msg.sender);
        }

        function removeAuthorization(address schedulerAddress) public {
                callDatabase.accountAuthorizations[sha3(schedulerAddress, msg.sender)] = false;
        }

        function checkAuthorization(address schedulerAddress, address contractAddress) constant returns (bool) {
                return callDatabase.accountAuthorizations[sha3(schedulerAddress, contractAddress)];
        }

        /*
         *  Caller bonding
         */
        function getMinimumBond() constant returns (uint) {
                return ScheduledCallLib.getMinimumBond();
        }

        function depositBond() public {
                ResourcePoolLib.addToBond(callDatabase.callerPool, msg.sender, msg.value);
        }

        function withdrawBond(uint value) public {
                ResourcePoolLib.withdrawBond(callDatabase.callerPool, msg.sender, value, getMinimumBond());
        }

        function getBondBalance() constant returns (uint) {
                return getBondBalance(msg.sender);
        }

        function getBondBalance(address callerAddress) constant returns (uint) {
                return callDatabase.callerPool.bonds[callerAddress];
        }


        /*
         *  Pool Management
         */
        function getGenerationForCall(bytes32 callKey) constant returns (uint) {
                var call = callDatabase.calls[callKey];
                return ResourcePoolLib.getGenerationForWindow(callDatabase.callerPool, call.targetBlock, call.targetBlock + call.gracePeriod);
        }

        function getGenerationSize(uint generationId) constant returns (uint) {
                return callDatabase.callerPool.generations[generationId].members.length;
        }

        function getGenerationStartAt(uint generationId) constant returns (uint) {
                return callDatabase.callerPool.generations[generationId].startAt;
        }

        function getGenerationEndAt(uint generationId) constant returns (uint) {
                return callDatabase.callerPool.generations[generationId].endAt;
        }

        function getCurrentGenerationId() constant returns (uint) {
                return ResourcePoolLib.getCurrentGenerationId(callDatabase.callerPool);
        }

        function getNextGenerationId() constant returns (uint) {
                return ResourcePoolLib.getNextGenerationId(callDatabase.callerPool);
        }

        function isInPool() constant returns (bool) {
                return ResourcePoolLib.isInPool(callDatabase.callerPool, msg.sender);
        }

        function isInPool(address callerAddress) constant returns (bool) {
                return ResourcePoolLib.isInPool(callDatabase.callerPool, callerAddress);
        }

        function isInGeneration(uint generationId) constant returns (bool) {
                return isInGeneration(msg.sender, generationId);
        }

        function isInGeneration(address callerAddress, uint generationId) constant returns (bool) {
                return ResourcePoolLib.isInGeneration(callDatabase.callerPool, callerAddress, generationId);
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
        function canEnterPool() constant returns (bool) {
                return ResourcePoolLib.canEnterPool(callDatabase.callerPool, msg.sender, getMinimumBond());
        }

        function canEnterPool(address callerAddress) constant returns (bool) {
                return ResourcePoolLib.canEnterPool(callDatabase.callerPool, callerAddress, getMinimumBond());
        }

        function canExitPool() constant returns (bool) {
                return ResourcePoolLib.canExitPool(callDatabase.callerPool, msg.sender);
        }

        function canExitPool(address callerAddress) constant returns (bool) {
                return ResourcePoolLib.canExitPool(callDatabase.callerPool, callerAddress);
        }

        function enterPool() public {
                uint generationId = ResourcePoolLib.enterPool(callDatabase.callerPool, msg.sender, getMinimumBond());
                ResourcePoolLib.AddedToGeneration(msg.sender, generationId);
        }

        function exitPool() public {
                uint generationId = ResourcePoolLib.exitPool(callDatabase.callerPool, msg.sender);
                ResourcePoolLib.RemovedFromGeneration(msg.sender, generationId);
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

        function getCallMaxCost(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getCallMaxCost(callDatabase, callKey);
        }

        function getCallData(bytes32 callKey) constant returns (bytes) {
                return callDatabase.data_registry[callDatabase.calls[callKey].dataHash];
        }

        /*
         *  Data registration API
         */
        function registerData() public {
                ScheduledCallLib.registerData(callDatabase, msg.data);
                ScheduledCallLib.DataRegistered(callDatabase.lastDataHash);
        }

        function getLastDataHash() constant returns (bytes32) {
                return callDatabase.lastDataHash;
        }

        function getLastDataLength() constant returns (uint) {
                return callDatabase.lastDataLength;
        }

        function getLastData() constant returns (bytes) {
                return callDatabase.lastData;
        }

        /*
         *  Call execution API
         */
        function doCall(bytes32 callKey) public {
                ScheduledCallLib.doCall(callDatabase, callKey, msg.sender);
        }

        /*
         *  Call Scheduling API
         */
        function getMinimumGracePeriod() constant returns (uint) {
                return ScheduledCallLib.getMinimumGracePeriod();
        }

        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock) public {
                /*
                 *  Schedule call with gracePeriod defaulted to 255 and nonce
                 *  defaulted to 0.
                 */
                scheduleCall(contractAddress, abiSignature, dataHash, targetBlock, 255, 0);
        }

        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod) public {
                /*
                 *  Schedule call with nonce defaulted to 0.
                 */
                scheduleCall(contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, 0);
        }

        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public {
                /*
                 * Primary API for scheduling a call.  Prior to calling this
                 * the data should already have been registered through the
                 * `registerData` API.
                 */
                bytes15 reason = ScheduledCallLib.scheduleCall(callDatabase, msg.sender, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);
                bytes32 callKey = ScheduledCallLib.computeCallKey(msg.sender, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);

                if (reason != 0x0) {
                        ScheduledCallLib.CallRejected(callKey, reason);
                }
                else {
                        ScheduledCallLib.CallScheduled(callKey);
                }
        }

        function cancelCall(bytes32 callKey) public {
                if (ScheduledCallLib.cancelCall(callDatabase, callKey, address(msg.sender))) {
                        ScheduledCallLib.CallCancelled(callKey);
                }
        }

        /*
         *  Next Call API
         */
        function getCallWindowSize() constant returns (uint) {
                return ScheduledCallLib.getCallWindowSize();
        }

        function getGenerationIdForCall(bytes32 callKey) constant returns (uint) {
                return ScheduledCallLib.getGenerationIdForCall(callDatabase, callKey);
        }

        function getDesignatedCaller(bytes32 callKey, uint blockNumber) constant returns (address) {
                return ScheduledCallLib.getDesignatedCaller(callDatabase, callKey, blockNumber);
        }

        function getNextCall(uint blockNumber) constant returns (bytes32) {
                return GroveLib.query(callDatabase.callIndex, ">=", int(blockNumber));
        }

        function getNextCallSibling(bytes32 callKey) constant returns (bytes32) {
                return GroveLib.getNextNode(callDatabase.callIndex, callKey);
        }
}
