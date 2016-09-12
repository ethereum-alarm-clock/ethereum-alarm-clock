from web3.utils.encoding import decode_hex


MEASURED_VALUE = 80000


def test_minimum_call_gas(chain, web3, denoms, get_scheduled_fbc):
    client_contract = chain.get_contract('TestCallExecution')
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    _, sig, _ = client_contract._get_function_info('setBool')

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        contractAddress=client_contract.address,
        abiSignature=decode_hex(sig),
        targetBlock=target_block,
    )
    chain.wait.for_receipt(scheduling_txn_hash)
    fbc = get_scheduled_fbc(scheduling_txn_hash)

    chain.wait.for_block(fbc.call().firstClaimBlock() + 250)

    claim_txn_hash = fbc.transact({'value': 10 * denoms.ether}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    chain.wait.for_block(fbc.call().targetBlock())

    assert fbc.call().claimer() == web3.eth.coinbase
    assert client_contract.call().v_bool() is False

    execute_txn_hash = fbc.transact().execute()
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().wasCalled() is True
    assert fbc.call().wasSuccessful() is True

    actual = execute_txn_receipt['gasUsed']

    assert actual < MEASURED_VALUE
    assert MEASURED_VALUE - actual < 10000
    assert actual * 2 < scheduler.call().getMinimumCallGas()
