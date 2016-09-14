//pragma solidity 0.4.1;


library ClaimLib {
    struct ClaimData {
        // The address that has claimed this request
        address claimedBy;

        // The deposit amount that was put down by the claimer.
        uint claimDeposit;

        // An integer constrained between 0-100 that will be applied to the
        // request payment as a percentage.
        uint8 paymentModifier;

        // The number of temporal units that prior to the call freeze window
        // during which the request will be claimable.
        uint claimWindowSize;
    }

    /*
     * Helper: returns whether this request is claimed.
     */
    function isClaimed(ClaimData storage self) returns (bool) {
        return self.claimedBy != 0x0;
    }
}
