contract TestDataRegistry {
        uint8 public wasSuccessful = 0;

        function reset() public {
            wasSuccessful = 0;
        }

        function registerUInt(address to, uint v) public {
            bool result = to.call(bytes4(sha3("register_data()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerInt(address to, int v) public {
            bool result = to.call(bytes4(sha3("register_data()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerBytes32(address to, bytes32 v) public {
            bool result = to.call(bytes4(sha3("register_data()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerBytes(address to, bytes v) public {
            bool result = to.call(bytes4(sha3("register_data()")), v.length, v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerAddress(address to, address v) public {
            bool result = to.call(bytes4(sha3("register_data()")), v);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function registerMany(address to, uint a, int b, uint c, bytes20 d, address e, bytes f) public {
            bool result = to.call(bytes4(sha3("register_data()")), a, b, c, d, e, f.length, f);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function register_data(address to, int arg1, bytes32 arg2, address arg3) public {
            // 0xb0f07e44 == bytes4(sha3("register_data()"))
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
        uint8 public wasSuccessful;

        function doExecution(address to, address callAddress) {
            bool result = to.call(bytes4(sha3("execute()")), callAddress);
            if (result) {
                wasSuccessful = 1;
            }
            else {
                wasSuccessful = 2;
            }
        }

        function doLoops(uint iterations) {
            for (uint i = 0; i < iterations; i++) {
                address(this).send(1);
            }
        }

        bool public v_bool;

        function setBool() public {
            v_bool = true;
        }

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

        function doInfinite() public {
                while (true) {
                        tx.origin.send(1);
                }
                value = true;
        }
}
