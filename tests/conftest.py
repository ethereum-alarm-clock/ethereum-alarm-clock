import os

import pytest


NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


@pytest.fixture()
def request_tracker(unmigrated_chain, web3):
    chain = unmigrated_chain
    tracker = chain.get_contract('RequestTracker')
    return tracker


@pytest.fixture()
def request_factory(chain, web3, request_tracker):
    import time
    start_at = time.time()
    print("Start:", start_at)
    factory = chain.get_contract('RequestFactory', deploy_args=[request_tracker.address])

    chain_code = web3.eth.getCode(factory.address)
    assert len(chain_code) > 10
    print("End:", time.time(), "Elapsed:", time.time() - start_at)

    return factory


@pytest.fixture()
def RequestLib(chain):
    return type(chain.get_contract('RequestLib'))


@pytest.fixture()
def TransactionRequest(chain):
    # force lazy deployment of the dependencies for the TransactionRequest
    # contract.
    chain.get_contract('RequestLib')
    TransactionRequest = chain.get_contract_factory('TransactionRequest')
    return TransactionRequest


@pytest.fixture()
def RequestFactory(chain, request_factory):
    return type(request_factory)


@pytest.fixture()
def denoms():
    from web3.utils.currency import units
    int_units = {
        key: int(value)
        for key, value in units.items()
    }
    return type('denoms', (object,), int_units)


@pytest.fixture()
def RequestData(chain,
                web3,
                request_factory,
                get_txn_request,
                denoms,
                TransactionRequest):
    class _RequestData(object):
        def __init__(self,
                     # claim
                     claimedBy=NULL_ADDRESS,
                     claimDeposit=0,
                     paymentModifier=0,
                     # meta
                     createdBy=web3.eth.coinbase,
                     owner=web3.eth.coinbase,
                     isCancelled=False,
                     wasCalled=False,
                     wasSuccessful=False,
                     # payment
                     anchorGasPrice=web3.eth.gasPrice,
                     donation=12345,
                     donationBenefactor='0xd3cda913deb6f67967b99d67acdfa1712c293601',
                     donationOwed=0,
                     payment=54321,
                     paymentBenefactor=NULL_ADDRESS,
                     paymentOwed=0,
                     # txnData
                     callData="",
                     toAddress=NULL_ADDRESS,
                     callGas=1000000,
                     callValue=0,
                     requiredStackDepth=0,
                     # schedule
                     claimWindowSize=255,
                     freezePeriod=None,
                     windowStart=None,
                     windowSize=None,
                     reservedWindowSize=None,
                     temporalUnit=1):

            if freezePeriod is None:
                if temporalUnit == 0:
                    freezePeriod = 10 * 17
                else:
                    freezePeriod = 10

            if windowSize is None:
                if temporalUnit == 0:
                    windowSize = 255 * 17
                else:
                    windowSize = 255

            if windowStart is None:
                if temporalUnit == 0:
                    windowStart = web3.eth.getBlock('latest')['timestamp'] + freezePeriod
                else:
                    windowStart = web3.eth.blockNumber + freezePeriod

            if reservedWindowSize is None:
                if temporalUnit == 0:
                    reservedWindowSize = 16 * 17
                else:
                    reservedWindowSize = 16

            self.claimData = type('claimData', (object,), {
                'claimedBy': claimedBy,
                'claimDeposit': claimDeposit,
                'paymentModifier': paymentModifier,
            })
            self.meta = type('meta', (object,), {
                'createdBy': createdBy,
                'owner': owner,
                'isCancelled': isCancelled,
                'wasCalled': wasCalled,
                'wasSuccessful': wasSuccessful,
            })
            self.paymentData = type('paymentData', (object,), {
                'anchorGasPrice': anchorGasPrice,
                'donation': donation,
                'donationBenefactor': donationBenefactor,
                'donationOwed': donationOwed,
                'payment': payment,
                'paymentBenefactor': paymentBenefactor,
                'paymentOwed': paymentOwed,
            })
            self.txnData = type('txnData', (object,), {
                'callData': callData,
                'toAddress': toAddress,
                'callGas': callGas,
                'callValue': callValue,
                'requiredStackDepth': requiredStackDepth,
            })
            self.schedule = type('schedule', (object,), {
                'claimWindowSize': claimWindowSize,
                'freezePeriod': freezePeriod,
                'reservedWindowSize': reservedWindowSize,
                'temporalUnit': temporalUnit,
                'windowStart': windowStart,
                'windowSize': windowSize,
            })

        def to_factory_kwargs(self):
            return {
                'addressArgs': [
                    self.meta.owner,
                    self.paymentData.donationBenefactor,
                    self.txnData.toAddress,
                ],
                'uintArgs': [
                    self.paymentData.donation,
                    self.paymentData.payment,
                    self.schedule.claimWindowSize,
                    self.schedule.freezePeriod,
                    self.schedule.reservedWindowSize,
                    self.schedule.temporalUnit,
                    self.schedule.windowStart,
                    self.schedule.windowSize,
                    self.txnData.callGas,
                    self.txnData.callValue,
                    self.txnData.requiredStackDepth,
                ],
                'callData': self.txnData.callData,
            }

        def deploy_via_factory(self, deploy_txn=None):
            if deploy_txn is None:
                deploy_txn = {'value': 10 * denoms.ether}
            create_txn_hash = request_factory.transact(
                deploy_txn,
            ).createRequest(
                **self.to_factory_kwargs()
            )
            txn_request = get_txn_request(create_txn_hash)
            return txn_request

        def to_init_kwargs(self):
            return {
                'addressArgs': [
                    self.meta.createdBy,
                    self.meta.owner,
                    self.paymentData.donationBenefactor,
                    self.txnData.toAddress,
                ],
                'uintArgs': [
                    self.paymentData.donation,
                    self.paymentData.payment,
                    self.schedule.claimWindowSize,
                    self.schedule.freezePeriod,
                    self.schedule.reservedWindowSize,
                    self.schedule.temporalUnit,
                    self.schedule.windowStart,
                    self.schedule.windowSize,
                    self.txnData.callGas,
                    self.txnData.callValue,
                    self.txnData.requiredStackDepth,
                ],
                'callData': self.txnData.callData,
            }

        def direct_deploy(self, deploy_txn=None):
            if deploy_txn is None:
                deploy_txn = {'value': 10 * denoms.ether}
            deploy_txn_hash = TransactionRequest.deploy(
                transaction=deploy_txn,
                kwargs=self.to_init_kwargs(),
            )
            txn_request_address = chain.wait.for_contract_address(deploy_txn_hash)
            return TransactionRequest(address=txn_request_address)

        @classmethod
        def from_contract(cls, txn_request):
            address_args, bool_args, uint_args, uint8_args = txn_request.call().requestData()
            call_data = txn_request.call().callData()
            return cls.from_deserialize(
                address_args, bool_args, uint_args, uint8_args, call_data,
            )

        @classmethod
        def from_deserialize(cls, address_args, bool_args, uint_args, uint8_args, call_data):
            init_kwargs = {
                'claimedBy': address_args[0],
                'createdBy': address_args[1],
                'owner': address_args[2],
                'donationBenefactor': address_args[3],
                'paymentBenefactor': address_args[4],
                'toAddress': address_args[5],
                'wasCalled': bool_args[1],
                'wasSuccessful': bool_args[2],
                'isCancelled': bool_args[0],
                'paymentModifier': uint8_args[0],
                'claimDeposit': uint_args[0],
                'anchorGasPrice': uint_args[1],
                'donation': uint_args[2],
                'donationOwed': uint_args[3],
                'payment': uint_args[4],
                'paymentOwed': uint_args[5],
                'claimWindowSize': uint_args[6],
                'freezePeriod': uint_args[7],
                'reservedWindowSize': uint_args[8],
                'temporalUnit': uint_args[9],
                'windowStart': uint_args[10],
                'windowSize': uint_args[11],
                'callGas': uint_args[12],
                'callValue': uint_args[13],
                'requiredStackDepth': uint_args[14],
                'callData': call_data,
            }
            return cls(**init_kwargs)
    return _RequestData


@pytest.fixture()
def get_txn_request(chain, web3, request_factory, RequestFactory, TransactionRequest):
    def _get_txn_request(txn_hash):
        txn_receipt = chain.wait.for_receipt(txn_hash)
        request_created_filter = RequestFactory.pastEvents('RequestCreated', {
            'fromBlock': txn_receipt['blockNumber'],
            'toBlock': txn_receipt['blockNumber'],
            'address': request_factory.address,
        })
        request_created_logs = request_created_filter.get()
        assert len(request_created_logs) == 1

        log_data = request_created_logs[0]

        request_address = log_data['args']['request']
        txn_request = TransactionRequest(address=request_address)
        return txn_request
    return _get_txn_request


@pytest.fixture()
def AbortReasons():
    return (
        'WasCancelled',
        'AlreadyCalled',
        'BeforeCallWindow',
        'AfterCallWindow',
        'ReservedForClaimer',
        'StackTooDeep',
        'InsufficientGas',
    )


@pytest.fixture()
def get_execute_data(chain, web3, RequestLib, AbortReasons):
    def _get_execute_data(execute_txn_hash):
        execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)
        execute_filter = RequestLib.pastEvents('Executed', {
            'fromBlock': execute_txn_receipt['blockNumber'],
            'toBlock': execute_txn_receipt['blockNumber'],
        })
        execute_logs = execute_filter.get()
        if len(execute_logs) == 0:
            abort_filter = RequestLib.pastEvents('Aborted', {
                'fromBlock': execute_txn_receipt['blockNumber'],
                'toBlock': execute_txn_receipt['blockNumber'],
            })
            abort_logs = abort_filter.get()
            if abort_logs:
                errors = [AbortReasons[entry['args']['reason']] for entry in abort_logs]
                raise AssertionError("Execution Failed: {0}".format(', '.join(errors)))
        assert len(execute_logs) == 1
        execute_data = execute_logs[0]
        return execute_data
    return _get_execute_data


@pytest.fixture()
def test_contract_factories(web3):
    from solc import compile_files
    from populus.utils.filesystem import recursive_find_files
    from populus.utils.contracts import (
        package_contracts,
        construct_contract_factories,
    )

    base_tests_dir = os.path.dirname(__file__)

    solidity_source_files = recursive_find_files(base_tests_dir, '*.sol')
    compiled_contracts = compile_files(solidity_source_files)
    test_contract_factories = construct_contract_factories(web3, compiled_contracts)
    return package_contracts(test_contract_factories)


@pytest.fixture()
def ErrorGenerator(test_contract_factories):
    return test_contract_factories.ErrorGenerator


@pytest.fixture()
def error_generator(chain, ErrorGenerator):
    chain.contract_factories['ErrorGenerator'] = ErrorGenerator
    return chain.get_contract('ErrorGenerator')
