import "owned";


contract DataRegistry is owned {
        bytes lastData;
        uint lastDataLength;
        bytes32 lastDataHash;

        function getLastDataHash() public returns (bytes32) {
                return lastDataHash;
        }

        function getLastDataLength() public returns (uint) {
                return lastDataLength;
        }

        function getLastData() public returns (bytes) {
                return lastData;
        }

        mapping (bytes32 => bytes) hash_to_data;

        /*
         *  Main Alarm API
         */
        event DataRegistered(address registeredBy, bytes32 dataHash, bytes data);

        function registerData() public {
                bytes trunc;
                if (msg.data.length > 4) {
                        trunc.length = msg.data.length - 4;
                        for (uint i = 0; i < trunc.length; i++) {
                                trunc[trunc.length - 1 - i] = msg.data[msg.data.length - 1 - i];
                        }
                }
                hash_to_data[sha3(trunc)] = trunc;
                lastDataHash = sha3(trunc);
                lastDataLength = trunc.length;
                lastData = trunc;
                DataRegistered(msg.sender, lastDataHash, lastData);
        }
}
