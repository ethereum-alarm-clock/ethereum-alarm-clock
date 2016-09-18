//pragma solidity 0.4.1;


import {FutureBlockTransactionLib} from "contracts/BlockSchedulerLib.sol";


contract BaseScheduler {
    address trackerAddress;
    address factoryAddress;

    function BaseScheduler(address _trackerAddress, address _factoryAddress) {
        trackerAddress = _trackerAddress;
        factoryAddress = _factoryAddress;
    }
}


contract BlockScheduler is BaseScheduler {
    using FutureBlockTransactionLib for FutureBlockTransactionLib.FutureBlockTransaction;

    function BlockScheduler(address _trackerAddress, address _factoryAddress)
             BaseScheduler(_trackerAddress, _factoryAddress) {
    }

    /*
     * Local storage variable used to hold 
     */
    FutureBlockTransactionLib.FutureBlockTransaction futureBlockTransaction;

    modifier doReset {
        futureBlockTransaction.reset();
        _ 
    }

    /*
     *  Full scheduling API exposing all fields.
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] windowStart
     *  uint8 windowSize;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint8 windowSize,
                                 uint[3] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.windowSize = windowSize;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.windowStart = uintArgs[2];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  Full scheduling API exposing all fields.
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] donation
     *  uintArgs[3] payment
     *  uintArgs[4] requiredStackDepth
     *  uintArgs[5] windowStart
     *  uint8 windowSize;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint8 windowSize,
                                 uint[6] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.windowSize = windowSize;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.donation = uintArgs[2];
        futureBlockTransaction.payment = uintArgs[3];
        futureBlockTransaction.requiredStackDepth = uintArgs[4];
        futureBlockTransaction.windowStart = uintArgs[5];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }
}
