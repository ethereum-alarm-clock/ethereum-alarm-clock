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


## Call Tracking Tree

The ordering of upcoming calls is stored as a tree structure.  The tree has a
`rootNode` which represents the *base* of the tree.

Each tree node corresponds to a specific call which is guaranteed to be a 1-1
relationship.  There can however be multiple nodes which correspond to a
specific block since multiple calls can be scheduled for the same block.

Each tree node has a left child and a right child.  A child in the left
position is a call that should happen before the reference node.  A child in
the right position is a call that should happen after (or concurrently) with
the reference node.

The contract keeps track of the most recently called callKey as a reference
point for where to begin searching for the next call.
