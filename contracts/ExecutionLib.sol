//pragma solidity 0.4.1;


library ExecutionLib {
    struct ExecutionData {
        // The address that the txn will be sent to.
        address toAddress;

        // The bytes value that will be sent with the txn.
        bytes callData;

        // The value in wei that will be sent with the txn.
        uint callValue;

        // The amount of gas that will be sent with the txn
        uint callGas;

        // The stack depth this txn requires.
        uint requiredStackDepth;
    }

    function sendTransaction(ExecutionData storage self) returns (bool) {
        return self.toAddress.call.value(self.callValue)
                                  .gas(self.callGas)
                                  (self.callData);
    }

    uint constant _GAS_PER_DEPTH = 700;

    function GAS_PER_DEPTH() returns (uint) {
        return _GAS_PER_DEPTH;
    }

    /*
     *  Verifies that the stack can currently be extended by the
     *  `requiredStackDepth`.  For this function to work, the contract calling
     *  this library function must have implemented the interface found in the
     *  `contracts/Digger.sol` contract.
     */
    function stackCanBeExtended(ExecutionData storage self) returns (bool) {
        if (self.requiredStackDepth == 0) return true;
        return address(this).call
                            .gas(_GAS_PER_DEPTH * self.requiredStackDepth)
                            (
                                bytes4(sha3("__dig(uint256)")),
                                self.requiredStackDepth - 1
                            );
    }
}
