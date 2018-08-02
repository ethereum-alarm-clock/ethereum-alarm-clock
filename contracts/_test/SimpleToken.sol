pragma solidity 0.4.24;

/// Super simple token contract that moves funds into the owner account on creation and
/// only exposes an API to be used for `test/proxy.js`
contract SimpleToken {

    address public owner;

    mapping(address => uint) balances;

    function SimpleToken (uint _initialSupply) public {
        owner = msg.sender;
        balances[owner] = _initialSupply;
    }

    function transfer (address _to, uint _amount)
        public returns (bool success)
    {
        require(balances[msg.sender] > _amount);
        balances[msg.sender] -= _amount;
        balances[_to] += _amount;
        success = true;
    }

    uint public constant rate = 30;

    function buyTokens()
        public payable returns (bool success)
    {
        require(msg.value > 0);
        balances[msg.sender] += msg.value * rate;
        success = true;
    }

    function balanceOf (address _who)
        public view returns (uint balance)
    {
        balance = balances[_who];
    }
}
