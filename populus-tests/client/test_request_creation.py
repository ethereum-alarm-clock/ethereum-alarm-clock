import pytest

from click.testing import CliRunner


from alarm_client.cli import main


@pytest.fixture(autouse=True)
def deployed_contract_addresses(monkeypatch,
                                web3,
                                request_tracker,
                                request_factory,
                                payment_lib,
                                request_lib):
    monkeypatch.setenv('TRACKER_ADDRESS', request_tracker.address)
    monkeypatch.setenv('FACTORY_ADDRESS', request_factory.address)
    monkeypatch.setenv('REQUEST_LIB_ADDRESS', request_lib.address)
    monkeypatch.setenv('PAYMENT_LIB_ADDRESS', payment_lib.address)
    monkeypatch.setenv('PROVIDER', 'rpc')
    monkeypatch.setenv('RPC_HOST', web3.currentProvider.host)
    monkeypatch.setenv('RPC_PORT', web3.currentProvider.port)


def test_creating_a_request(chain,
                            web3,
                            txn_recorder,
                            request_factory,
                            TransactionRequest,
                            RequestData):
    runner = CliRunner()

    window_start = web3.eth.blockNumber + 50

    result = runner.invoke(main, [
        'request:create',
        '--to-address', txn_recorder.address,
        '--window-start', str(window_start),
        '--call-data', 'test-call-data',
        '--call-gas', '300000',
        '--call-value', '12345',
        '--no-confirm',
    ])
    print(result)

    created_filter = request_factory.pastEvents('RequestCreated')
    created_logs = created_filter.get()

    assert len(created_logs) == 1

    txn_request = TransactionRequest(address=created_logs[0]['args']['request'])

    assert txn_request.callData == 'test-call-data'
    assert txn_request.windowStart == window_start
    assert txn_request.callGas == 300000
    assert txn_request.callValue == 12345
    assert txn_request.toAddress == txn_recorder.address
