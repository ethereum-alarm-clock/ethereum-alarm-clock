contract AlarmAPI {
        function scheduleCall(bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {}
}

contract Trigger {
        uint public value;
        bytes32 public dataHash;

        function doIt(uint a) public {
                value = a;
        }

        function scheduleIt(address to, uint a) public {
                dataHash = sha3(a);
                to.call(bytes4(sha3("registerData()")), a);
                AlarmAPI alarm = AlarmAPI(to);
                alarm.scheduleCall(bytes4(sha3("doIt(uint256)")), dataHash, block.number + 100);
        }
}
