def test_scheduler_gets_what_is_leftover(unmigrated_chain, web3, denoms,
                                         deploy_fbc):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')
    CallLib = chain.get_contract_factory('CallLib')

    scheduler_address = web3.eth.accounts[1]
    web3.eth.sendTransaction({'to': scheduler_address, 'value': 20 * denoms.ether})

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 10,
        payment=12345,
        donation=54321,
        endowment=10 * denoms.ether,
        scheduler_address=scheduler_address,
    )

    chain.wait.for_block(fbc.call().targetBlock())

    before_balance = web3.eth.getBalance(scheduler_address)
    before_call_balance = web3.eth.getBalance(fbc.address)

    assert fbc.call().wasCalled() is False
    assert before_call_balance == 10 * denoms.ether

    execute_txn_h = fbc.transact({
        'from': web3.eth.coinbase,
    }).execute()
    chain.wait.for_receipt(execute_txn_h)

    assert fbc.call().wasCalled() is True
    assert web3.eth.getBalance(fbc.address) == 0

    execute_filter = CallLib.pastEvents(
        'CallExecuted',
        {'address', fbc.address},
    )
    execute_logs = execute_filter.get()
    assert len(execute_logs) == 1
    execute_log_data = execute_logs[0]

    after_balance = web3.eth.getBalance(scheduler_address)
    payout = execute_log_data['args']['payment']
    donation = execute_log_data['args']['donation']

    computed_reimbursement = after_balance - before_balance
    expected_reimbursement = before_call_balance - payout - donation

    assert computed_reimbursement == expected_reimbursement
