pragma solidity 0.4.24;

/**
 * @title ExecutionLib
 * @dev Contains the logic for executing a scheduled transaction.
 */
library ExecutionLib {

    struct ExecutionData {
        address toAddress;                  /// The destination of the transaction.
        bytes callData;                     /// The bytecode that will be sent with the transaction.
        uint callValue;                     /// The wei value that will be sent with the transaction.
        uint callGas;                       /// The amount of gas to be sent with the transaction.
        uint gasPrice;                      /// The gasPrice that should be set for the transaction.
    }

    /**
     * @dev Send the transaction according to the parameters outlined in ExecutionData.
     * @param self The ExecutionData object.
     */
    function sendTransaction(ExecutionData storage self)
        internal returns (bool)
    {
        /// Should never actually reach this require check, but here in case.
        require(self.gasPrice <= tx.gasprice);
        /* solium-disable security/no-call-value */
        return self.toAddress.call.value(self.callValue).gas(self.callGas)(self.callData);
    }


    /**
     * Returns the maximum possible gas consumption that a transaction request
     * may consume.  The EXTRA_GAS value represents the overhead involved in
     * request execution.
     */
    function CALL_GAS_CEILING(uint EXTRA_GAS) 
        internal view returns (uint)
    {
        return block.gaslimit - EXTRA_GAS;
    }

    /*
     * @dev Validation: ensure that the callGas is not above the total possible gas
     * for a call.
     */
    function validateCallGas(uint callGas, uint EXTRA_GAS)
        internal view returns (bool)
    {
        return callGas < CALL_GAS_CEILING(EXTRA_GAS);
    }

    /*
     * @dev Validation: ensure that the toAddress is not set to the empty address.
     */
    function validateToAddress(address toAddress)
        internal pure returns (bool)
    {
        return toAddress != 0x0;
    }
}
