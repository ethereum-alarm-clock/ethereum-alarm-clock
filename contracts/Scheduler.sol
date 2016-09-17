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

    /*
     * Local storage variable used to hold 
     */
    FutureBlockTransactionLib.FutureBlockTransaction futureBlockTransaction;

    function scheduleAtBlock(uint targetBlock) public returns (address) {
        futureBlockTransaction.initialize();
        futureBlockTransaction.targetBlock = targetBlock;
        return futureBlockTransaction.schedule(factoryAddress, trackerAddress);
    }
}
