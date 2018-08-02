pragma solidity 0.4.24;

library ClaimLib {

    struct ClaimData {
        address claimedBy;          // The address that has claimed the txRequest.
        uint claimDeposit;          // The deposit amount that was put down by the claimer.
        uint requiredDeposit;       // The required deposit to claim the txRequest.
        uint8 paymentModifier;      // An integer constrained between 0-100 that will be applied to the
                                    // request payment as a percentage.
    }

    /*
     * @dev Mark the request as being claimed.
     * @param self The ClaimData that is being accessed.
     * @param paymentModifier The payment modifier.
     */
    function claim(
        ClaimData storage self, 
        uint8 _paymentModifier
    ) 
        internal returns (bool)
    {
        self.claimedBy = msg.sender;
        self.claimDeposit = msg.value;
        self.paymentModifier = _paymentModifier;
        return true;
    }

    /*
     * Helper: returns whether this request is claimed.
     */
    function isClaimed(ClaimData storage self) 
        internal view returns (bool)
    {
        return self.claimedBy != 0x0;
    }


    /*
     * @dev Refund the claim deposit to claimer.
     * @param self The Request.ClaimData
     * Called in RequestLib's `cancel()` and `refundClaimDeposit()`
     */
    function refundDeposit(ClaimData storage self) 
        internal returns (bool)
    {
        // Check that the claim deposit is non-zero.
        if (self.claimDeposit > 0) {
            uint depositAmount;
            depositAmount = self.claimDeposit;
            self.claimDeposit = 0;
            /* solium-disable security/no-send */
            return self.claimedBy.send(depositAmount);
        }
        return true;
    }
}