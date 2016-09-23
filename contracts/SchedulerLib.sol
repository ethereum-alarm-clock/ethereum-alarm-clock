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

        uint8 windowSize;
        uint windowStart;
        RequestScheduleLib.TemporalUnit temporalUnit;

        uint callGas;
        uint callValue;
        bytes callData;
        address toAddress;
        uint requiredStackDepth;
    }

    /*
     * Set default values.
     */
    function resetAsBlock(FutureTransaction storage self) public returns (bool) {
        self.donation = 12345;
        self.payment = 54321;
        self.windowSize = 255;
        self.windowStart = block.number + 10;
        self.toAddress = msg.sender;
        self.callGas = 90000;
        self.callData = "";
        self.requiredStackDepth = 0;

        return true;
    }

    function resetAsTimestamp(FutureTransaction storage self) public returns (bool) {
        self.donation = 12345;
        self.payment = 54321;
        self.windowSize = 255;
        self.windowStart = now + 5 minutes;
        self.toAddress = msg.sender;
        self.callGas = 90000;
        self.callData = "";
        self.requiredStackDepth = 0;

        return true;
    }

    /*
     *  The low level interface for creating a transaction request.
     */
    function schedule(FutureTransaction storage self,
                      address factoryAddress,
                      address trackerAddress) public returns (address) {
        var factory = RequestFactoryInterface(factoryAddress);
        address newRequestAddress = factory.createRequest.value(PaymentLib.computeEndowment(
            self.payment,
            self.donation,
            self.callGas,
            self.callValue
        ).min(this.balance))(
            [
                msg.sender,           // meta.owner
                DONATION_BENEFACTOR,  // paymentData.donationBenefactor
                self.toAddress        // txnData.toAddress
            ],
            [
                self.donation,            // paymentData.donation
                self.payment,             // paymentData.payment
                255,                      // scheduler.claimWindowSize
                10,                       // scheduler.freezePeriod
                16,                       // scheduler.reservedWindowSize
                uint(self.temporalUnit),  // scheduler.temporalUnit (1: block, 2: timestamp)
                self.windowStart,         // scheduler.windowStart
                255,                      // scheduler.windowSize
                self.callGas,             // txnData.callGas
                self.callValue,           // txnData.callValue
                self.requiredStackDepth   // txnData.requiredStackDepth
            ],
            self.callData
        );

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
