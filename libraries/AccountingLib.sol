library AccountingLib {
        struct Bank {
            mapping (address => uint) public accountBalances;
        }

        /*
         *  Account Management API
         */
        function _deductFunds(address accountAddress, uint value) internal {
                /*
                 *  Helper function that should be used for any reduction of
                 *  account funds.  It has error checking to prevent
                 *  underflowing the account balance which would be REALLY bad.
                 */
                if (value > accountBalances[accountAddress]) {
                        // Prevent Underflow.
                        throw;
                }
                accountBalances[accountAddress] -= value;
        }

        function _addFunds(address accountAddress, uint value) internal {
                /*
                 *  Helper function that should be used for any addition of
                 *  account funds.  It has error checking to prevent
                 *  overflowing the account balance.
                 */
                if (accountBalances[accountAddress] + value < accountBalances[accountAddress]) {
                        // Prevent Overflow.
                        throw;
                }
                accountBalances[accountAddress] += value;
        }

        event Deposit(address indexed _from, address indexed accountAddress, uint value);

        function deposit(address accountAddress) public returns (bool) {
                /*
                 *  Public API for depositing funds in a specified account.
                 */
                _addFunds(accountAddress, msg.value);
                return true;
        }

        event Withdrawal(address indexed accountAddress, uint value);
        event InsufficientFunds(address indexed accountAddress, uint value, uint balance);

        function withdraw(uint value) public returns (bool) {
                /*
                 *  Public API for withdrawing funds.
                 */
                if (accountBalances[msg.sender] >= value) {
                        _deductFunds(msg.sender, value);
                        if (!msg.sender.send(value)) {
                                // Potentially sending money to a contract that
                                // has a fallback function.  So instead, try
                                // tranferring the funds with the call api.
                                if (!msg.sender.call.gas(msg.gas).value(value)()) {
                                        // Revert the entire transaction.  No
                                        // need to destroy the funds.
                                        throw;
                                }
                        }
                        return true;
                }
                return false;
        }
}
