contract MasterAPI {
        function checkIfDesignated(uint leftBound, uint RightBound) {
                // 1. there is a generation for this window.
                // 2. that generation is non-empty.
        }
}

contract ScheduledBlockCall {
        address public owner;
        address public contractAddress;

        MasterAPI master;
        
        uint public targetBlock;
        uint8 public gracePeriod;
        
        uint public baseGasPrice;
        
        bytes4 public abiSignature;
        bytes public callData;

        // The author (Piper Merriam) address.
        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        // TODO: variable reward.

        function ScheduledCall(address _master, address _owner, uint _targetBlock, uint8 _gracePeriod, address _contractAddress, bytes4 _abiSignature, bytes _callData) {
                master = MasterAPI(_master);
                owner = _owner;

                targetBlock = _targetBlock;
                gracePeriod = _gracePeriod;

                contractAddress = _contractAddress;
                abiSignature = _abiSignature;
                callData = _callData;
        }

        event CallAborted(address caller, bytes32 reason);

        function execute() public {
            uint gasBefore = msg.gas;

            if (block.number < targetBlock) {
                    // Target block hasnt happened yet.
                    CallAborted(msg.sender, "TOO EARLY");
                    return;
            }

            if (block.number > targetBlock + gracePeriod) {
                    // The blockchain has advanced passed the period where
                    // it was allowed to be called.
                    CallAborted(msg.sender, "TOO LATE");
                    return;
            }

            // Check if this caller is allowed to execute the call.
            if (master.checkIfDesignated(targetBlock, targetBlock + gracePeriod) {
                    address designatedCaller = getDesignatedCaller(targetBlock, targetBlock + gracePeriod, block.number);
                    if (designatedCaller != 0x0 && designatedCaller != msg.sender) {
                            // This call was reserved for someone from the
                            // bonded pool of callers and can only be
                            // called by them during this block window.
                            CallAborted(msg.sender, "WRONG_CALLER");
                            return;
                    }

                    uint blockWindow = (block.number - call.targetBlock) / CALL_WINDOW_SIZE;
                    if (blockWindow > 0) {
                            // Someone missed their call so this caller
                            // gets to claim their bond for picking up
                            // their slack.
                            awardMissedBlockBonus(self, msgSender, callKey);
                    }
            }

            // Log metadata about the call.
            call.gasPrice = tx.gasprice;
            call.executedBy = msgSender;
            call.calledAtBlock = block.number;

            // Fetch the call data
            var data = self.data_registry[call.dataHash];

            // During the call, we need to put enough funds to pay for the
            // call on hold to ensure they are available to pay the caller.
            AccountingLib.withdraw(self.gasBank, call.scheduledBy, heldBalance);

            // Mark whether the function call was successful.
            if (checkAuthorization(self, call.scheduledBy, call.contractAddress)) {
                    call.wasSuccessful = self.authorizedRelay.relayCall.gas(msg.gas - CALL_OVERHEAD)(call.contractAddress, call.abiSignature, data);
            }
            else {
                    call.wasSuccessful = self.unauthorizedRelay.relayCall.gas(msg.gas - CALL_OVERHEAD)(call.contractAddress, call.abiSignature, data);
            }

            // Add the held funds back into the scheduler's account.
            AccountingLib.deposit(self.gasBank, call.scheduledBy, heldBalance);

            // Mark the call as having been executed.
            call.wasCalled = true;

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

            AccountingLib.deductFunds(self.gasBank, call.scheduledBy, call.payout + call.fee);

            AccountingLib.addFunds(self.gasBank, msgSender, call.payout);
            AccountingLib.addFunds(self.gasBank, owner, call.fee);
}
