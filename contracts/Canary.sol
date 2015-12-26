contract SchedulerInterface {
    function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment, uint baseFee) public returns (address);
    function isKnownCall(address callAddress) constant returns (bool);
}

contract CallContractAPI {
    function targetBlock() constant returns (uint);
    function cancel() public;
}


contract Canary {
    uint public aliveSince;
    uint public lastHeartbeat;
    uint public heartbeatCount;
    SchedulerInterface scheduler;
    CallContractAPI callContract;

    address public owner;

    function schedulerAddress() constant returns (address) {
        return address(scheduler);
    }

    function callContractAddress() constant returns (address) {
        return address(callContract);
    }

    function Canary(address _scheduler) {
            owner = msg.sender;
            scheduler = SchedulerInterface(_scheduler);
            aliveSince = now;
    }

    function() {
        if (this.balance < 2 ether) {
            owner.send(this.balance);
        }
    }

    function cancel() {
        // not authorized
        if (msg.sender != owner) throw;
        // need to wait until the 
        if (callContract.balance > 0) {
            callContract.cancel();
        }
        owner.send(address(this).balance);

    }

    event Heartbeat(uint blockNumber, uint heartbeatCount, address callerAddress, address originAddress, address nextCallerAddress);

    function heartbeat() public {
        // Ran out of funds.
        if (this.balance < 2 ether) return;
        // The canary has died!
        if (!isAlive()) return;
        // Not being called by the callContract
        if (address(callContract) != 0x0 && msg.sender != address(callContract)) return;

        // Increment the heartbeat count
        heartbeatCount += 1;

        // schedule the call (~2 hours from now)
        address call_address = scheduler.scheduleCall.value(2 ether)(address(this), bytes4(sha3("heartbeat()")), block.number + 480, 2000000, 255, 1 finney, 0);
        if (call_address != 0x0) {
            callContract = CallContractAPI(call_address);
        }

        // Log the heartbeat
        Heartbeat(block.number, heartbeatCount, msg.sender, tx.origin, address(callContract));
    }

    function isAlive() constant returns (bool) {
        if (address(callContract) == 0x0) return true;
        return (block.number < callContract.targetBlock() + 255);
    }
}


contract CanaryV6 is Canary {
    function CanaryV6() Canary(0xe109ecb193841af9da3110c80fdd365d1c23be2a) {
    }
}
