from eth_abi import (
    decode_abi,
    decode_single,
)
from web3.utils.abi import (
    get_abi_input_types,
    get_abi_input_names,
    get_indexed_event_inputs,
    exclude_indexed_event_inputs,
)
from populus.utils.transactions import (
    wait_for_transaction_receipt,
)


def get_event_data(event_abi, log_entry):
    log_topics = log_entry['topics'][1:]
    log_topics_abi = get_indexed_event_inputs(event_abi)
    log_topic_types = get_abi_input_types({'inputs': log_topics_abi})
    log_topic_names = get_abi_input_names({'inputs': log_topics_abi})

    log_data = log_entry['data']
    log_data_abi = exclude_indexed_event_inputs(event_abi)
    log_data_types = get_abi_input_types({'inputs': log_data_abi})
    log_data_names = get_abi_input_names({'inputs': log_data_abi})

    decoded_log_data = decode_abi(log_data_types, log_data)
    decoded_topic_data = [
        decode_single(topic_type, topic_data)
        for topic_type, topic_data
        in zip(log_topic_types, log_topics)
    ]

    decoded_data = {
        'topics': dict(zip(log_topic_names, decoded_topic_data)),
        'data': dict(zip(log_data_names, decoded_log_data)),
    }
    return decoded_data


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

    event_abi = CallLib.find_matching_event_abi('CallExecuted')

    event_data = get_event_data(event_abi, call_txn_receipt['logs'][0])

    expected_payout = 12345 + event_data['data']['gasCost']

    assert event_data['data']['payment'] == expected_payout
    assert web3.eth.getBalance(client_contract.address) == event_data['data']['payment']
