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
     *  +----------------+
     *  | Scheduling API |
     *  +----------------+
     *
     *  Attempt to expose as many common ways of scheduling a transaction
     *  request as possible.
     *
     *  uint donation;
     *  uint payment;
     *  uint8 gracePeriod;
     *  uint targetBlock;
     *  uint callGas;
     *  uint callValue;
     *  bytes callData;
     *  address toAddress;
     *  uint requiredStackDepth;
     */
    function scheduleTransaction() doReset public returns (address) {
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  +----------------------------+
     *  | Common Scheduling Patterns |
     *  +----------------------------+
     */

    /*
     * - without targetBlock
     */
    function scheduleTransaction(address toAddress) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint callValue,
                                 address toAddress) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callValue = callValue;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(address toAddress,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint callValue) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     * - with targetBlock
     */
    function scheduleTransaction(uint targetBlock,
                                 address toAddress,
                                 uint callValue) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callValue = callValue;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint targetBlock,
                                 address toAddress,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint targetBlock,
                                 address toAddress,
                                 bytes callData,
                                 uint callValue) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }


    /*
     *  +---------------------------------------------------------+
     *  | Transactions which will use msg.sender as the toAddress |
     *  +---------------------------------------------------------+
     */

    /*
     *  - without callData
     */
    function scheduleTransaction(uint targetBlock) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint targetBlock,
                                 uint callValue) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint targetBlock,
                                 uint callValue,
                                 uint callGas) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        futureBlockTransaction.callGas = callGas;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }


    /*
     *  - with callData
     */
    function scheduleTransaction(uint targetBlock,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint targetBlock,
                                 uint callValue,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(uint targetBlock,
                                 uint callValue,
                                 uint callGas,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        futureBlockTransaction.callGas = callGas;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  +--------------------------------------------+
     *  | Transactions which specify the `toAddress` |
     *  +--------------------------------------------+
     */

    /*
     *  - without callData
     */
    function scheduleTransaction(address toAddress,
                                 uint targetBlock) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.targetBlock = targetBlock;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(address toAddress,
                                 uint targetBlock,
                                 uint callValue) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(address toAddress,
                                 uint targetBlock,
                                 uint callValue,
                                 uint callGas) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        futureBlockTransaction.callGas = callGas;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }


    /*
     *  - with callData
     */
    function scheduleTransaction(address toAddress,
                                 uint targetBlock,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(address toAddress,
                                 uint targetBlock,
                                 uint callValue,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    function scheduleTransaction(address toAddress,
                                 uint targetBlock,
                                 uint callValue,
                                 uint callGas,
                                 bytes callData) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.targetBlock = targetBlock;
        futureBlockTransaction.callValue = callValue;
        futureBlockTransaction.callGas = callGas;
        futureBlockTransaction.callData = callData;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  All fields except `requiredStackDepth` and `gracePeriod` and `donation` and `payment`
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] targetBlock
     *  uint8 gracePeriod;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint[3] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.targetBlock = uintArgs[2];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  All fields except `requiredStackDepth` and `gracePeriod` and `donation`
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] payment
     *  uintArgs[3] targetBlock
     *  uint8 gracePeriod;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint[4] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.payment = uintArgs[2];
        futureBlockTransaction.targetBlock = uintArgs[3];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  All fields except `requiredStackDepth` and `gracePeriod`
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] donation
     *  uintArgs[3] payment
     *  uintArgs[4] targetBlock
     *  uint8 gracePeriod;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint[5] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.donation = uintArgs[2];
        futureBlockTransaction.payment = uintArgs[3];
        futureBlockTransaction.targetBlock = uintArgs[4];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  All fields except `requiredStackDepth`
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] donation
     *  uintArgs[3] payment
     *  uintArgs[4] targetBlock
     *  uint8 gracePeriod;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint8 gracePeriod,
                                 uint[5] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.gracePeriod = gracePeriod;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.donation = uintArgs[2];
        futureBlockTransaction.payment = uintArgs[3];
        futureBlockTransaction.targetBlock = uintArgs[4];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  Full scheduling API exposing all fields.
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] donation
     *  uintArgs[3] payment
     *  uintArgs[4] targetBlock
     *  uintArgs[5] requiredStackDepth
     *  uint8 gracePeriod;
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint8 gracePeriod,
                                 uint[6] uintArgs) doReset public returns (address) {
        futureBlockTransaction.toAddress = toAddress;
        futureBlockTransaction.callData = callData;
        futureBlockTransaction.gracePeriod = gracePeriod;
        futureBlockTransaction.callGas = uintArgs[0];
        futureBlockTransaction.callValue = uintArgs[1];
        futureBlockTransaction.donation = uintArgs[2];
        futureBlockTransaction.payment = uintArgs[3];
        futureBlockTransaction.targetBlock = uintArgs[4];
        futureBlockTransaction.requiredStackDepth = uintArgs[5];
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }
}
