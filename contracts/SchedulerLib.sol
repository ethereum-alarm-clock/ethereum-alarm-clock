//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";
import {RequestTrackerInterface} from "contracts/RequestTrackerInterface.sol";
import {PaymentLib} from "contracts/PaymentLib.sol";
import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {SafeSendLib} from "contracts/SafeSendLib.sol";
import {MathLib} from "contracts/MathLib.sol";


library SchedulerLib {
    using SafeSendLib for address;
    using MathLib for uint;

    address constant DONATION_BENEFACTOR = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

    struct FutureTransaction {
        uint donation;
        uint payment;

        uint windowSize;
        uint windowStart;
        RequestScheduleLib.TemporalUnit temporalUnit;

        uint callGas;
        uint callValue;
        bytes callData;
        address toAddress;
        uint requiredStackDepth;

        uint reservedWindowSize;
        uint freezePeriod;
        uint claimWindowSize;
    }

    /*
     * Set common default values.
     */
    function resetCommon(FutureTransaction storage self) public returns (bool) {
        if (self.payment != 1000000 * tx.gasprice) {
            self.payment = 1000000 * tx.gasprice;
        }
        if (self.donation != self.payment / 100 ) {
            self.donation = self.payment / 100;
        }
        if (self.toAddress != msg.sender) {
            self.toAddress = msg.sender;
        }
        if (self.callGas != 90000) {
            self.callGas = 90000;
        }
        if (self.callData.length != 0) {
            self.callData = "";
        }
        if (self.requiredStackDepth != 10) {
            self.requiredStackDepth = 10;
        }
        return true;
    }

    /*
     * Set default values for block based scheduling.
     */
    function resetAsBlock(FutureTransaction storage self) public returns (bool) {
        if (!resetCommon(self)) throw;

        if (self.windowSize != 255) {
            self.windowSize = 255;
        }
        if (self.windowStart != block.number + 10) {
            self.windowStart = block.number + 10;
        }
        if (self.reservedWindowSize != 16) {
            self.reservedWindowSize = 16;
        }
        if (self.freezePeriod != 10) {
            self.freezePeriod = 10;
        }
        if (self.claimWindowSize != 255) {
            self.claimWindowSize = 255;
        }

        return true;
    }

    /*
     * Set default values for timestamp based scheduling.
     */
    function resetAsTimestamp(FutureTransaction storage self) public returns (bool) {
        if (!resetCommon(self)) throw;

        if (self.windowSize != 60 minutes) {
            self.windowSize = 60 minutes;
        }
        if (self.windowStart != now + 5 minutes) {
            self.windowStart = now + 5 minutes;
        }
        if (self.reservedWindowSize != 5 minutes) {
            self.reservedWindowSize = 5 minutes;
        }
        if (self.freezePeriod != 3 minutes) {
            self.freezePeriod = 3 minutes;
        }
        if (self.claimWindowSize != 60 minutes) {
            self.claimWindowSize = 60 minutes;
        }

        return true;
    }

    /*
     *  The low level interface for creating a transaction request.
     */
    function schedule(FutureTransaction storage self,
                      address factoryAddress,
                      address trackerAddress) public returns (address) {
        var factory = RequestFactoryInterface(factoryAddress);
        var endowment = PaymentLib.computeEndowment(
            self.payment,
            self.donation,
            self.callGas,
            self.callValue
        ).min(this.balance);

        address newRequestAddress = factory.createValidatedRequest.value(msg.value)(
            [
                msg.sender,           // meta.owner
                DONATION_BENEFACTOR,  // paymentData.donationBenefactor
                self.toAddress        // txnData.toAddress
            ],
            [
                self.donation,            // paymentData.donation
                self.payment,             // paymentData.payment
                self.claimWindowSize,     // scheduler.claimWindowSize
                self.freezePeriod,        // scheduler.freezePeriod
                self.reservedWindowSize,  // scheduler.reservedWindowSize
                uint(self.temporalUnit),  // scheduler.temporalUnit (1: block, 2: timestamp)
                self.windowSize,          // scheduler.windowSize
                self.windowStart,         // scheduler.windowStart
                self.callGas,             // txnData.callGas
                self.callValue,           // txnData.callValue
                self.requiredStackDepth   // txnData.requiredStackDepth
            ],
            self.callData
        );
        return 0x0;

        if (newRequestAddress == 0x0) {
            // Something went wrong during creation (likely a ValidationError).
            // Try to return the ether that was sent.  If this fails then
            // resort to throwing an exception to force reversion.
            if (msg.sender.sendOrThrow(msg.value)) {
                return 0x0;
            }
            throw;
        }

        var tracker = RequestTrackerInterface(trackerAddress);
        tracker.addRequest(newRequestAddress, self.windowStart);

        return newRequestAddress;
    }
}
