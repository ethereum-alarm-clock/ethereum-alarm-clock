//pragma solidity 0.4.1;

import {SafeSendLib} from "contracts/SafeSendLib.sol";
import {MathLib} from "contracts/MathLib.sol";


library PaymentLib {
    using SafeSendLib for address;
    using MathLib for uint;

    struct PaymentData {
        // The gas price that was used during creation of this request.
        uint anchorGasPrice;

        // The amount in wei that will be payed to the address that executes
        // this request.
        uint payment;

        // The address that the payment should be sent to.
        address paymentBenefactor;

        // The amount that is owed to the payment benefactor.
        uint paymentOwed;

        // The amount in wei that will be payed to the donationBenefactor address.
        uint donation;

        // The address that the donation should be sent to.
        address donationBenefactor;

        // The amount that is owed to the donation benefactor.
        uint donationOwed;
    }

    /*
     *
     */
    function hasBenefactor(PaymentData storage self) returns (bool) {
        return self.donationBenefactor != 0x0;
    }

    /*
    *  Return a number between 0 - 200 to scale the donation based on the
    *  gas price set for the calling transaction as compared to the gas
    *  price of the scheduling transaction.
    *
    *  - number approaches zero as the transaction gas price goes
    *  above the gas price recorded when the call was scheduled.
    *
    *  - the number approaches 200 as the transaction gas price
    *  drops under the price recorded when the call was scheduled.
    *
    *  This encourages lower gas costs as the lower the gas price
    *  for the executing transaction, the higher the payout to the
    *  caller.
    */
    function getMultiplier(PaymentData storage self) returns (uint) {
        if (tx.gasprice > self.anchorGasPrice) {
            return self.anchorGasPrice.safeMultiply(100) / tx.gasprice;
        }
        else {
            return 200 - (self.anchorGasPrice.safeMultiply(100) /
                self.anchorGasPrice.safeMultiply(2).flooredSub(tx.gasprice)
            ).min(200);
        }
    }

    /*
     *  Computes the amount to send to the donationBenefactor
     */
    function getDonation(PaymentData storage self) returns (uint) {
        if (getMultiplier(self) == 0) throw;
        return self.donation.safeMultiply(getMultiplier(self)) / 100;
    }

    /*
     *  Computes the amount to send to the address that fulfilled the request
     */
    function getPayment(PaymentData storage self) returns (uint) {
        return self.payment.safeMultiply(getMultiplier(self)) / 100;
    }

    /*
     *  Computes the amount to send to the address that fulfilled the request
     *  with an additional modifier.  This is used when the call was claimed.
     */
    function getPaymentWithModifier(PaymentData storage self,
                                    uint8 paymentModifier) returns (uint) {
        return getPayment(self).safeMultiply(paymentModifier) / 100;
    }

    /*
     * Send the donationOwed amount to the donationBenefactor
     */
    function sendDonation(PaymentData storage self) returns (bool) {
        return sendDonation(self, SafeSendLib.DEFAULT_SEND_GAS());
    }

    function sendDonation(PaymentData storage self, uint sendGas) returns (bool) {
        uint donationAmount = self.donationOwed;
        if (donationAmount > 0) {
            // re-entrance protection.
            self.donationOwed = 0;
            self.donationOwed = donationAmount.flooredSub(self.donationBenefactor.safeSend(donationAmount,
                                                                                           sendGas));
        }
        return true;
    }

    /*
     * Send the paymentOwed amount to the paymentBenefactor
     */
    function sendPayment(PaymentData storage self) returns (bool) {
        return sendPayment(self, SafeSendLib.DEFAULT_SEND_GAS());
    }

    function sendPayment(PaymentData storage self, uint sendGas) returns (bool) {
        uint paymentAmount = self.paymentOwed;
        if (paymentAmount > 0) {
            // re-entrance protection.
            self.paymentOwed = 0;
            self.paymentOwed = paymentAmount.flooredSub(self.paymentBenefactor.safeSend(paymentAmount,
                                                                                        sendGas));
        }
        return true;
    }


    /*
     * Compute the required endowment value for the given TransactionRequest
     * parameters.
     */
    function computeEndowment(uint payment,
                              uint donation,
                              uint callGas,
                              uint callValue) returns (uint) {
        return payment.safeAdd(donation)
                      .safeMultiply(2)
                      .safeAdd(callGas.safeMultiply(tx.gasprice))
                      .safeAdd(callValue);
    }

    /*
     * Validation: ensure that the request endowment is sufficient to cover.
     * - payment * maxMultiplier
     * - donation * maxMultiplier
     * - gasReimbursment
     * - callValue
     */
    function validateEndowment(uint endowment,
                               uint payment,
                               uint donation,
                               uint callGas,
                               uint callValue) returns (bool) {
        return endowment >= payment.safeAdd(donation)
                                   .safeMultiply(2)
                                   .safeAdd(callGas.safeMultiply(tx.gasprice))
                                   .safeAdd(callValue);
    }
}
