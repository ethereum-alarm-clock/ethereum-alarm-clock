from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "DepositsFunds",
]


def test_contract_depositing_funds(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    depositer = deployed_contracts.DepositsFunds
    coinbase = deploy_client.get_coinbase()

    assert alarm.getAccountBalance(depositer._meta.address) == 0

    wait_for_transaction(deploy_client, deploy_client.send_transaction(
        to=depositer._meta.address,
        value=1000000,
    ))

    assert deploy_client.get_balance(depositer._meta.address) == 1000000

    assert depositer.sentSuccessful() == 0

    wait_for_transaction(deploy_client, depositer.doIt.sendTransaction(
        alarm._meta.address,
        123,
    ))

    assert depositer.sentSuccessful() == 1

    assert alarm.getAccountBalance(coinbase) == 0
    assert alarm.getAccountBalance(depositer._meta.address) == 123

    wait_for_transaction(deploy_client, depositer.doIt.sendTransaction(
        alarm._meta.address,
        456,
    ))

    assert alarm.getAccountBalance(depositer._meta.address) == 579
