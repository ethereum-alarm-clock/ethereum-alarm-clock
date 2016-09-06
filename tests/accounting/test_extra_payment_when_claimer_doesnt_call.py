def test_claim_deposit_goes_to_caller(chain, web3, denoms, deploy_fbc):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')
    CallLib = chain.get_contract_factory('CallLib')

    target_block = web3.eth.blockNumber + 300

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
        payment=12345,
        donation=54321,
        endowment=denoms.ether * 100,
    )

    chain.wait.for_block(target_block - 10 - 255)

    # claim it
    deposit_amount = 2 * fbc.call().basePayment()
    claim_txn_h = fbc.transact({'value': deposit_amount}).claim()
    chain.wait.for_receipt(claim_txn_h)

    chain.wait.for_block(
        fbc.call().targetBlock() + scheduler.call().getCallWindowSize() + 1
    )
    executor_addr = web3.eth.accounts[1]
    before_balance = web3.eth.getBalance(executor_addr)

    assert fbc.call().wasCalled() is False
    assert fbc.call().claimer() == web3.eth.coinbase
    assert fbc.call().claimerDeposit() == deposit_amount

    ffa_txn_h = fbc.transact({'from': executor_addr}).execute()
    ffa_txn_r = chain.wait.for_receipt(ffa_txn_h)

    assert fbc.call().wasCalled() is True
    assert fbc.call().claimer() == web3.eth.coinbase
    assert fbc.call().claimerDeposit() == 0

    execute_filter = CallLib.pastEvents('CallExecuted', {'address': fbc.address})
    execute_logs = execute_filter.get()

    assert len(execute_logs) == 1
    execute_log_data = execute_logs[0]

    assert executor_addr == execute_log_data['args']['executor']

    after_balance = web3.eth.getBalance(executor_addr)
    expected_payout = deposit_amount + fbc.call().basePayment() + execute_log_data['args']['gasCost']

    assert abs(execute_log_data['args']['payment'] - expected_payout) < 100

    computed_payout = after_balance - before_balance
    actual_gas = ffa_txn_r['gasUsed']
    gas_diff = execute_log_data['args']['gasCost'] - actual_gas

    assert computed_payout == deposit_amount + 12345 + gas_diff
