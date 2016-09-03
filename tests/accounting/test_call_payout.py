from populus.utils.transactions import (
    wait_for_transaction_receipt,
)



#def test_execution_payment(deploy_client, deployed_contracts,
#                           deploy_future_block_call, denoms,
#                           FutureBlockCall, CallLib, SchedulerLib):
def test_execution_payment(unmigrated_chain, web3, FutureBlockCall, CallLib,
                           deploy_fbc):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    call = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 20,
        payment=12345,
        donation=54321,
    )

    while web3.eth.blockNumber < call.call().targetBlock():
        web3._requestManager.request_blocking("evm_mine", [])

    assert web3.eth.getBalance(client_contract.address) == 0

    assert client_contract.call().v_bool() is False
    assert client_contract.call().wasSuccessful() == 0

    call_txn_hash = client_contract.transact().doExecution(call.address)
    call_txn_receipt = wait_for_transaction_receipt(web3, call_txn_hash)

    assert client_contract.call().wasSuccessful() == 1
    assert client_contract.call().v_bool() is True

    log_entries = call_txn_receipt['logs']
    assert log_entries

    filter = CallLib().pastEvents('CallExecuted')
    events = filter.get()

    assert len(events) == 1
    event = events[0]

    assert 'gasCost' in event['args']
    expected_payout = 12345 + event['args']['gasCost']

    assert event['args']['payment'] == expected_payout
    assert web3.eth.getBalance(client_contract.address) == event['args']['payment']
