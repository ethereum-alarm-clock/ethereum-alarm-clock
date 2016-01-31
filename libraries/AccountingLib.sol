// Accounting v0.1 (not the same as the 0.1 release of this library)

/// @title Accounting Lib - Accounting utilities
/// @author Piper Merriam - <pipermerriam@gmail.com>
library AccountingLib {
        /*
         *  Address: 0x89efe605e9ecbe22849cd85d5449cc946c26f8f3
         */
        struct Bank {
            mapping (address => uint) accountBalances;
        }

        /// @dev Low level method for adding funds to an account.  Protects against overflow.
        /// @param self The Bank instance to operate on.
        /// @param accountAddress The address of the account the funds should be added to.
        /// @param value The amount that should be added to the account.
        function addFunds(Bank storage self, address accountAddress, uint value) public {
                if (self.accountBalances[accountAddress] + value < self.accountBalances[accountAddress]) {
                        // Prevent Overflow.
                        throw;
                }
                self.accountBalances[accountAddress] += value;
        }

        event _Deposit(address indexed _from, address indexed accountAddress, uint value);
        /// @dev Function wrapper around the _Deposit event so that it can be used by contracts.  Can be used to log a deposit to an account.
        /// @param _from The address that deposited the funds.
        /// @param accountAddress The address of the account the funds were added to.
        /// @param value The amount that was added to the account.
        function Deposit(address _from, address accountAddress, uint value) public {
            _Deposit(_from, accountAddress, value);
        }


        /// @dev Safe function for depositing funds.  Returns boolean for whether the deposit was successful
        /// @param self The Bank instance to operate on.
        /// @param accountAddress The address of the account the funds should be added to.
        /// @param value The amount that should be added to the account.
        function deposit(Bank storage self, address accountAddress, uint value) public returns (bool) {
                addFunds(self, accountAddress, value);
                return true;
        }

        event _Withdrawal(address indexed accountAddress, uint value);

        /// @dev Function wrapper around the _Withdrawal event so that it can be used by contracts.  Can be used to log a withdrawl from an account.
        /// @param accountAddress The address of the account the funds were withdrawn from.
        /// @param value The amount that was withdrawn to the account.
        function Withdrawal(address accountAddress, uint value) public {
            _Withdrawal(accountAddress, value);
        }

        event _InsufficientFunds(address indexed accountAddress, uint value, uint balance);

        /// @dev Function wrapper around the _InsufficientFunds event so that it can be used by contracts.  Can be used to log a failed withdrawl from an account.
        /// @param accountAddress The address of the account the funds were to be withdrawn from.
        /// @param value The amount that was attempted to be withdrawn from the account.
        /// @param balance The current balance of the account.
        function InsufficientFunds(address accountAddress, uint value, uint balance) public {
            _InsufficientFunds(accountAddress, value, balance);
        }

        /// @dev Low level method for removing funds from an account.  Protects against underflow.
        /// @param self The Bank instance to operate on.
        /// @param accountAddress The address of the account the funds should be deducted from.
        /// @param value The amount that should be deducted from the account.
        function deductFunds(Bank storage self, address accountAddress, uint value) public {
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

        /// @dev Safe function for withdrawing funds.  Returns boolean for whether the deposit was successful as well as sending the amount in ether to the account address.
        /// @param self The Bank instance to operate on.
        /// @param accountAddress The address of the account the funds should be withdrawn from.
        /// @param value The amount that should be withdrawn from the account.
        function withdraw(Bank storage self, address accountAddress, uint value) public returns (bool) {
                /*
                 *  Public API for withdrawing funds.
                 */
                if (self.accountBalances[accountAddress] >= value) {
                        deductFunds(self, accountAddress, value);
                        if (!accountAddress.send(value)) {
                                // Potentially sending money to a contract that
                                // has a fallback function.  So instead, try
                                // tranferring the funds with the call api.
                                if (!accountAddress.call.value(value)()) {
                                        // Revert the entire transaction.  No
                                        // need to destroy the funds.
                                        throw;
                                }
                        }
                        return true;
                }
                return false;
        }

        uint constant DEFAULT_SEND_GAS = 100000;

        function sendRobust(address toAddress, uint value) public returns (bool) {
                if (msg.gas < DEFAULT_SEND_GAS) {
                    return sendRobust(toAddress, value, msg.gas);
                }
                return sendRobust(toAddress, value, DEFAULT_SEND_GAS);
        }

        function sendRobust(address toAddress, uint value, uint maxGas) public returns (bool) {
                if (value > 0 && !toAddress.send(value)) {
                        // Potentially sending money to a contract that
                        // has a fallback function.  So instead, try
                        // tranferring the funds with the call api.
                        if (!toAddress.call.gas(maxGas).value(value)()) {
                                return false;
                        }
                }
                return true;
        }
}
