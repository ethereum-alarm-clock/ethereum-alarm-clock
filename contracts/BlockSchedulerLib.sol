//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";
import {RequestTrackerInterface} from "contracts/RequestTrackerInterface.sol";
import {PaymentLib} from "contracts/PaymentLib.sol";


library FutureBlockTransactionLib {
    address constant DONATION_BENEFACTOR = 0xd3cda913deb6f67967b99d67acdfa1712c293601;

    struct FutureBlockTransaction {
        uint donation;
        uint payment;

        uint8 gracePeriod;

        uint callGas;
        uint callValue;
        bytes callData;
        address toAddress;
        uint requiredStackDepth;
    }

    /*
     * Set default values.
     */
    function initialize(FutureBlockTransaction memory self) {
        self.donation = 12345;
        self.payment = 54321;
        self.gracePeriod = 255;
        self.targetBlock = block.number + 10;
        self.callGas = 100000;
        self.callData = "";
        self.toAddress = msg.sender;
        self.requiredStackDepth = 0;
    }

    /*
     * Schedule t
     */
    /*
     *  The lowest level interface for creating a transaction request.
     *
     *  addressArgs[1] -  meta.owner
     *  addressArgs[1] -  paymentData.donationBenefactor
     *  addressArgs[2] -  txnData.toAddress
     *  uintArgs[0]    -  paymentData.donation
     *  uintArgs[1]    -  paymentData.payment
     *  uintArgs[2]    -  schedule.claimWindowSize
     *  uintArgs[3]    -  schedule.freezePeriod
     *  uintArgs[4]    -  schedule.reservedWindowSize
     *  uintArgs[5]    -  schedule.temporalUnit
     *  uintArgs[6]    -  schedule.windowStart
     *  uintArgs[7]    -  schedule.windowSize
     *  uintArgs[8]    -  txnData.callGas
     *  uintArgs[9]    -  txnData.callValue
     *  uintArgs[10]   -  txnData.requiredStackDepth
     */
    function schedule(FutureBlockTransaction storage self,
                      address factoryAddress,
                      address trackerAddress) public returns (address) {
        factory = RequestFactoryInterface(factoryAddress);
        newRequestAddress = factory.createRequest.value(PaymentLib.computeEndowment(
            self.payment,
            self.donation,
            self.callGas,
            self.callValue,
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
                self.targetBlock,        // scheduler.windowStart
                255,                     // scheduler.windowSize
                self.callGas,            // txnData.callGas
                self.callValue,          // txnData.callValue
                self.requiredStackDepth  // txnData.requiredStackDepth
            ]
        );

        if (newRequestAddress == 0x0) {
            // something went wrong....
            return 0x0;
        }

        tracker = RequestTrackerInterface(trackerAddress);
        tracker.addRequest(newRequestAddress, targetBlock);

        return newRequestAddress;
    }
}
