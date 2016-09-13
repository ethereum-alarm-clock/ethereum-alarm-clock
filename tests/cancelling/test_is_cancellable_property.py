class State(object):
    Pending = 0
    Unclaimed = 1
    Claimed = 2
    Frozen = 3
    Callable = 4
    Executed = 5
    Cancelled = 6
    Missed = 7


def test_is_cancellable_before_call_window(chain, web3, deploy_fbc):
    fbc = deploy_fbc(target_block=web3.eth.blockNumber + 300)

    assert fbc.call().isCancellable() is True

    # false for non-scheduler account
    assert fbc.call({'from': web3.eth.accounts[1]}).isCancellable() is False

    cancel_txn_hash = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    assert fbc.call().isCancellable() is False
    assert fbc.call({'from': web3.eth.accounts[1]}).isCancellable() is False


def test_not_cancellable_during_claim_window_and_call_window(chain,
                                                             web3,
                                                             denoms,
                                                             deploy_fbc):
    fbc = deploy_fbc(target_block=web3.eth.blockNumber + 300)

    assert fbc.call().state() == State.Pending
    assert fbc.call().isCancellable() is True

    # false for non-scheduler account
    assert fbc.call({'from': web3.eth.accounts[1]}).isCancellable() is False

    chain.wait.for_block(fbc.call().firstClaimBlock())

    assert fbc.call().isCancellable() is False

    claim_txn_hash = fbc.transact({'value': 2 * denoms.ether}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    assert fbc.call().state() == State.Claimed
    assert fbc.call().isCancellable() is False

    chain.wait.for_block(fbc.call().targetBlock() - 9)

    assert fbc.call().state() == State.Frozen
    assert fbc.call().isCancellable() is False

    chain.wait.for_block(fbc.call().targetBlock())

    assert fbc.call().state() == State.Callable
    assert fbc.call().isCancellable() is False

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().state() == State.Executed
    assert fbc.call().isCancellable() is False


def test_cancellable_after_call_window_if_missed(chain, web3, deploy_fbc):
    fbc = deploy_fbc(target_block=web3.eth.blockNumber + 300)

    assert fbc.call().state() == State.Pending

    chain.wait.for_block(fbc.call().targetBlock() + fbc.call().gracePeriod())

    assert fbc.call().state() == State.Missed

    assert fbc.call().isCancellable() is True
    # true for non-scheduler account
    assert fbc.call({'from': web3.eth.accounts[1]}).isCancellable() is True

    cancel_txn_hash = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    assert fbc.call().isCancellable() is False
    assert fbc.call({'from': web3.eth.accounts[1]}).isCancellable() is False
