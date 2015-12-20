from ethereum import utils
from ethereum.tester import (
    accounts,
    encode_hex,
)


deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_claim_deposit_goes_to_caller(deploy_client, deployed_contracts,
                                      deploy_future_block_call, denoms,
                                      deploy_coinbase, FutureBlockCall,
                                      CallLib, SchedulerLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 1000

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
        payment=12345,
        fee=54321,
        endowment=denoms.ether * 100,
    )

    deploy_client.wait_for_block(target_block - 10 - 255)

    # claim it
    deposit_amount = 2 * call.basePayment()
    claim_txn_h = call.claim(value=deposit_amount)
    claim_txn_r = deploy_client.wait_for_transaction(claim_txn_h)

    deploy_client.wait_for_block(
        call.targetBlock() + deployed_contracts.Scheduler.getCallWindowSize() + 1
    )
    exe_addr = "0x" + encode_hex(accounts[1])
    before_balance = deploy_client.get_balance(exe_addr)
    before_call_balance = call.get_balance()

    assert call.wasCalled() is False
    assert call.bidder() == deploy_coinbase
    assert call.bidderDeposit() == deposit_amount

    ffa_txn_h = call.execute(_from=exe_addr)
    ffa_txn_r = deploy_client.wait_for_transaction(ffa_txn_h)
    ffa_txn = deploy_client.get_transaction_by_hash(ffa_txn_h)

    assert call.wasCalled() is True
    assert call.bidder() == deploy_coinbase
    assert call.bidderDeposit() == 0

    execute_logs = CallLib.CallExecuted.get_transaction_logs(ffa_txn_h)
    assert len(execute_logs) == 1
    execute_data = CallLib.CallExecuted.get_log_data(execute_logs[0])

    assert exe_addr in ffa_txn_r['logs'][0]['topics']

    after_balance = deploy_client.get_balance(exe_addr)
    expected_payout = deposit_amount + call.basePayment() + execute_data['gasCost']

    assert abs(execute_data['payment'] - expected_payout) < 100

    computed_payout = after_balance - before_balance
    actual_gas = int(ffa_txn_r['gasUsed'], 16)
    gas_diff = execute_data['gasCost'] - actual_gas

    assert computed_payout == deposit_amount + 12345 + gas_diff
