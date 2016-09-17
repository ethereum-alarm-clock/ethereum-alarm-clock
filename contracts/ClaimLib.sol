//pragma solidity 0.4.1;

import {SafeSendLib} from "contracts/SafeSendLib.sol";
import {MathLib} from "contracts/MathLib.sol";


library ClaimLib {
    using SafeSendLib for address;
    using MathLib for uint;

    struct ClaimData {
        // The address that has claimed this request
        address claimedBy;

        // The deposit amount that was put down by the claimer.
        uint claimDeposit;

        // An integer constrained between 0-100 that will be applied to the
        // request payment as a percentage.
        uint8 paymentModifier;
    }

    /*
     * Mark the request as being claimed
     */
    function claim(ClaimData storage self, uint8 paymentModifier) returns (bool) {
        self.claimedBy = msg.sender;
        self.claimDeposit = msg.value;
        self.paymentModifier = paymentModifier;
    }

    /*
     * Helper: returns whether this request is claimed.
     */
    function isClaimed(ClaimData storage self) returns (bool) {
        return self.claimedBy != 0x0;
    }

    /*
     * Amount that must be supplied as a deposit to claim.  This is set to the
     * maximum possible payment value that could be paid out by this request.
     */
    function minimumDeposit(uint payment) returns (uint) {
        return payment.safeMultiply(2);
    }

    /*
     * Refund the claimer deposit.
     */
    function refundDeposit(ClaimData storage self) returns (bool) {
        return refundDeposit(self, SafeSendLib.DEFAULT_SEND_GAS());
    }

    function refundDeposit(ClaimData storage self, uint sendGas) returns (bool) {
        uint depositAmount;

        depositAmount = self.claimDeposit;
        // re-entrance protection.
        self.claimDeposit = 0;
        self.claimDeposit = depositAmount.flooredSub(self.claimedBy.safeSend(depositAmount, sendGas));

        return true;
    }
}
