from web3.utils.encoding import (
    decode_hex,
)
from web3.utils.abi import (
    function_abi_to_4byte_selector,
)


def test_early_claim_decreases_default_payment(chain, web3, denoms):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')
    SchedulerLib = chain.get_contract_factory('SchedulerLib')
    FutureBlockCall = chain.get_contract_factory('FutureBlockCall')

    target_block = web3.eth.blockNumber + 300

    bytes4_selector = decode_hex(function_abi_to_4byte_selector(client_contract.find_matching_fn_abi(
        'noop',
    )))
    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
        #'gas': 3000000,
    }).scheduleCall(
        client_contract.address,
        bytes4_selector,
        target_block,
    )

    scheduling_receipt = chain.wait.for_receipt(scheduling_txn_hash)

    event_filter = SchedulerLib.pastEvents('CallScheduled', {'address': scheduler.address})
    events = event_filter.get()
    assert len(events) == 1
    event_data = events[0]

    call_address = event_data['args']['call_address']
    call = FutureBlockCall(address=call_address)

    chain.wait.for_block(call.call().firstClaimBlock())

    claim_txn_hash = call.transact({'value': 10 * denoms.ether}).claim()
    claim_txn_receipt = chain.wait.for_receipt(claim_txn_hash)

    assert call.call().claimer() == web3.eth.coinbase

    chain.wait.for_block(target_block)

    default_payment_before = scheduler.call().defaultPayment()

    execute_txn_hash = call.transact().execute()
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    assert call.call().wasCalled()

    expected = default_payment_before * 9999 / 10000
    actual = scheduler.call().defaultPayment()

    assert actual < default_payment_before
    assert actual == expected
