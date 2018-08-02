pragma solidity 0.4.24;

import "contracts/zeppelin/SafeMath.sol";

/**
 * Library containing the functionality for the bounty and fee payments.
 * - Bounty payments are the reward paid to the executing agent of transaction
 * requests.
 * - Fee payments are the cost of using a Scheduler to make transactions. It is 
 * a way for developers to monetize their work on the EAC.
 */
library PaymentLib {
    using SafeMath for uint;

    struct PaymentData {
        uint bounty;                /// The amount in wei to be paid to the executing agent of the TransactionRequest.

        address bountyBenefactor;   /// The address that the bounty will be sent to.

        uint bountyOwed;            /// The amount that is owed to the bountyBenefactor.

        uint fee;                   /// The amount in wei that will be paid to the FEE_RECIPIENT address.

        address feeRecipient;       /// The address that the fee will be sent to.

        uint feeOwed;               /// The amount that is owed to the feeRecipient.
    }

    ///---------------
    /// GETTERS
    ///---------------

    /**
     * @dev Getter function that returns true if a request has a benefactor.
     */
    function hasFeeRecipient(PaymentData storage self)
        internal view returns (bool)
    {
        return self.feeRecipient != 0x0;
    }

    /**
     * @dev Computes the amount to send to the feeRecipient. 
     */
    function getFee(PaymentData storage self) 
        internal view returns (uint)
    {
        return self.fee;
    }

    /**
     * @dev Computes the amount to send to the agent that executed the request.
     */
    function getBounty(PaymentData storage self)
        internal view returns (uint)
    {
        return self.bounty;
    }
 
    /**
     * @dev Computes the amount to send to the address that fulfilled the request
     *       with an additional modifier. This is used when the call was claimed.
     */
    function getBountyWithModifier(PaymentData storage self, uint8 _paymentModifier)
        internal view returns (uint)
    {
        return getBounty(self).mul(_paymentModifier).div(100);
    }

    ///---------------
    /// SENDERS
    ///---------------

    /**
     * @dev Send the feeOwed amount to the feeRecipient.
     * Note: The send is allowed to fail.
     */
    function sendFee(PaymentData storage self) 
        internal returns (bool)
    {
        uint feeAmount = self.feeOwed;
        if (feeAmount > 0) {
            // re-entrance protection.
            self.feeOwed = 0;
            /* solium-disable security/no-send */
            return self.feeRecipient.send(feeAmount);
        }
        return true;
    }

    /**
     * @dev Send the bountyOwed amount to the bountyBenefactor.
     * Note: The send is allowed to fail.
     */
    function sendBounty(PaymentData storage self)
        internal returns (bool)
    {
        uint bountyAmount = self.bountyOwed;
        if (bountyAmount > 0) {
            // re-entrance protection.
            self.bountyOwed = 0;
            return self.bountyBenefactor.send(bountyAmount);
        }
        return true;
    }

    ///---------------
    /// Endowment
    ///---------------

    /**
     * @dev Compute the endowment value for the given TransactionRequest parameters.
     * See request_factory.rst in docs folder under Check #1 for more information about
     * this calculation.
     */
    function computeEndowment(
        uint _bounty,
        uint _fee,
        uint _callGas,
        uint _callValue,
        uint _gasPrice,
        uint _gasOverhead
    ) 
        public pure returns (uint)
    {
        return _bounty
            .add(_fee)
            .add(_callGas.mul(_gasPrice))
            .add(_gasOverhead.mul(_gasPrice))
            .add(_callValue);
    }

    /*
     * Validation: ensure that the request endowment is sufficient to cover.
     * - bounty
     * - fee
     * - gasReimbursment
     * - callValue
     */
    function validateEndowment(uint _endowment, uint _bounty, uint _fee, uint _callGas, uint _callValue, uint _gasPrice, uint _gasOverhead)
        public pure returns (bool)
    {
        return _endowment >= computeEndowment(
            _bounty,
            _fee,
            _callGas,
            _callValue,
            _gasPrice,
            _gasOverhead
        );
    }
}
