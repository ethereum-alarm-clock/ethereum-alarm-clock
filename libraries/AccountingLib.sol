library AccountingLib {
        struct Bank {
            mapping (address => uint) accountBalances;
        }

        /*
         *  Account Management API
         */
        function _deductFunds(Bank storage self, address accountAddress, uint value) internal {
                /*
                 *  Helper function that should be used for any reduction of
                 *  account funds.  It has error checking to prevent
                 *  underflowing the account balance which would be REALLY bad.
                 */
                if (value > self.accountBalances[accountAddress]) {
                        // Prevent Underflow.
                        throw;
                }
                self.accountBalances[accountAddress] -= value;
        }

        function _addFunds(Bank storage self, address accountAddress, uint value) internal {
                /*
                 *  Helper function that should be used for any addition of
                 *  account funds.  It has error checking to prevent
                 *  overflowing the account balance.
                 */
                if (self.accountBalances[accountAddress] + value < self.accountBalances[accountAddress]) {
                        // Prevent Overflow.
                        throw;
                }
                self.accountBalances[accountAddress] += value;
        }

        event _Deposit(address indexed _from, address indexed accountAddress, uint value);
        function Deposit(address _from, address accountAddress, uint value) public {
            _Deposit(_from, accountAddress, value);
        }

        function deposit(Bank storage self, address accountAddress, uint value) public returns (bool) {
                /*
                 *  Public API for depositing funds in a specified account.
                 */
                _addFunds(self, accountAddress, value);
                return true;
        }

        event _Withdrawal(address indexed accountAddress, uint value);
        function Withdrawal(address accountAddress, uint value) public {
            _Withdrawal(accountAddress, value);
        }

        event _InsufficientFunds(address indexed accountAddress, uint value, uint balance);
        function InsufficientFunds(address accountAddress, uint value, uint balance) public {
            _InsufficientFunds(accountAddress, value, balance);
        }

        function withdraw(Bank storage self, address accountAddress, uint value) public returns (bool) {
                /*
                 *  Public API for withdrawing funds.
                 */
                if (self.accountBalances[accountAddress] >= value) {
                        _deductFunds(self, accountAddress, value);
                        if (!accountAddress.send(value)) {
                                // Potentially sending money to a contract that
                                // has a fallback function.  So instead, try
                                // tranferring the funds with the call api.
                                if (!accountAddress.call.gas(msg.gas).value(value)()) {
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
