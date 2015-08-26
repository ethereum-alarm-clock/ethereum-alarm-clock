contract AlarmAPI {
        function scheduleCall(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {}
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
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), dataHash, block.number + 100);
        }
}


contract Fails {
        bool public value;
        bytes32 public dataHash;

        function doIt() public {
                uint[] x;
                x[1];
        }

        function scheduleIt(address to) public {
                dataHash = sha3();
                to.call(bytes4(sha3("registerData()")));

                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(address(this), bytes4(sha3("doIt()")), dataHash, block.number + 100);
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
                alarm.scheduleCall(address(this), bytes4(sha3("doIt(uint256)")), dataHash, block.number + 100);
        }
}
