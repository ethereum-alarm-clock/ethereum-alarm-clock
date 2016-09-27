//pragma solidity 0.4.1;

import {MathLib} from "contracts/MathLib.sol";


library SafeSendLib {
    using MathLib for uint;

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

    uint constant _GAS_BUFFER = 10000;

    function GAS_BUFFER() returns (uint) {
        return _GAS_BUFFER;
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
            throw;
        }

        if (sendGas > 0) {
            // 0 send gas indicates sending all send gas.
            if (!to.call.value(value)
                        .gas(sendGas.min(msg.gas.flooredSub(_GAS_BUFFER)))()) {
                SendFailed(to, value);
                return 0;
            }
        } else {
            if (!to.call.value(value)()) {
                SendFailed(to, value);
                return 0;
            }
        }


        return value;
    }

    /*
     * Try to send to the account.  If the send fails, then throw.
     */
    function sendOrThrow(address to, uint value) returns (bool) {
        if (value > this.balance) {
            throw;
        }

        if (value == 0) {
            return true;
        }

        if (to == 0x0) {
            throw;
        }

        if (!to.call.value(value)()) {
            throw;
        }

        return true;
    }
}
