/*
 *  Version 0.2.0
 *
 *  address: 0xc1cfa6ac1d7cf99bd1e145dcd04ec462b3b0c4da
 */
contract Relay {
        address operator;

        function Relay() {
                operator = msg.sender;
        }

        function relayCall(address contractAddress, bytes4 abiSignature, bytes data) public returns (bool) {
                if (msg.sender != operator) {
                        __throw();
                }
                return contractAddress.call(abiSignature, data);
        }

        function __throw() internal {
                int[] x;
                x[1];
        }
}


contract CallerPool {
        address operator;

        function CallerPool() {
                operator = msg.sender;
        }

        /*
         *  Caller bonding
         */
        mapping (address => uint) public callerBonds;

        function getMinimumBond() constant returns (uint) {
                return tx.gasprice * block.gaslimit;
        }

        function _deductFromBond(address callerAddress, uint value) internal {
                /*
                 *  deduct funds from a bond value without risk of an
                 *  underflow.
                 */
                if (value > callerBonds[callerAddress]) {
                        // Prevent Underflow.
                        __throw();
                }
                callerBonds[callerAddress] -= value;
        }

        function _addToBond(address callerAddress, uint value) internal {
                /*
                 *  Add funds to a bond value without risk of an
                 *  overflow.
                 */
                if (callerBonds[callerAddress] + value < callerBonds[callerAddress]) {
                        // Prevent Overflow
                        __throw();
                }
                callerBonds[callerAddress] += value;
        }

        function depositBond() public {
                _addToBond(msg.sender, msg.value);
        }

        function withdrawBond(uint value) public {
                /*
                 *  Only if you are not in either of the current call pools.
                 */
                if (isInAnyPool(msg.sender)) {
                        // Prevent underflow
                        if (value > callerBonds[msg.sender]) {
                                __throw();
                        }
                        // Don't allow withdrawl if this would drop the bond
                        // balance below the minimum.
                        if (callerBonds[msg.sender] - value < getMinimumBond()) {
                                return;
                        }
                }
                _deductFromBond(msg.sender, value);
                if (!msg.sender.send(value)) {
                        // Potentially sending money to a contract that
                        // has a fallback function.  So instead, try
                        // tranferring the funds with the call api.
                        if (!msg.sender.call.gas(msg.gas).value(value)()) {
                                // Revert the entire transaction.  No
                                // need to destroy the funds.
                                __throw();
                        }
                }
        }

        function() {
                /*
                 *  Fallback function that allows depositing bond funds just by
                 *  sending a transaction.
                 */
                _addToBond(msg.sender, msg.value);
        }

        /*
         *  API used by Alarm service
         */
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
                var pool = callerPools[poolNumber];

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
                var pool = callerPools[poolNumber];
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
         *  Caller Pool Management
         */
        uint[] public poolHistory;
        mapping (uint => address[]) callerPools;

        function getPoolKeyForBlock(uint blockNumber) constant returns (uint) {
                if (poolHistory.length == 0) {
                        return 0;
                }
                for (uint i = 0; i < poolHistory.length; i++) {
                        uint poolStartBlock = poolHistory[poolHistory.length - i - 1];
                        if (poolStartBlock <= blockNumber) {
                                return poolStartBlock;
                        }
                }
                return 0;
        }

        function getActivePoolKey() constant returns (uint) {
                return getPoolKeyForBlock(block.number);
        }

        function getPoolSize(uint poolKey) constant returns (uint) {
                return callerPools[poolKey].length;
        }

        function getNextPoolKey() constant returns (uint) {
                if (poolHistory.length == 0) {
                        return 0;
                }
                uint latestPool = poolHistory[poolHistory.length - 1];
                if (latestPool > block.number) {
                        return latestPool;
                }
                return 0;
        }

        function isInAnyPool(address callerAddress) constant returns (bool) {
                /*
                 *  Returns boolean whether the `callerAddress` is in either
                 *  the current active pool or the next pool.
                 */
                return isInPool(msg.sender, getActivePoolKey()) || isInPool(msg.sender, getNextPoolKey());
        }

        function isInPool(address callerAddress, uint poolNumber) constant returns (bool) {
                /*
                 *  Returns boolean whether the `callerAddress` is in the
                 *  poolNumber.
                 */
                if (poolNumber == 0 ) {
                        // Nobody can be in pool 0
                        return false;
                }

                var pool = callerPools[poolNumber];

                // Nobody is in the pool.
                if (pool.length == 0) {
                        return false;
                }

                for (uint i = 0; i < pool.length; i++) {
                        // Address is in the pool and thus is allowed to exit.
                        if (pool[i] == callerAddress) {
                                return true;
                        }
                }

                return false;
        }

        // Ten minutes into the future.
        //uint constant POOL_FREEZE_NUM_BLOCKS = 256;
        uint constant POOL_FREEZE_NUM_BLOCKS = 40;

        function getPoolFreezeDuration() constant returns (uint) {
                return POOL_FREEZE_NUM_BLOCKS;
        }

        function getPoolMinimumLength() constant returns (uint) {
                return 2 * POOL_FREEZE_NUM_BLOCKS;
        }

        function canEnterPool(address callerAddress) constant returns (bool) {
                /*
                 *  Returns boolean whether `callerAddress` is allowed to enter
                 *  the next pool (which may or may not already have been
                 *  created.
                 */
                // Not allowed to join if you are in either the current
                // active pool or the next pool.
                if (isInAnyPool(callerAddress)) {
                        return false;
                }

                // Next pool begins within the POOL_FREEZE_NUM_BLOCKS grace
                // period so no changes are allowed.
                if (getNextPoolKey() != 0 && block.number >= (getNextPoolKey() - POOL_FREEZE_NUM_BLOCKS)) {
                        return false;
                }

                // Account bond balance is too low.
                if (callerBonds[callerAddress] < getMinimumBond()) {
                        return false;
                }
                
                return true;
        }

        function canExitPool(address callerAddress) constant returns (bool) {
                /*
                 *  Returns boolean whether `callerAddress` is allowed to exit
                 *  the current active pool.
                 */
                // Can't exit if we aren't in the current active pool.
                if (!isInPool(callerAddress, getActivePoolKey())) {
                        return false;
                }

                // There is a next pool coming up.
                if (getNextPoolKey() != 0) {
                        // Next pool begins within the POOL_FREEZE_NUM_BLOCKS
                        // window and thus can't be modified.
                        if (block.number >= (getNextPoolKey() - POOL_FREEZE_NUM_BLOCKS)) {
                                return false;
                        }

                        // Next pool was already setup and callerAddress isn't
                        // in it which indicates that they already left.
                        if (!isInPool(callerAddress, getNextPoolKey())) {
                                return false;
                        }
                }

                // They must be in the current pool and either the next pool
                // hasn't been initiated or it has but this user hasn't left
                // yet.
                return true;
        }

        function _initiateNextPool() internal {
                if (getNextPoolKey() != 0) {
                        // If there is already a next pool, we shouldn't
                        // initiate a new one until it has become active.
                        __throw();
                }
                // Set the next pool to start at double the freeze block number
                // in the future.
                uint nextPool = block.number + 2 * POOL_FREEZE_NUM_BLOCKS;

                // Copy the current pool into the next pool.
                callerPools[nextPool] = callerPools[getActivePoolKey()];

                // Randomize the pool order
                _shufflePool(nextPool);

                // Push the next pool into the pool history.
                poolHistory.length += 1;
                poolHistory[poolHistory.length - 1] = nextPool;
        }

        function _shufflePool(uint poolNumber) internal {
                var pool = callerPools[poolNumber];

                uint swapIndex;
                address buffer;

                for (uint i = 0; i < pool.length; i++) {
                        swapIndex = uint(sha3(block.blockhash(block.number), i)) % pool.length;
                        if (swapIndex == i) {
                                continue;
                        }
                        buffer = pool[i];
                        pool[i] = pool[swapIndex];
                        pool[swapIndex] = buffer;
                }
        }

        event AddedToPool(address indexed callerAddress, uint indexed pool);
        event RemovedFromPool(address indexed callerAddress, uint indexed pool);

        function _addToPool(address callerAddress, uint poolNumber) internal {
                if (poolNumber == 0 ) {
                        // This shouldn't be called with 0;
                        __throw();
                }

                // already in the pool.
                if (isInPool(callerAddress, poolNumber)) {
                        return;
                }
                var pool = callerPools[poolNumber];
                pool.length += 1;
                pool[pool.length - 1] = callerAddress;
                
                // Log the addition.
                AddedToPool(callerAddress, poolNumber);
        }

        function _removeFromPool(address callerAddress, uint poolNumber) internal {
                if (poolNumber == 0 ) {
                        // This shouldn't be called with 0;
                        __throw();
                }

                // nothing to remove.
                if (!isInPool(callerAddress, poolNumber)) {
                        return;
                }
                var pool = callerPools[poolNumber];
                // special case length == 1
                if (pool.length == 1) {
                        pool.length = 0;
                }
                for (uint i = 0; i < pool.length; i++) {
                        // When we find the index of the address to remove we
                        // shift the last person to that location and then we
                        // truncate the last member off of the end.
                        if (pool[i] == callerAddress) {
                                pool[i] = pool[pool.length - 1];
                                pool.length -= 1;
                                break;
                        }
                }

                // Log the addition.
                RemovedFromPool(callerAddress, poolNumber);
        }

        function enterPool() public {
                /*
                 *  Request to be added to the call pool.
                 */
                if (canEnterPool(msg.sender)) {
                        if (getNextPoolKey() == 0) {
                                // This is the first address to modify the
                                // current pool so we need to setup the next
                                // pool.
                                _initiateNextPool();
                        }
                        _addToPool(msg.sender, getNextPoolKey());
                }
        }

        function exitPool() public {
                /*
                 *  Request to be removed from the call pool.
                 */
                if (canExitPool(msg.sender)) {
                        if (getNextPoolKey() == 0) {
                                // This is the first address to modify the
                                // current pool so we need to setup the next
                                // pool.
                                _initiateNextPool();
                        }
                        _removeFromPool(msg.sender, getNextPoolKey());
                }
        }

        function __throw() internal {
                int[] x;
                x[1];
        }
}


contract GroveAPI {
        /*
         *  Shortcuts
         */
        function getIndexId(address ownerAddress, bytes32 indexName) constant returns (bytes32);
        function getNodeId(bytes32 indexId, bytes32 id) constant returns (bytes32);

        /*
         *  Node and Index API
         */
        function getIndexName(bytes32 indexId) constant returns (bytes32);
        function getIndexRoot(bytes32 indexId) constant returns (bytes32);
        function getNodeId(bytes32 nodeId) constant returns (bytes32);
        function getNodeIndexId(bytes32 nodeId) constant returns (bytes32);
        function getNodeValue(bytes32 nodeId) constant returns (int);
        function getNodeHeight(bytes32 nodeId) constant returns (uint);
        function getNodeParent(bytes32 nodeId) constant returns (bytes32);
        function getNodeLeftChild(bytes32 nodeId) constant returns (bytes32);
        function getNodeRightChild(bytes32 nodeId) constant returns (bytes32);

        /*
         *  Insert and Query API
         */
        function insert(bytes32 indexName, bytes32 id, int value) public;
        function query(bytes32 indexId, bytes2 operator, int value) constant returns (bytes32);
}


contract Alarm {
        /*
         *  Administration API
         *
         *  There is currently no special administrative API beyond the hard
         *  coded owner address which receives 1% of each executed call.  This
         *  eliminates any need for trust as nobody has any special access.
         */
        function Alarm(address groveAddress) {
                unauthorizedRelay = new Relay();
                authorizedRelay = new Relay();
                callerPool = new CallerPool();
                grove = GroveAPI(groveAddress);
        }

        address constant owner = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        // The deployed grove contract for call tree tracking.
        GroveAPI grove;

        /*
         *  Account Management API
         */
        mapping (address => uint) public accountBalances;

        function _deductFunds(address accountAddress, uint value) internal {
                /*
                 *  Helper function that should be used for any reduction of
                 *  account funds.  It has error checking to prevent
                 *  underflowing the account balance which would be REALLY bad.
                 */
                if (value > accountBalances[accountAddress]) {
                        // Prevent Underflow.
                        __throw();
                }
                accountBalances[accountAddress] -= value;
        }

        function _addFunds(address accountAddress, uint value) internal {
                /*
                 *  Helper function that should be used for any addition of
                 *  account funds.  It has error checking to prevent
                 *  overflowing the account balance.
                 */
                if (accountBalances[accountAddress] + value < accountBalances[accountAddress]) {
                        // Prevent Overflow.
                        __throw();
                }
                accountBalances[accountAddress] += value;
        }

        event Deposit(address indexed _from, address indexed accountAddress, uint value);

        function deposit(address accountAddress) public {
                /*
                 *  Public API for depositing funds in a specified account.
                 */
                _addFunds(accountAddress, msg.value);
                Deposit(msg.sender, accountAddress, msg.value);
        }

        event Withdraw(address indexed accountAddress, uint value);

        function withdraw(uint value) public {
                /*
                 *  Public API for withdrawing funds.
                 */
                if (accountBalances[msg.sender] >= value) {
                        _deductFunds(msg.sender, value);
                        if (!msg.sender.send(value)) {
                                // Potentially sending money to a contract that
                                // has a fallback function.  So instead, try
                                // tranferring the funds with the call api.
                                if (!msg.sender.call.gas(msg.gas).value(value)()) {
                                        // Revert the entire transaction.  No
                                        // need to destroy the funds.
                                        __throw();
                                }
                        }
                        Withdraw(msg.sender, value);
                }
        }

        function() {
                /*
                 *  Fallback function that allows depositing funds just by
                 *  sending a transaction.
                 */
                _addFunds(msg.sender, msg.value);
                Deposit(msg.sender, msg.sender, msg.value);
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

        mapping (bytes32 => bool) accountAuthorizations;

        function addAuthorization(address schedulerAddress) public {
                accountAuthorizations[sha3(schedulerAddress, msg.sender)] = true;
        }

        function removeAuthorization(address schedulerAddress) public {
                accountAuthorizations[sha3(schedulerAddress, msg.sender)] = false;
        }

        function checkAuthorization(address schedulerAddress, address contractAddress) constant returns (bool) {
                return accountAuthorizations[sha3(schedulerAddress, contractAddress)];
        }

        /*
         *  Call Information API
         */
        bytes32 lastCallKey;

        function getLastCallKey() constant returns (bytes32) {
                return lastCallKey;
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

        mapping (bytes32 => Call) key_to_calls;

        /*
         *  Getter methods for `Call` information
         */
        function getCallContractAddress(bytes32 callKey) constant returns (address) {
                return key_to_calls[callKey].contractAddress;
        }

        function getCallScheduledBy(bytes32 callKey) constant returns (address) {
                return key_to_calls[callKey].scheduledBy;
        }

        function getCallCalledAtBlock(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].calledAtBlock;
        }

        function getCallGracePeriod(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].gracePeriod;
        }

        function getCallTargetBlock(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].targetBlock;
        }

        function getCallBaseGasPrice(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].baseGasPrice;
        }

        function getCallGasPrice(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].gasPrice;
        }

        function getCallGasUsed(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].gasUsed;
        }

        function getCallABISignature(bytes32 callKey) constant returns (bytes4) {
                return key_to_calls[callKey].abiSignature;
        }

        function checkIfCalled(bytes32 callKey) constant returns (bool) {
                return key_to_calls[callKey].wasCalled;
        }

        function checkIfSuccess(bytes32 callKey) constant returns (bool) {
                return key_to_calls[callKey].wasSuccessful;
        }

        function checkIfCancelled(bytes32 callKey) constant returns (bool) {
                return key_to_calls[callKey].isCancelled;
        }

        function getCallDataHash(bytes32 callKey) constant returns (bytes32) {
                return key_to_calls[callKey].dataHash;
        }

        function getCallPayout(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].payout;
        }

        function getCallFee(bytes32 callKey) constant returns (uint) {
                return key_to_calls[callKey].fee;
        }

        /*
         *  Data Registry API
         */
        bytes lastData;
        uint lastDataLength;
        bytes32 lastDataHash;

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
                return hash_to_data[key_to_calls[callKey].dataHash];
        }

        mapping (bytes32 => bytes) hash_to_data;

        /*
         *  Data registration API
         */
        event DataRegistered(bytes32 indexed dataHash);

        function registerData() public {
                lastData.length = msg.data.length - 4;
                if (msg.data.length > 4) {
                        for (uint i = 0; i < lastData.length; i++) {
                                lastData[i] = msg.data[i + 4];
                        }
                }
                hash_to_data[sha3(lastData)] = lastData;
                lastDataHash = sha3(lastData);
                lastDataLength = lastData.length;
                lastData = lastData;

                // Log it.
                //DataRegistered(lastDataHash);
        }

        /*
         *  Call execution API
         */
        CallerPool callerPool;

        function getCallerPoolAddress() constant returns (address) {
                return address(callerPool);
        }

        // This number represents the constant gas cost of the addition
        // operations that occur in `doCall` that cannot be tracked with
        // msg.gas.
        uint constant EXTRA_CALL_GAS = 151054;

        // This number represents the overall overhead involved in executing a
        // scheduled call.
        uint constant CALL_OVERHEAD = 144982;

        event CallExecuted(address indexed executedBy, bytes32 indexed callKey);
        event CallAborted(address indexed executedBy, bytes32 indexed callKey, bytes18 reason);

        function doCall(bytes32 callKey) public {
                uint gasBefore = msg.gas;

                var call = key_to_calls[callKey];

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

                _deductFunds(call.scheduledBy, call.payout + call.fee);

                _addFunds(msg.sender, call.payout);
                _addFunds(owner, call.fee);
        }

        function getCallMaxCost(bytes32 callKey) constant returns (uint) {
                /*
                 *  tx.gasprice * block.gaslimit
                 *  
                 */
                // call cost + 2%
                var call = key_to_calls[callKey];

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
                bytes32 callKey = getCallKey(msg.sender, contractAddress, abiSignature, dataHash, targetBlock, gracePeriod, nonce);

                if (dataHash != emptyDataHash && hash_to_data[dataHash].length == 0) {
                        // Don't allow registering calls if the data hash has
                        // not actually been registered.  The only exception is
                        // the *emptyDataHash*.
                        CallRejected(callKey, "NO_DATA");
                        return;
                }

                if (targetBlock < block.number + MAX_BLOCKS_IN_FUTURE) {
                        // Don't allow scheduling further than
                        // MAX_BLOCKS_IN_FUTURE
                        CallRejected(callKey, "TOO_SOON");
                        return;
                }
                var call = key_to_calls[callKey];

                if (call.contractAddress != 0x0) {
                        CallRejected(callKey, "DUPLICATE");
                        return;
                }

                if (gracePeriod < 16) {
                        CallRejected(callKey, "GRACE_TOO_SHORT");
                        return;
                }

                lastCallKey = callKey;

                call.contractAddress = contractAddress;
                call.scheduledBy = msg.sender;
                call.nonce = nonce;
                call.abiSignature = abiSignature;
                call.dataHash = dataHash;
                call.targetBlock = targetBlock;
                call.gracePeriod = gracePeriod;
                call.baseGasPrice = tx.gasprice;

                // Put the call into the grove index.
                grove.insert(GROVE_INDEX_NAME, lastCallKey, int(call.targetBlock));

                CallScheduled(lastCallKey);
        }

        bytes32 constant GROVE_INDEX_NAME = "callTargetBlock";

        function getGroveAddress() constant returns (address) {
                return address(grove);
        }

        function getGroveIndexName() constant returns (bytes32) {
                return GROVE_INDEX_NAME;
        }

        function getGroveIndexId() constant returns (bytes32) {
                return grove.getIndexId(address(this), GROVE_INDEX_NAME);
        }

        event CallCancelled(bytes32 indexed callKey);

        // Two minutes
        uint constant MIN_CANCEL_WINDOW = 8;

        function cancelCall(bytes32 callKey) public {
                var call = key_to_calls[callKey];
                if (call.scheduledBy != msg.sender) {
                        // Nobody but the scheduler can cancel a call.
                        return;
                }
                if (call.wasCalled) {
                        // No need to cancel a call that already was executed.
                        return;
                }
                if (call.targetBlock - MIN_CANCEL_WINDOW <= block.number) {
                        // Call cannot be cancelled this close to execution.
                        return;
                }
                call.isCancelled = true;
                CallCancelled(callKey);
        }

        function __throw() internal {
                int[] x;
                x[1];
        }
}
