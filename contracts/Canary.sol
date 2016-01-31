contract SchedulerInterface {
    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas) public returns (address);
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

    uint16 public frequency;

    function Canary(address _scheduler, uint16 _frequency) {
            owner = msg.sender;
            scheduler = SchedulerInterface(_scheduler);
            frequency = _frequency;
    }

    function() {
        if (this.balance < 2 ether) {
            owner.send(this.balance);
        }
    }

    function cancel() public {
        // not authorized
        if (msg.sender != owner) throw;
        // need to wait until the 
        if (callContract.balance > 0) {
            callContract.cancel();
        }
        owner.send(address(this).balance);

    }

    function initialize() public {
        // ensure we are not already initialized.
        if (aliveSince != 0) return;

        // mark when the canary came to life.
        aliveSince = now;

        // schedule the first call
        scheduleHeartbeat();
    }

    function scheduleHeartbeat() public {
        // schedule the call (~2 hours from now)
        address call_address = scheduler.scheduleCall.value(2 ether)(
            0x3defb962,
            block.number + frequency,
            2000000);
        if (call_address != 0x0) {
            callContract = CallContractAPI(call_address);
        }
    }

    function heartbeat() public {
        // Ran out of funds.
        if (this.balance < 2 ether) return;

        // Not being called by the callContract.
        if (msg.sender != address(callContract)) return;

        // The canary has died!
        if (!isAlive()) return;

        // schedule the next call.
        scheduleHeartbeat();

        // Increment the heartbeat count
        heartbeatCount += 1;
        lastHeartbeat = now;
    }

    function isAlive() constant returns (bool) {
        return (aliveSince > 0 && block.number < callContract.targetBlock() + 255);
    }
}


contract CanaryV7 is Canary {
    function CanaryV7() Canary(0x6c8f2a135f6ed072de4503bd7c4999a1a17f824b, 480) {
    }
}


contract CanaryV7Testnet is Canary {
    function CanaryV7Testnet() Canary(0x26416b12610d26fd31d227456e9009270574038f, 480) {
    }
}


contract CanaryV7FastTestnet is Canary {
    function CanaryV7FastTestnet() Canary(0x26416b12610d26fd31d227456e9009270574038f, 100) {
    }
}
