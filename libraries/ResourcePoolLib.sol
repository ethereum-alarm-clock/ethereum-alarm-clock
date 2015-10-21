// Resource Pool v0.1.0
import "libraries/GroveLib.sol";
import "libraries/StringLib.sol";


// @title ResourcePoolLib - Library for a set of resources that are ready for use.
// @author Piper Merriam <pipermerriam@gmail.com>
library ResourcePoolLib {
        struct Pool {
                uint rotationDelay;
                uint overlapSize;
                uint freezePeriod;

                uint _id;

                GroveLib.Index generationStart;
                GroveLib.Index generationEnd;

                mapping (uint => Generation) generations;
                mapping (address => uint) bonds;
        }

        /*
         * Generations have the following properties.
         *
         * 1. Must always overlap by a minimum amount specified by MIN_OVERLAP.
         *
         *    1   2   3   4   5   6   7   8   9   10  11  12  13
         *    [1:-----------------]
         *                [4:--------------------->
         */
        struct Generation {
                uint id;
                uint startAt;
                uint endAt;
                address[] members;
        }

        function createNextGeneration(Pool storage self) public returns (uint) {
            // TODO: tests
                /*
                 *  Creat a new pool generation with all of the current
                 *  generation's members copied over in random order.
                 */
                Generation storage previousGeneration = self.generations[self._id];

                self._id += 1;
                Generation storage nextGeneration = self.generations[self._id];
                nextGeneration.id = self._id;
                nextGeneration.startAt = block.number + self.freezePeriod + self.rotationDelay;
                GroveLib.insert(self.generationStart, StringLib.uintToBytes(nextGeneration.id), int(nextGeneration.startAt));

                if (previousGeneration.id == 0) {
                        // This is the first generation so we just need to set
                        // it's `id` and `startAt`.
                        return nextGeneration.id;
                }

                // Set the end date for the current generation.
                previousGeneration.endAt = block.number + self.freezePeriod + self.rotationDelay + self.overlapSize;
                GroveLib.insert(self.generationEnd, StringLib.uintToBytes(previousGeneration.id), int(previousGeneration.endAt));

                // Now we copy the members of the previous generation over to
                // the next generation as well as randomizing their order.
                address[] memory members = previousGeneration.members;

                for (uint i = 0; i < members.length; i++) {
                    // Pick a *random* index and push it onto the next
                    // generation's members.
                    uint index = uint(sha3(block.blockhash(block.number))) % (members.length - nextGeneration.members.length);
                    nextGeneration.members.length += 1;
                    nextGeneration.members[nextGeneration.members.length - 1] = members[index];

                    // Then move the member at the last index into the picked
                    // index's location.
                    members[index] = members[members.length - 1];
                }

                return nextGeneration.id;
        }

        function getGenerationForWindow(Pool storage self, uint leftBound, uint rightBound) constant returns (uint) {
            // TODO: tests
                var left = GroveLib.query(self.generationStart, "<=", int(leftBound));

                if (left != 0x0) {
                    Generation memory leftCandidate = self.generations[StringLib.bytesToUInt(left)];
                    if (leftCandidate.startAt <= leftBound && (leftCandidate.endAt >= rightBound || leftCandidate.endAt == 0)) {
                        return leftCandidate.id;
                    }
                }

                var right = GroveLib.query(self.generationEnd, ">=", int(rightBound));
                if (right != 0x0) {
                    Generation memory rightCandidate = self.generations[StringLib.bytesToUInt(right)];
                    if (rightCandidate.startAt <= leftBound && (rightCandidate.endAt >= rightBound || rightCandidate.endAt == 0)) {
                        return rightCandidate.id;
                    }
                }

                return 0;
        }

        function getNextGenerationId(Pool storage self) constant returns (uint) {
            // TODO: tests
                var next = GroveLib.query(self.generationStart, ">", int(block.number));
                if (next == 0x0) {
                    return 0;
                }
                return StringLib.bytesToUInt(next);
        }

        function getCurrentGenerationId(Pool storage self) constant returns (uint) {
            // TODO: tests
                var next = GroveLib.query(self.generationEnd, ">", int(block.number));
                if (next != 0x0) {
                    return StringLib.bytesToUInt(next);
                }

                next = GroveLib.query(self.generationStart, "<=", int(block.number));
                if (next != 0x0) {
                    return StringLib.bytesToUInt(next);
                }
                return 0;
        }

        /*
         *  Pool membership API
         */
        function isInGeneration(Pool storage self, address resourceAddress, uint generationId) constant returns (bool) {
            // TODO: tests
            if (generationId == 0) {
                return false;
            }
            Generation memory generation = self.generations[generationId];
            for (uint i = 0; i < generation.members.length; i++) {
                if (generation.members[i] == resourceAddress) {
                    return true;
                }
            }
            return false;
        }

        function isInCurrentGeneration(Pool storage self, address resourceAddress) constant returns (bool) {
            // TODO: tests
            return isInGeneration(self, resourceAddress, getCurrentGenerationId(self));
        }

        function isInNextGeneration(Pool storage self, address resourceAddress) constant returns (bool) {
            // TODO: tests
            return isInGeneration(self, resourceAddress, getNextGenerationId(self));
        }

        function isInPool(Pool storage self, address resourceAddress) constant returns (bool) {
            // TODO: tests
            return (isInCurrentGeneration(self, resourceAddress) || isInNextGeneration(self, resourceAddress));
        }

        event _AddedToGeneration(address indexed callerAddress, uint indexed generationId);
        function AddedToGeneration(address callerAddress, uint generationId) public {
                _AddedToGeneration(callerAddress, generationId);
        }
        event _RemovedFromGeneration(address indexed callerAddress, uint indexed generationId);
        function RemovedFromGeneration(address callerAddress, uint generationId) public {
                _RemovedFromGeneration(callerAddress, generationId);
        }

        function canEnterPool(Pool storage self, address resourceAddress, uint minimumBond) constant returns (bool) {
            /*
             *  - bond
             *  - pool is open
             *  - not already in it.
             *  - not already left it.
             */
            // TODO: tests
            if (self.bonds[resourceAddress] < minimumBond) {
                // Insufficient bond balance;
                return false;
            }

            if (isInPool(self, resourceAddress)) {
                // Already in the pool either in the next upcoming generation
                // or the currently active generation.
                return false;
            }

            var nextGenerationId = getNextGenerationId(self);
            if (nextGenerationId != 0) {
                var nextGeneration = self.generations[nextGenerationId];
                if (block.number + self.freezePeriod >= nextGeneration.startAt) {
                    // Next generation starts too soon.
                    return false;
                }
            }

            return true;
        }

        function enterPool(Pool storage self, address resourceAddress, uint minimumBond) public returns (uint) {
            if (!canEnterPool(self, resourceAddress, minimumBond)) {
                throw;
            }
            uint nextGenerationId = getNextGenerationId(self);
            if (nextGenerationId == 0) {
                // No next generation has formed yet so create it.
                nextGenerationId = createNextGeneration(self);
            }
            Generation storage nextGeneration = self.generations[nextGenerationId];
            // now add the new address.
            nextGeneration.members.length += 1;
            nextGeneration.members[nextGeneration.members.length - 1] = resourceAddress;
            return nextGenerationId;
        }

        function canExitPool(Pool storage self, address resourceAddress) constant returns (bool) {
            if (!isInCurrentGeneration(self, resourceAddress)) {
                // Not in the pool.
                return false;
            }

            uint nextGenerationId = getNextGenerationId(self);
            if (nextGenerationId == 0) {
                // Next generation hasn't been generated yet.
                return true;
            }

            if (self.generations[nextGenerationId].startAt - self.freezePeriod <= block.number) {
                // Next generation starts too soon.
                return false;
            }

            // They can leave if they are still in the next generation.
            // otherwise they have already left it.
            return isInNextGeneration(self, resourceAddress);
        }

        function exitPool(Pool storage self, address resourceAddress) public returns (uint) {
            if (!canExitPool(self, resourceAddress)) {
                throw;
            }
            uint nextGenerationId = getNextGenerationId(self);
            if (nextGenerationId == 0) {
                // No next generation has formed yet so create it.
                nextGenerationId = createNextGeneration(self);
            }
            // Remove them from the generation
            removeFromGeneration(self, nextGenerationId, resourceAddress);
            return nextGenerationId;
        }

        function removeFromGeneration(Pool storage self, uint generationId, address resourceAddress) public returns (bool){
            Generation storage generation = self.generations[generationId];
            // now remove the address
            for (uint i = 0; i < generation.members.length; i++) {
                if (generation.members[i] == resourceAddress) {
                    generation.members[i] = generation.members[generation.members.length - 1];
                    generation.members.length -= 1;
                    return true;
                }
            }
            return false;
        }

        /*
         *  Bonding
         */

        function deductFromBond(Pool storage self, address resourceAddress, uint value) public {
                /*
                 *  deduct funds from a bond value without risk of an
                 *  underflow.
                 */
                if (value > self.bonds[resourceAddress]) {
                        // Prevent Underflow.
                        throw;
                }
                self.bonds[resourceAddress] -= value;
        }

        function addToBond(Pool storage self, address resourceAddress, uint value) public {
                /*
                 *  Add funds to a bond value without risk of an
                 *  overflow.
                 */
                if (self.bonds[resourceAddress] + value < self.bonds[resourceAddress]) {
                        // Prevent Overflow
                        throw;
                }
                self.bonds[resourceAddress] += value;
        }

        function withdrawBond(Pool storage self, address resourceAddress, uint value, uint minimumBond) public {
                /*
                 *  Only if you are not in either of the current call pools.
                 */
                // Prevent underflow
                if (value > self.bonds[resourceAddress]) {
                        throw;
                }

                // Do a permissions check to be sure they can withdraw the
                // funds.
                if (isInPool(self, resourceAddress)) {
                        if (self.bonds[resourceAddress] - value < minimumBond) {
                            return;
                        }
                }

                deductFromBond(self, resourceAddress, value);
                if (!resourceAddress.send(value)) {
                        // Potentially sending money to a contract that
                        // has a fallback function.  So instead, try
                        // tranferring the funds with the call api.
                        if (!resourceAddress.call.gas(msg.gas).value(value)()) {
                                // Revert the entire transaction.  No
                                // need to destroy the funds.
                                throw;
                        }
                }
        }
}
