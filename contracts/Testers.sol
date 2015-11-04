contract AlarmTestAPI {
        // account functiosn
        function withdraw(uint value) public;
        function getAccountBalance(address account) public returns (uint);

        // call scheduling
        function scheduleCall(address contractAddress, bytes4 signature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public;

        // Pool functions
        function depositBond() public;
        function enterPool() public;
        function exitPool() public;
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

        function registerBytes32(address to, bytes32 v) public {
            bool result = to.call(bytes4(sha3("registerData()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerBytes(address to, bytes v) public {
            bool result = to.call(bytes4(sha3("setBytes(bytes)")), v);
            //bool result = to.call(bytes4(sha3("registerData()")), v);
            //bool result = to.call(v);
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

        function registerMany(address to, uint a, int b, uint c, bytes20 d, address e, bytes f) public {
            bool result = to.call(bytes4(sha3("setMany(uint256,int256,uint256,bytes20,address,bytes)")), a, b, c, d, e, f);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerData(address to, int arg1, bytes32 arg2, address arg3) public {
            // 0xb0f07e44 == bytes4(sha3("registerData()"))
            bool result = to.call(0xb0f07e44, arg1, arg2, arg3);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }
}


contract TestCallExecution {
        uint public v_uint;

        function setUInt(uint v) public {
            v_uint = v;
        }

        int public v_int;

        function setInt(int v) public {
            v_int = v;
        }

        address public v_address;

        function setAddress(address v) public {
            v_address = v;
        }

        bytes32 public v_bytes32;

        function setBytes32(bytes32 v) public {
            v_bytes32 = v;
        }

        bytes public v_bytes;

        function setBytes(bytes v) public {
            Bytes(v);
            Bytes(msg.data);
            v_bytes = v;
        }

        uint public vm_a;
        int public vm_b;
        uint public vm_c;
        bytes20 public vm_d;
        address public vm_e;
        bytes public vm_f;

        event Bytes(bytes f);

        function setMany(uint a, int b, uint c, bytes20 d, address e, bytes f) public {
            Bytes(f);
            Bytes(msg.data);
            vm_a = a;
            vm_b = b;
            vm_c = c;
            vm_d = d;
            vm_e = e;
            vm_f = f;
        }
}


contract TestErrors {
        bool public value;

        function doFail() public {
                throw;
                value = true;
        }

        function scheduleFail(address to) public {
                //  TODO: convert to use scheduler
                AlarmTestAPI alarm = AlarmTestAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doFail()")), sha3(), block.number + 40, 255, 0);
        }

        function doInfinite() public {
                while (true) {
                        tx.origin.send(1);
                }
                value = true;
        }

        function scheduleInfinite(address to) public {
                //  TODO: convert to use scheduler
                AlarmTestAPI alarm = AlarmTestAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doInfinite()")), sha3(), block.number + 40, 255, 0);
        }
}


contract WithdrawsDuringCall {
        /*
         *  Used to test that the funds of an account are locked during the
         *  function call to prevent withdrawing funds that are about to be
         *  used to pay the caller.
         */
        AlarmTestAPI alarm;
        uint public withdrawAmount;

        function WithdrawsDuringCall(address alarmAddress) {
                alarm = AlarmTestAPI(alarmAddress);
        }

        function getAlarmBalance() public returns (uint) {
                return alarm.getAccountBalance(address(this));
        }

        bool public wasCalled;

        function doIt() public {
                wasCalled = true;
                withdrawAmount = getAlarmBalance();
        }

        function scheduleIt() public {
                address(alarm).call(bytes4(sha3("registerData()")));
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), sha3(), block.number + 40, 255, 0);
        }
}


contract JoinsPool {
        AlarmTestAPI alarm;

        function setCallerPool(address to) public {
                alarm = AlarmTestAPI(to);
        }

        function deposit(uint value) public {
                alarm.depositBond.value(value)();
        }

        function enter() public {
                alarm.enterPool();
        }

        function exit() public {
                alarm.exitPool();
        }
}
