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


def test_scheduler_gets_what_is_leftover(deploy_client, deployed_contracts,
                                         deploy_future_block_call, denoms,
                                         deploy_coinbase, FutureBlockCall,
                                         CallLib, SchedulerLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    scheduler_address = "0x" + encode_hex(accounts[1])
    deploy_client.send_transaction(to=scheduler_address, value=20 * denoms.ether)

    target_block = deploy_client.get_block_number() + 1000

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
        payment=12345,
        donation=54321,
        endowment=denoms.ether * 10,
        scheduler_address=scheduler_address,
    )

    deploy_client.wait_for_block(target_block)

    before_balance = deploy_client.get_balance(scheduler_address)
    before_call_balance = call.get_balance()

    assert call.wasCalled() is False
    assert before_call_balance == 10 * denoms.ether

    ffa_txn_h = call.execute(_from=deploy_coinbase)
    ffa_txn_r = deploy_client.wait_for_transaction(ffa_txn_h)
    ffa_txn = deploy_client.get_transaction_by_hash(ffa_txn_h)

    assert call.wasCalled() is True
    assert call.get_balance() == 0

    execute_logs = CallLib.CallExecuted.get_transaction_logs(ffa_txn_h)
    assert len(execute_logs) == 1
    execute_data = CallLib.CallExecuted.get_log_data(execute_logs[0])

    after_balance = deploy_client.get_balance(scheduler_address)
    payout = execute_data['payment']
    donation = execute_data['donation']

    computed_reimbursement = after_balance - before_balance
    expected_reimbursement = before_call_balance - payout - donation

    assert computed_reimbursement == expected_reimbursement
