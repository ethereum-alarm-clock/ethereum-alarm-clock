contract AlarmAPI {
        function withdraw(uint value) public;
        function accountBalances(address account) public returns (uint);
        function scheduleCall(address to, bytes4 signature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod) public returns (bytes32);
}


contract TestDataRegistry {
        uint8 public wasSuccessful = 0;

        function registerUInt(address to, uint v) public {
            bool result = to.call(bytes4(sha3("registerData()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerInt(address to, int v) public {
            bool result = to.call(bytes4(sha3("registerData()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerBytes(address to, bytes32 v) public {
            bool result = to.call(bytes4(sha3("registerData()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerAddress(address to, address v) public {
            bool result = to.call(bytes4(sha3("registerData()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }
}


contract NoArgs {
        bool public value;
        bytes32 public dataHash;

        function doIt() public {
                value = true;
        }

        function undoIt() public {
                value = false;
        }

        function scheduleIt(address to) public {
                dataHash = sha3();
                to.call(bytes4(sha3("registerData()")));

                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), dataHash, block.number + 100, 255);
        }
}


contract Fails {
        bool public value;
        bytes32 public dataHash;

        function doIt() public {
                int x = 1;
                int y = 0;
                x / y;
        }

        function scheduleIt(address to) public {
                dataHash = sha3();
                to.call(bytes4(sha3("registerData()")));

                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), dataHash, block.number + 100, 255);
        }
}


contract PassesInt {
        int public value;
        bytes32 public dataHash;

        function doIt(int a) public {
                value = a;
        }

        function scheduleIt(address to, int a) public {
                dataHash = sha3(a);
                to.call(bytes4(sha3("registerData()")), a);
                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt(int256)")), dataHash, block.number + 100, 255);
        }
}


contract PassesUInt {
        uint public value;
        bytes32 public dataHash;

        function doIt(uint a) public {
                value = a;
        }

        function scheduleIt(address to, uint a) public {
                dataHash = sha3(a);
                to.call(bytes4(sha3("registerData()")), a);
                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt(uint256)")), dataHash, block.number + 100, 255);
        }
}


contract PassesBytes32 {
        bytes32 public value;
        bytes32 public dataHash;

        function doIt(bytes32 a) public {
                value = a;
        }

        function scheduleIt(address to, bytes32 a) public {
                dataHash = sha3(a);
                to.call(bytes4(sha3("registerData()")), a);
                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt(bytes32)")), dataHash, block.number + 100, 255);
        }
}


contract PassesAddress {
        address public value;
        bytes32 public dataHash;
        bytes public data;

        function doIt(address a) public {
                value = a;
                data = msg.data;
        }

        function scheduleIt(address to, address a) public {
                dataHash = sha3(bytes32(a));
                to.call(bytes4(sha3("registerData()")), a);
                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt(address)")), dataHash, block.number + 100, 255);
        }
}


contract CancelsCall {
        function doIt() public {
        }

        function cancelIt(address to, bytes32 callKey) public {
                to.call(bytes4(sha3("cancelCall(bytes32)")), callKey);
        }

        function scheduleIt(address to) public {
                to.call(bytes4(sha3("registerData()")));

                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), sha3(), block.number + 100, 255);
        }
}


contract WithdrawsDuringCall {
        /*
         *  Used to test that the funds of an account are locked during the
         *  function call to prevent withdrawing funds that are about to be
         *  used to pay the caller.
         */
        AlarmAPI alarm;
        uint public withdrawAmount;

        function setAlarm(address alarmAddress) public {
                alarm = AlarmAPI(alarmAddress);
        }

        function getAlarmBalance() returns (uint) {
                return alarm.accountBalances(address(this));
        }

        bool public wasCalled;

        function doIt() public {
                wasCalled = true;
                withdrawAmount = getAlarmBalance();
                alarm.withdraw(withdrawAmount);
        }

        function scheduleIt() public {
                address(alarm).call(bytes4(sha3("registerData()")));
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), sha3(), block.number + 100, 255);
        }
}


contract DepositsFunds {
        uint public sentSuccessful;

        function doIt(address a, uint value) public {
                bool result = a.call.value(value)(bytes4(sha3("deposit(address)")), address(this));
                if (result) {
                        sentSuccessful = 1;
                }
                else {
                        sentSuccessful = 2;
                }
        }
}


contract SpecifyBlock {
        bool public value;

        function doIt() public {
                value = true;
        }

        function scheduleIt(address to, uint blockNumber) public {
                to.call(bytes4(sha3("registerData()")), block.timestamp);

                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), sha3(block.timestamp), blockNumber, 255);
        }
}


contract AuthorizesOthers {
        function doIt() public {
        }

        function authorize(address to) public {
                to.call(bytes4(sha3("addAuthorization(address)")), msg.sender);
        }

        function unauthorize(address to) public {
                to.call(bytes4(sha3("removeAuthorization(address)")), msg.sender);
        }

        function scheduleIt(address to, uint blockNumber) public {
                to.call(bytes4(sha3("registerData()")), block.timestamp);

                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), sha3(), block.number + 100, 255);
        }
}
