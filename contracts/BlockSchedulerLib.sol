//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";
import {RequestTrackerInterface} from "contracts/RequestTrackerInterface.sol";
import {PaymentLib} from "contracts/PaymentLib.sol";
import {SafeSendLib} from "contracts/SafeSendLib.sol";


library FutureBlockTransactionLib {
    using SafeSendLib for address;

    address constant DONATION_BENEFACTOR = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

    struct FutureBlockTransaction {
        uint donation;
        uint payment;

        uint8 windowSize;

        uint windowStart;
        uint callGas;
        uint callValue;
        bytes callData;
        address toAddress;
        uint requiredStackDepth;
    }

    /*
     * Set default values.
     */
    function reset(FutureBlockTransaction storage self) {
        self.donation = 12345;
        self.payment = 54321;
        self.windowSize = 255;
        self.windowStart = block.number + 10;
        self.toAddress = msg.sender;
        self.callGas = 90000;
        self.callData = "";
        self.requiredStackDepth = 0;
    }

    /*
     *  The low level interface for creating a transaction request.
     */
    function schedule(FutureBlockTransaction storage self,
                      address factoryAddress,
                      address trackerAddress) public returns (address) {
        var factory = RequestFactoryInterface(factoryAddress);
        address newRequestAddress = factory.createRequest.value(PaymentLib.computeEndowment(
            self.payment,
            self.donation,
            self.callGas,
            self.callValue
        ))(
            [
                msg.sender,           // meta.owner
                DONATION_BENEFACTOR,  // paymentData.donationBenefactor
                self.toAddress        // txnData.toAddress
            ],
            [
                self.donation,           // paymentData.donation
                self.payment,            // paymentData.payment
                255,                     // scheduler.claimWindowSize
                10,                      // scheduler.freezePeriod
                16,                      // scheduler.reservedWindowSize
                1,                       // scheduler.temporalUnit (block)
                self.windowStart,        // scheduler.windowStart
                255,                     // scheduler.windowSize
                self.callGas,            // txnData.callGas
                self.callValue,          // txnData.callValue
                self.requiredStackDepth  // txnData.requiredStackDepth
            ],
            self.callData
        );

        if (newRequestAddress == 0x0) {
            // Something went wrong during creation (likely a ValidationError).
            // Try to return the ether that was sent.  If this fails then
            // resort to throwing an exception to force reversion.
            return 0x0;
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
