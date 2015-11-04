library CallLib {
        struct Call {
                address contractAddress;
                bytes4 abiSignature;
                bytes callData;
                uint anchorGasPrice;
                uint suggestedGas;
        }

        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function extractCallData(Call storage call, bytes data) public {
            if (call.callData.length > 0) {
                    // cannot write over call dat
                    throw;
            }
            call.callData.length = data.length - 4;
            if (data.length > 4) {
                    for (uint i = 0; i < call.callData.length; i++) {
                            call.callData[i] = data[i + 4];
                    }
            }
        }

        function sendSafe(address toAddress, uint value) public {
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

        event CallExecuted(address indexed executor, uint payment, uint fee, bool success);

        function logExecution(address executor, uint payment, uint fee, bool success) public {
                CallExecuted(executor, payment, fee, success);
        }

        function execute(Call storage call, uint startGas, address executor, uint basePayment, uint baseFee, uint overhead, uint extraGas) public {
            // Make the call
            bool success = call.contractAddress.call.gas(msg.gas - overhead)(call.abiSignature, call.callData);

            // Compute the scalar (0 - 200) for the fee.
            uint feeScalar = getCallFeeScalar(call.anchorGasPrice, tx.gasprice);

            uint payment = basePayment * feeScalar / 100; 
            uint fee = baseFee * feeScalar / 100;

            logExecution(executor, payment, fee, success);
            // Log how much gas this call used.  EXTRA_CALL_GAS is a fixed
            // amount that represents the gas usage of the commands that
            // happen after this line.
            uint gasCost = tx.gasprice * (startGas - msg.gas + extraGas);

            // Now we need to pay the executor as well as keep fee.
            sendSafe(executor, payment + gasCost);
            sendSafe(creator, fee);
        }

        event Cancelled(address indexed cancelledBy);

        function cancel(address sender) public {
                Cancelled(sender);
                suicide(sender);
        }
}


contract FutureCall {
        address public owner;
        address public schedulerAddress;

        uint public basePayment;
        uint public baseFee;

        CallLib.Call call;

        function contractAddress() constant returns (address) {
                return call.contractAddress;
        }

        function abiSignature() constant returns (bytes4) {
                return call.abiSignature;
        }

        function callData() constant returns (bytes) {
                return call.callData;
        }

        function anchorGasPrice() constant returns (uint) {
                return call.anchorGasPrice;
        }

        function suggestedGas() constant returns (uint) {
                return call.suggestedGas;
        }

        function () {
                // Fallback to allow sending funds to this contract.
        }

        modifier onlyscheduler { if (msg.sender == schedulerAddress) _ }

        // The author (Piper Merriam) address.
        address constant creator = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

        function registerData() public {
                CallLib.extractCallData(call, msg.data);
        }

        // API for inherited contracts
        function beforeExecute(address executor) constant returns (bool);
        function afterExecute(address executor) internal;
        function getOverhead() constant returns (uint);
        function getExtraGas() constant returns (uint);

        event CallAborted(address executor, bytes32 reason);

        function sendSafe(address toAddress, uint value) internal {
                CallLib.sendSafe(toAddress, value);
        }

        modifier onlyowner { if (msg.sender == owner) _ }

        function execute() public onlyowner {
                uint startGas = msg.gas;
                execute(startGas,  msg.sender);
        }

        function execute(uint startGas, address executor) public onlyowner {
            CallLib.execute(call, startGas, executor, basePayment, baseFee, getOverhead(), getExtraGas());

            // Any logic that needs to occur after the call has executed should
            // go in afterExecute
            afterExecute(executor);
        }

        event Cancelled(address indexed cancelledBy);

        function cancel(address sender) public onlyscheduler {
                CallLib.cancel(sender);
        }
}


contract FutureBlockCall is FutureCall {
        uint public targetBlock;
        uint8 public gracePeriod;
        
        function FutureBlockCall(address _schedulerAddress, uint _targetBlock, uint8 _gracePeriod, address _contractAddress, bytes4 _abiSignature, uint _suggestedGas, uint _basePayment, uint _baseFee) {
                owner = msg.sender;

                schedulerAddress = _schedulerAddress;

                targetBlock = _targetBlock;
                gracePeriod = _gracePeriod;


                basePayment = _basePayment;
                baseFee = _baseFee;

                call.suggestedGas = _suggestedGas;
                call.anchorGasPrice = tx.gasprice;
                call.contractAddress = _contractAddress;
                call.abiSignature = _abiSignature;
        }

        function beforeExecute(address executor) constant returns (bool) {
                if (block.number < targetBlock || block.number > targetBlock + gracePeriod) {
                        // Not being called within call window.
                        return false;
                }

                return true;
        }

        function afterExecute(address executor) internal {
            suicide(schedulerAddress);
        }

        function getOverhead() constant returns (uint) {
                // TODO
                return 200000;
        }

        function getExtraGas() constant returns (uint) {
                // TODO
                return 100000;
        }
}

