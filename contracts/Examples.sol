contract ERC20Token {
    /*
     *  https://github.com/ethereum/EIPs/issues/20
     */
    function totalSupply() constant returns (uint supply);
    function balanceOf( address who ) constant returns (uint value);
    function allowance(address owner, address spender) constant returns (uint _allowance);
    function transfer( address to, uint value) returns (bool ok);
    function transferFrom( address from, address to, uint value) returns (bool ok);
    function approve(address spender, uint value) returns (bool ok);
    event Transfer(address indexed from, address indexed to, uint value);
    event Approval( address indexed owner, address indexed spender, uint value);
}


contract TrustFund {
    /*
     *  This contract locks away whatever funds it was given until the
     *  `releaseBlock`
     */
    address public beneficiary;
    uint public releaseBlock;

    function TrustFund(address _beneficiary, uint _releaseBlock, address alarmScheduler) {
        beneficiary = _beneficiary;
        releaseBlock = _releaseBlock;

        // Schedule a call to happen at the block specified by release block.
        alarmScheduler.call(bytes4(sha3("scheduleCall(uint256)")), releaseBlock);
    }

    function releaseFunds() {
        // only release the funds if there are sunds to be released and we've
        // reached `releaseBlock`
        if (this.balance == 0 || block.number < releaseBlock) return;

        beneficiary.send(this.balance);
    }

    function () {
        releaseFunds();
    }
}


contract TokenCallContract {
    address public schedulerAddress;
}

contract TokenScheduler {
    function isKnownCall(address callAddress) public returns (bool);
    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock) public returns (address);
}


contract ERC20ScheduledTransfer is ERC20Token {
    /*
     *  An ERC20 compliant token contract which supports scheduled funds
     *  transfers.
     */
    // Note: this address should be filled out with the address of the Alarm
    // Scheduler contract.
    TokenScheduler public scheduler = TokenScheduler(0x0);

    mapping (address => uint) balances;

    function scheduleTransfer(address to, uint value, uint when) returns (bool) {
        // Schedule the call;
        var callAddress = scheduler.scheduleCall(bytes4(sha3("transferFrom(address,address,uint256)")), when);
        // Register the call data
        callAddress.call(msg.sender, to, value);
    }

    function transferFrom(address from, address to, uint value) returns (bool) {
        // Insufficient balance
        if (value > balances[from]) return;

        bool isAuthorized;

        if (msg.sender == from) {
            isAuthorized = true;
        }
        else if (scheduler.isKnownCall(msg.sender)) {
            // If the caller is a known call contract with the scheduler we can
            // trust it to tell us who scheduled it.
            var call = TokenCallContract(msg.sender);
            var schedulerAddress = call.schedulerAddress();

            // The call is authorized if either this token contract or the
            // `from` address was the scheduler of the call.
            isAuthorized = (schedulerAddress == from || schedulerAddress == address(this));
        }
        else {
            isAuthorized = false;
        }

        if (isAuthorized) {
            balances[from] -= value;
            balances[to] += value;
            Transfer(from, to , value);
            return true;
        }
        return false;
    }
}
