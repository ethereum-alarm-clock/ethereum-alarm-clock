from web3.utils.string import (
    force_text,
)
from web3.utils.encoding import (
    decode_hex,
)


def test_basic_call_scheduling(chain, web3, get_scheduled_fbc, denoms):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 255 + 10 + 40

    _, sig, _ = client_contract._get_function_info('setBytes', ['some-byte-string'])
    call_data = client_contract.encodeABI('setBytes', ['some-byte-string'])

    base_payment = scheduler.call().defaultPayment()
    default_payment = scheduler.call().defaultPayment() // 100

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        contractAddress=client_contract.address,
        abiSignature=decode_hex(sig),
        callData=decode_hex(call_data),
        targetBlock=target_block,
    )
    scheduling_txn = web3.eth.getTransaction(scheduling_txn_hash)
    chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)

    # Sanity check for all of the queriable call values.
    assert fbc.call().targetBlock() == target_block
    assert fbc.call().gracePeriod() == 255
    assert fbc.call().requiredGas() == 200000
    assert fbc.call().callValue() == 0
    assert fbc.call().basePayment() == base_payment
    assert fbc.call().baseDonation() == default_payment
    assert fbc.call().schedulerAddress() == web3.eth.coinbase
    assert fbc.call().contractAddress() == client_contract.address
    assert fbc.call().abiSignature() == force_text(decode_hex(sig))
    assert fbc.call().callData() == force_text(decode_hex(call_data))
    assert fbc.call().anchorGasPrice() == scheduling_txn['gasPrice']
    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"
    assert fbc.call().claimAmount() == 0
    assert fbc.call().claimerDeposit() == 0
    assert fbc.call().wasSuccessful() is False
    assert fbc.call().wasCalled() is False
    assert fbc.call().isCancelled() is False
