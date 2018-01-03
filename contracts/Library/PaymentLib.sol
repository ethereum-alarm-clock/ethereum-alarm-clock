pragma solidity ^0.4.18;

import "contracts/Library/ExecutionLib.sol";
import "contracts/Library/MathLib.sol";
import "contracts/zeppelin/SafeMath.sol";

library PaymentLib {
    using SafeMath for uint;

    struct PaymentData {
        uint payment;               /// The amount in wei to be paid to the executor of this TransactionRequest.

        address paymentBenefactor;  /// The address that the payment should be sent to.

        uint paymentOwed;           /// The amount that is owed to the paymentBenefactor.

        uint donation;              /// The amount in wei that will be paid to the donationBenefactor address.

        address donationBenefactor; /// The address that the donation should be sent to.

        uint donationOwed;          /// The amount that is owed to the donationBenefactor.
    }

    ///---------------
    /// GETTERS
    ///---------------

    /**
     * @dev Getter function that returns true if a request has a benefactor.
     */
    function hasBenefactor(PaymentData storage self)
        internal view returns (bool)
    {
        return self.donationBenefactor != 0x0;
    }

    /**
     * @dev Computes the amount to send to the donationBenefactor. 
     */
    function getDonation(PaymentData storage self) 
        internal view returns (uint)
    {
        return self.donation;
    }

    /**
     * @dev Computes the amount to send to the address that fulfilled the request.
     */
    function getPayment(PaymentData storage self)
        internal view returns (uint)
    {
        return self.payment;
    }
 
    /**
     * @dev Computes the amount to send to the address that fulfilled the request
     *       with an additional modifier. This is used when the call was claimed.
     */
    function getPaymentWithModifier(PaymentData storage self,
                                    uint8 _paymentModifier)
        internal view returns (uint)
    {
        return getPayment(self).mul(_paymentModifier).div(100);
    }

    ///---------------
    /// SENDERS
    ///---------------

    /**
     * @dev Send the donationOwed amount to the donationBenefactor.
     * Note: The send is allowed to fail.
     */
    function sendDonation(PaymentData storage self) 
        internal returns (bool)
    {
        uint donationAmount = self.donationOwed;
        if (donationAmount > 0) {
            // re-entrance protection.
            self.donationOwed = 0;
            return self.donationBenefactor.send(donationAmount);
        }
        return true;
    }

    /**
     * @dev Send the paymentOwed amount to the paymentBenefactor.
     * Note: The send is allowed to fail.
     */
    function sendPayment(PaymentData storage self)
        internal returns (bool)
    {
        uint paymentAmount = self.paymentOwed;
        if (paymentAmount > 0) {
            // re-entrance protection.
            self.paymentOwed = 0;
            return self.paymentBenefactor.send(paymentAmount);
        }
        return true;
    }

    ///---------------
    /// HELPERS
    ///---------------

    /**
     * @dev Compute the endowment value for the given TransactionRequest parameters.
     * See request_factory.rst in docs folder under Check #1 for more information about
     * this calculation.
     */
    function computeEndowment(
        uint _payment,
        uint _donation,
        uint _callGas,
        uint _callValue,
        uint _gasPrice,
        uint _gasOverhead
    ) 
        internal pure returns (uint)
    {
        return _payment
                .add(_donation).mul(2)
                .add(_computeHelper(_callGas, _callValue, _gasOverhead, _gasPrice));
    }

    /// Was getting a stack depth error after replacing old MathLib with Zeppelin's SafeMath.
    ///  Added this function to fix it.
    ///  See for context: https://ethereum.stackexchange.com/questions/7325/stack-too-deep-try-removing-local-variables 
    function _computeHelper(
        uint _callGas,
        uint _callValue,
        uint _gasOverhead,
        uint _gasPrice
    )
        internal pure returns (uint)
    {
        return _callGas.mul(_gasPrice)
                        .add(_gasOverhead.mul(_gasPrice))
                        .add(_callValue);
    }
    /*
     * Validation: ensure that the request endowment is sufficient to cover.
     * - payment * maxMultiplier
     * - donation * maxMultiplier
     * - gasReimbursment
     * - callValue
     */
    function validateEndowment(uint _endowment,
                               uint _payment,
                               uint _donation,
                               uint _callGas,
                               uint _callValue,
                               uint _gasPrice,
                               uint _gasOverhead)
        public pure returns (bool)
    {
        return _endowment >= computeEndowment(
            _payment,
            _donation,
            _callGas,
            _callValue,
            _gasPrice,
            _gasOverhead
        );
    }
}
