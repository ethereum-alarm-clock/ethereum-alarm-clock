//pragma solidity 0.4.1;


library SafeSendLib {
    event SendFailed(address to, uint value);

    uint constant _DEFAULT_SEND_GAS = 30000;

    function DEFAULT_SEND_GAS() returns (uint) {
        return _DEFAULT_SEND_GAS;
    }

    /*
     * Send ether to an address.
     * On failure log the `SendFailed` event.
     * Returns the amount of wei that was sent (which will be 0 on failure).
     */
    function safeSend(address to, uint value) returns (uint) {
        return safeSend(to, value, _DEFAULT_SEND_GAS);
    }

    /*
     * Same as `safeSend` but allows specifying the gas to be included with the
     * send.
     */
    function safeSend(address to, uint value, uint sendGas) returns (uint) {
        if (value > this.balance) {
            value = this.balance;
        }

        if (value == 0) {
            return 0;
        }

        if (to == 0x0) {
            //throw;
        }

        if (!to.call.value(value).gas(sendGas)()) {
            SendFailed(to, value);
            return 0;
        }

        return value;
    }

    /*
     * Try to send to the account.  If the send fails, then throw.
     */
    function sendOrThrow(address to, uint value) returns (bool) {
        uint remainder = safeSend(to, value, msg.gas);
        if (remainder > 0) {
            //throw;
        }
        return true;
    }
}
