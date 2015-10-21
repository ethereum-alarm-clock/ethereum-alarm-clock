from populus.utils import wait_for_transaction


def test_withdrawing_with_insufficient_funds(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    assert alarm.getAccountBalance.call(coinbase) == 0

    wait_for_transaction(deploy_client, alarm.deposit.sendTransaction(coinbase, value=1000))

    assert alarm.getAccountBalance.call(coinbase) == 1000

    wait_for_transaction(deploy_client, alarm.withdraw.sendTransaction(1001))

    assert alarm.getAccountBalance.call(coinbase) == 1000

    wait_for_transaction(deploy_client, alarm.withdraw.sendTransaction(1000))

    assert alarm.getAccountBalance.call(coinbase) == 0
