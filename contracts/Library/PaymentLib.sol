pragma solidity ^0.4.18;

import "contracts/Library/ExecutionLib.sol";
import "contracts/Library/MathLib.sol";
import "contracts/zeppelin/SafeMath.sol";

library PaymentLib {
    using SafeMath for uint;

    struct PaymentData {
        uint payment;               /// The amount in wei to be paid to the executor of this TransactionRequest.

        address paymentBenefactor;  /// The address that the payment will be sent to.

        uint paymentOwed;           /// The amount that is owed to the paymentBenefactor.

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
    function hasBenefactor(PaymentData storage self)
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
            return self.feeRecipient.send(feeAmount);
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
    /// Endowment
    ///---------------

    /**
     * @dev Compute the endowment value for the given TransactionRequest parameters.
     * See request_factory.rst in docs folder under Check #1 for more information about
     * this calculation.
     */
    function computeEndowment(
        uint _payment,
        uint _fee,
        uint _callGas,
        uint _callValue,
        uint _gasPrice,
        uint _gasOverhead
    ) 
        public pure returns (uint)
    {
        return _payment
                .add(_fee.mul(2))
                .add(_callGas.mul(_gasPrice))
                .add(_gasOverhead.mul(_gasPrice))
                .add(_callValue);
    }

    /*
     * Validation: ensure that the request endowment is sufficient to cover.
     * - payment * maxMultiplier
     * - fee * maxMultiplier
     * - gasReimbursment
     * - callValue
     */
    function validateEndowment(uint _endowment,
                               uint _payment,
                               uint _fee,
                               uint _callGas,
                               uint _callValue,
                               uint _gasPrice,
                               uint _gasOverhead)
        public pure returns (bool)
    {
        return _endowment >= computeEndowment(
            _payment,
            _fee,
            _callGas,
            _callValue,
            _gasPrice,
            _gasOverhead
        );
    }
}
