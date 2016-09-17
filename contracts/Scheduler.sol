//pragma solidity 0.4.1;


import {FutureBlockTransactionLib} from "contracts/FutureBlockTransactionLib.sol";


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
    FutureBlockTransactionLib.FutureBlockTransaction __futureBlockTransaction;

    function scheduleTransaction() public returns (address) {
    }
}



