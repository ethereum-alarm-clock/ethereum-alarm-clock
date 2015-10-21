from populus.contracts import (
    get_max_gas,
    deploy_contract,
)
from populus.utils import (
    wait_for_transaction,
    get_contract_address_from_txn,
)


deploy_contracts = [
    "Alarm",
    "JoinsPool",
    "NoArgs",
]


def test_free_for_all_window_awards_mega_bonus(deploy_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs
    joiner_a = deployed_contracts.JoinsPool

    coinbase = deploy_client.get_coinbase()

    deploy_txn = deploy_contract(deploy_client, contracts.JoinsPool, _from=coinbase, gas=get_max_gas(deploy_client))
    joiner_b = contracts.JoinsPool(get_contract_address_from_txn(deploy_client, deploy_txn, 30), deploy_client)
    coinbase = deploy_client.get_coinbase()

    # Put in our deposit with the alarm contract.
    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(deploy_client, joiner_a.setCallerPool.sendTransaction(alarm._meta.address))
    wait_for_transaction(deploy_client, joiner_b.setCallerPool.sendTransaction(alarm._meta.address))

    assert alarm.getBondBalance(coinbase) == 0
    deposit_amount = alarm.getMinimumBond() * 10
    # Put in our bond
    wait_for_transaction(
        deploy_client, alarm.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put contract A's bond in
    wait_for_transaction(
        deploy_client,
        deploy_client.send_transaction(to=joiner_a._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        deploy_client, joiner_a.deposit.sendTransaction(deposit_amount)
    )
    # Put contract B's bond in
    wait_for_transaction(
        deploy_client,
        deploy_client.send_transaction(to=joiner_b._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        deploy_client, joiner_b.deposit.sendTransaction(deposit_amount)
    )

    # All join the pool
    wait_for_transaction(deploy_client, joiner_a.enter.sendTransaction())
    wait_for_transaction(deploy_client, joiner_b.enter.sendTransaction())
    wait_for_transaction(deploy_client, alarm.enterPool.sendTransaction())

    # New pool is formed but not active
    first_generation_id = alarm.getNextGenerationId()
    assert first_generation_id > 0

    # Wait for it to become active
    deploy_client.wait_for_block(alarm.getGenerationStartAt(first_generation_id), 240)

    # We should both be in the pool
    assert alarm.getCurrentGenerationId() == first_generation_id
    assert alarm.isInGeneration(joiner_a._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(joiner_b._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is True

    # Schedule the function call.
    txn_hash = client_contract.setGracePeriod.sendTransaction(alarm.getMinimumGracePeriod())
    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    target_block = alarm.getCallTargetBlock(call_key)
    grace_period = alarm.getCallGracePeriod(call_key)

    deploy_client.wait_for_block(target_block + grace_period - 4, 300)

    my_before_balance = alarm.getBondBalance(coinbase)
    before_balance_a = alarm.getBondBalance(joiner_a._meta.address)
    before_balance_b = alarm.getBondBalance(joiner_b._meta.address)
    assert alarm.checkIfCalled(call_key) is False

    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)
    call_block = deploy_client.get_block_by_hash(call_txn_receipt['blockHash'])

    my_after_balance = alarm.getBondBalance(coinbase)
    after_balance_a = alarm.getBondBalance(joiner_a._meta.address)
    after_balance_b = alarm.getBondBalance(joiner_b._meta.address)
    assert alarm.checkIfCalled(call_key) is True

    assert after_balance_a < before_balance_a
    assert after_balance_b < before_balance_b

    minimum_bond = int(call_block['gasLimit'], 16) * int(call_txn['gasPrice'], 16)
    assert after_balance_a == before_balance_a - minimum_bond
    assert after_balance_b == before_balance_b - minimum_bond

    assert my_after_balance > my_before_balance
    assert my_after_balance == my_before_balance + 2 * minimum_bond

    assert alarm.getNextGenerationId() == 0
