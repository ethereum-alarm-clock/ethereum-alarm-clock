import os

import pytest


NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


@pytest.fixture()
def request_tracker(unmigrated_chain, web3):
    chain = unmigrated_chain
    tracker = chain.get_contract('RequestTracker')
    return tracker


@pytest.fixture()
def request_factory(chain, web3):
    factory = chain.get_contract('RequestFactory')

    chain_code = web3.eth.getCode(factory.address)
    assert len(chain_code) > 10

    return factory


@pytest.fixture()
def request_lib(chain):
    return chain.get_contract('RequestLib')


@pytest.fixture()
def RequestLib(request_lib):
    return type(request_lib)


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
                txn_recorder,
                TransactionRequest):
    class _RequestData(object):
        _contract = None

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
                     toAddress=txn_recorder.address,
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

        def refresh(self):
            if not self._contract:
                raise ValueError("No contract set")
            self.__dict__.update(self.from_contract(self._contract).__dict__)

        @classmethod
        def from_contract(cls, txn_request):
            address_args, bool_args, uint_args, uint8_args = txn_request.call().requestData()
            call_data = txn_request.call().callData()
            instance = cls.from_deserialize(
                address_args, bool_args, uint_args, uint8_args, call_data,
            )
            instance._contract = txn_request
            return instance

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
def ValidationErrors():
    return (
        'InsufficientEndowment',
        'ReservedWindowBiggerThanExecutionWindow',
        'InvalidTemporalUnit',
        'ExecutionWindowTooSoon',
        'InvalidRequiredStackDepth',
        'CallGasTooHigh',
        'EmptyToAddress',
    )


@pytest.fixture()
def get_txn_request(chain,
                    web3,
                    request_factory,
                    RequestFactory,
                    TransactionRequest,
                    ValidationErrors,
                    logs_to_event_data,
                    TopicMap):
    def _get_txn_request(txn_hash):
        txn_receipt = chain.wait.for_receipt(txn_hash)
        request_created_filter = RequestFactory.pastEvents('RequestCreated', {
            'fromBlock': txn_receipt['blockNumber'],
            'toBlock': txn_receipt['blockNumber'],
        })
        request_created_logs = request_created_filter.get()
        if len(request_created_logs) == 0:
            error_filter = RequestFactory.pastEvents('ValidationError', {
                'fromBlock': txn_receipt['blockNumber'],
                'toBlock': txn_receipt['blockNumber'],
            })
            error_logs = error_filter.get()
            if error_logs:
                errors = [ValidationErrors[entry['args']['reason']] for entry in error_logs]
                raise AssertionError("ValidationError: {0}".format(', '.join(errors)))
            decoded_events = logs_to_event_data(txn_receipt['logs'])
            if decoded_events:
                raise AssertionError(
                    "Something went wrong.  The following events were found in"
                    "the logs for the given transaction hash:\n"
                    "{0}".format('\n'.join(decoded_events))
                )
            raise AssertionError("Something went wrong.  No 'RequestCreated' log entries found")

        log_data = request_created_logs[0]

        request_address = log_data['args']['request']
        txn_request = TransactionRequest(address=request_address)
        return txn_request
    return _get_txn_request


@pytest.fixture
def ABORT_REASONS_ENUM_KEYS():
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
def AbortReasons(ABORT_REASONS_ENUM_KEYS):
    return type('AbortReasons', (object,), {
        name: idx for idx, name in enumerate(ABORT_REASONS_ENUM_KEYS)
    })


@pytest.fixture()
def get_abort_data(chain, web3, RequestLib, logs_to_event_data):
    def _get_abort_data(execute_txn_hash):
        execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)
        abort_filter = RequestLib.pastEvents('Aborted', {
            'fromBlock': execute_txn_receipt['blockNumber'],
            'toBlock': execute_txn_receipt['blockNumber'],
        })
        abort_logs = abort_filter.get()
        if len(abort_logs) == 0:
            decoded_events = logs_to_event_data(execute_txn_receipt['logs'])
            if decoded_events:
                raise AssertionError(
                    "Something went wrong.  The following events were found in"
                    "the logs for the given transaction hash:\n"
                    "{0}".format('\n'.join(decoded_events))
                )
            raise AssertionError("Something went wrong.  No 'Aborted' log entries found")
        return abort_logs
    return _get_abort_data


@pytest.fixture()
def get_execute_data(chain, web3, RequestLib, ABORT_REASONS_ENUM_KEYS, get_abort_data):
    def _get_execute_data(execute_txn_hash):
        execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)
        execute_filter = RequestLib.pastEvents('Executed', {
            'fromBlock': execute_txn_receipt['blockNumber'],
            'toBlock': execute_txn_receipt['blockNumber'],
        })
        execute_logs = execute_filter.get()
        if len(execute_logs) == 0:
            abort_logs = get_abort_data(execute_txn_hash)
            errors = [ABORT_REASONS_ENUM_KEYS[entry['args']['reason']] for entry in abort_logs]
            raise AssertionError("Execution Failed: {0}".format(', '.join(errors)))
        execute_data = execute_logs[0]
        return execute_data
    return _get_execute_data


@pytest.fixture()
def get_claim_data(chain, web3, RequestLib, logs_to_event_data):
    def _get_claim_data(claim_txn_hash):
        claim_txn_receipt = chain.wait.for_receipt(claim_txn_hash)
        claim_filter = RequestLib.pastEvents('Claimed', {
            'fromBlock': claim_txn_receipt['blockNumber'],
            'toBlock': claim_txn_receipt['blockNumber'],
        })
        claim_logs = claim_filter.get()
        if len(claim_logs) == 0:
            decoded_events = logs_to_event_data(claim_txn_receipt['logs'])
            if decoded_events:
                raise AssertionError(
                    "Something went wrong.  The following events were found in"
                    "the logs for the given transaction hash:\n"
                    "{0}".format('\n'.join(decoded_events))
                )
            raise AssertionError("Something went wrong.  No 'Claimed' log entries found")
        claim_data = claim_logs[0]
        return claim_data
    return _get_claim_data


@pytest.fixture()
def get_cancel_data(chain, web3, RequestLib, logs_to_event_data):
    def _get_cancel_data(cancel_txn_hash):
        cancel_txn_receipt = chain.wait.for_receipt(cancel_txn_hash)
        cancel_filter = RequestLib.pastEvents('Cancelled', {
            'fromBlock': cancel_txn_receipt['blockNumber'],
            'toBlock': cancel_txn_receipt['blockNumber'],
        })
        cancel_logs = cancel_filter.get()
        if len(cancel_logs) == 0:
            decoded_events = logs_to_event_data(cancel_txn_receipt['logs'])
            if decoded_events:
                raise AssertionError(
                    "Something went wrong.  The following events were found in"
                    "the logs for the given transaction hash:\n"
                    "{0}".format('\n'.join(decoded_events))
                )
            raise AssertionError("Something went wrong.  No 'Cancelled' log entries found")
        cancel_data = cancel_logs[0]
        return cancel_data
    return _get_cancel_data


@pytest.fixture()
def logs_to_event_data(TopicMap):
    from web3.utils.events import (
        get_event_data,
    )

    def _logs_to_event_data(log_entries):
        return [
            get_event_data(TopicMap[log_entry['topics'][0]], log_entry)
            for log_entry in log_entries
            if log_entry['topics'] and log_entry['topics'][0] in TopicMap
        ]
    return _logs_to_event_data


@pytest.fixture()
def TopicMap(project):
    import itertools
    from web3.utils.abi import (
        filter_by_type,
        event_abi_to_log_topic,
    )
    all_events_abi = filter_by_type('event', itertools.chain.from_iterable(
        contract['abi'] for contract in project.compiled_contracts.values()
    ))
    topic_to_abi = {
        event_abi_to_log_topic(abi): abi
        for abi in all_events_abi
    }
    return topic_to_abi


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


@pytest.fixture()
def TransactionRecorder(test_contract_factories):
    return test_contract_factories.TransactionRecorder


@pytest.fixture()
def txn_recorder(chain, TransactionRecorder):
    chain.contract_factories['TransactionRecorder'] = TransactionRecorder
    return chain.get_contract('TransactionRecorder')


@pytest.fixture()
def Proxy(test_contract_factories):
    return test_contract_factories.Proxy


@pytest.fixture()
def proxy(chain, Proxy):
    chain.contract_factories['Proxy'] = Proxy
    return chain.get_contract('Proxy')
