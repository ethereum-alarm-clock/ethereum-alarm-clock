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

    uint constant _MAX_STACK_DEPTH_REQUIREMENT = 1000;

    function MAX_STACK_DEPTH_REQUIREMENT() returns (uint) {
        return _MAX_STACK_DEPTH_REQUIREMENT;
    }

    /*
     * Validation: ensure that the required stack depth is not above the
     * MAX_STACK_DEPTH_REQUIREMENT
     */
    function validateRequiredStackDepth(uint requiredStackDepth) returns (bool) {
        return requiredStackDepth <= _MAX_STACK_DEPTH_REQUIREMENT;
    }

    /*
     * Returns the maximum possible gas consumption that a transaction request
     * may consume.  The EXTRA_GAS value represents the overhead involved in
     * request execution.
     */
    function CALL_GAS_CEILING(uint EXTRA_GAS) returns (uint) {
        return block.gaslimit - EXTRA_GAS;
    }

    /*
     * Validation: ensure that the callGas is not above the total possible gas
     * for a call.
     */
     function validateCallGas(uint callGas, uint EXTRA_GAS) returns (bool) {
         return callGas < CALL_GAS_CEILING(EXTRA_GAS);
     }

    /*
     * Validation: ensure that the toAddress is not set to the empty address.
     */
     function validateToAddress(address toAddress) returns (bool) {
         return toAddress != 0x0;
     }
}
