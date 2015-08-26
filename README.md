# Ethereum Alarm Clock

Schedule function calls to occur at a specified block sometime in the future.


TODO:

- restrict public views.
- withdraw funds.  Need to be able to withdraw funds.
- `scheduleCall` need to enforce a minimum deposit size.  This should probably be set at maxGas.
- Charge a percentage fee of the gas used.
- After doing remote call, return the remaining deposit.
- Allow scheduling calls against someone other than `msg.sender`
- Addresses should be able to have an account balance that is used towards their calls.
- Account balance shouldn't be able to drop below a certain max.
- Could give a discount if the money comes from their balance rather than a deposit.
- Allow specifying `notAfterBlock` so that if things are running behind it
  doesn't get run after it should be.
