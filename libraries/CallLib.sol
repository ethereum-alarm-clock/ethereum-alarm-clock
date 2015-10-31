contract AlarmAPI {
        function getDesignatedCaller(uint leftBound, uint RightBound) returns (bool, address) {
                // 1. there is a generation for this window.
                // 2. that generation is non-empty.
        }
}


library CallLib {
        function registerData(bytes data) public returns (bytes callData){
            callData.length = data.length - 4;
            if (data.length > 4) {
                    for (uint i = 0; i < callData.length; i++) {
                            callData[i] = data[i + 4];
                    }
            }
            return callData;
        }

        function sendSafe(address toAddress, uint value) internal {
                if (value > address(this).balance) {
                        value = address(this).balance;
                }
                if (value > 0) {
                        AccountingLib.sendRobust(toAddress, value);
                }
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
}


contract FutureCall {
        address public schedulerAddress;
        address public contractAddress;

        AlarmAPI alarm;

        uint public anchorGasPrice;
        uint public suggestedGas;

        uint public reward;
        
        bytes4 public abiSignature;
        bytes public callData;

        function registerData() public onlyscheduler {
                callData = CallLib.registerData(msg.data);
        }

        function () {
                // Fallback to allow sending funds to this contract.
        }

        modifier onlyscheduler { if (msg.sender == schedulerAddress) _ }

        // The author (Piper Merriam) address.
        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        // API for inherited contracts
        function beforeExecute(address executor) internal returns (bool);
        function logExecution(address executor) internal;
        function afterExecute(address executor) internal;
        function getOverhead() constant returns (uint);
        function getExtraGas() constant returns (uint);
        function getPayment() constant returns (uint);
        function getFee() constant returns (uint);

        event CallAborted(address executor, bytes32 reason);

        function sendSafe(address toAddress, uint value) internal {
                CallLib.sendSafe(toAddress, value);
        }

        function execute(address executor) public {
            uint gasBefore = msg.gas;

            // The before execute function is where all pre-call validation
            // needs to occur.
            if (!beforeExecute(executor)) {
                return;
            }

            // Make the call
            bool success = contractAddress.call.gas(msg.gas - getOverhead())(abiSignature, callData);

            // Compute the scalar (0 - 200) for the fee.
            uint feeScalar = CallLib.getCallFeeScalar(anchorGasPrice, msg.gasprice);

            uint payment = getPayment() * feeScalar / 100; 
            uint fee = getFee() * feeScalar / 100;

            logExecution(executor, payment, fee, success);
            // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
            // amount that represents the gas usage of the commands that
            // happen after this line.
            uint gasCost = msg.gasprice * (gasBefore - msg.gas + getExtraGas());

            // Now we need to pay the executor as well as keep fee.
            sendSafe(executor, payment + gasCost);
            sendSafe(creator, fee);

            // Any logic that needs to occur after the call has executed should
            // go in afterExecute
            afterExecute(executor);
        }

        event Cancelled(address indexed cancelledBy);

        function cancel(address sender) onlyscheduler {
                Cancelled(sender);
                suicide(sender);
        }
}


contract FutureBlockCall is FutureCall {
        uint public targetBlock;
        uint8 public gracePeriod;

        uint public basePayment;
        uint public baseFee;
        
        function FutureBlockCall(address alarmAddress, address _schedulerAddress, uint _targetBlock, uint8 _gracePeriod, address _contractAddress, bytes4 _abiSignature, uint _suggestedGas, uint _basePayment, uint _baseFee) {
                alarm = AlarmAPI(alarmAddress);

                schedulerAddress = _schedulerAddress;

                targetBlock = _targetBlock;
                gracePeriod = _gracePeriod;

                anchorGasPrice = tx.gasprice;
                suggestedGas = _suggestedGas;

                basePayment = _basePayment;
                baseFee = _baseFee;

                contractAddress = _contractAddress;
                abiSignature = _abiSignature;
        }

        function getPayment() constant returns (uint) {
                return basePayment;
        }

        function getFee() constant returns (uint) {
                return baseFee;
        }

        function beforeExecute(address executor) internal {
                // Need to do do all the before-call validation.
        }

        event CallExecuted(address indexed executor, uint payment);

        function logExecution(address executor, uint payment) internal {
                CallExecuted(executor, payment);
        }

        function afterExecute(address executor) internal {
            suicide(schedulerAddress);
        }

        function getOverhead() returns (uint) {
                // TODO
                return 200000;
        }

        function getExtraGas() returns (uint) {
                // TODO
                return 100000;
        }
}

