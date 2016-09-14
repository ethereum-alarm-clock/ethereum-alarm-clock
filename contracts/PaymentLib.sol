//pragma solidity 0.4.1;


library PaymentLib {
    struct PaymentData {
        // The gas price that was used during creation of this request.
        uint anchorGasPrice;

        // The amount in wei that will be payed to the address that executes
        // this request.
        uint payment;

        // The amount in wei that will be payed to the donationBenefactor address.
        uint donation;

        // The address that the donation amount will be paid to.
        address donationBenefactor;
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
            return 100 * self.anchorGasPrice / tx.gasprice;
        }
        else {
            return 200 - 100 * self.anchorGasPrice / (2 * self.anchorGasPrice - tx.gasprice);
        }
    }

    /*
     *  Computes the amount to send to the donationBenefactor
     */
    function getDonation(PaymentData storage self) returns (uint) {
        return self.donation * getMultiplier(self) / 100;
    }

    /*
     *  Computes the amount to send to the address that fulfilled the request
     */
    function getPayment(PaymentData storage self) returns (uint) {
        return self.payment * getMultiplier(self) / 100;
    }

    /*
     *  Computes the amount to send to the address that fulfilled the request
     *  with an additional modifier.  This is used when the call was claimed.
     */
    function getPaymentWithModifier(PaymentData storage self,
                                    uint8 paymentModifier)returns (uint) {
        return getPayment(self) * 100 / paymentModifier;
    }

    event SendFailed(address to, uint value);

    uint constant DEFAULT_SEND_GAS = 90000;

    /*
     * Send ether to an address.
     * On failure log the `SendFailed` event.
     * Returns the amount of wei that was sent (which will be 0 on failure).
     */
    function safeSend(address to, uint value) internal returns (uint) {
        return safeSend(to, value, DEFAULT_SEND_GAS);
    }

    /*
     * Same as `safeSend` but allows specifying the gas to be included with the
     * send.
     */
    function safeSend(address to, uint value, uint sendGas) internal returns (uint) {
        if (value > this.balance) {
            value = this.balance;
        }

        if (value == 0) {
            return 0;
        }

        if (!to.call.value(value).gas(sendGas)()) {
            SendFailed(to, value);
            return 0;
        }

        return 0;
    }
}
