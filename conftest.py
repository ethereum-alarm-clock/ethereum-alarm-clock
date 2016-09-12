import pytest

from web3.utils.encoding import (
    decode_hex,
)


@pytest.fixture
def FutureBlockCall(chain):
    return chain.get_contract_factory('FutureBlockCall')


@pytest.fixture
def CallLib(chain):
    return chain.get_contract_factory('CallLib')


@pytest.fixture
def SchedulerLib(chain):
    return chain.get_contract_factory('SchedulerLib')


def get_block_gas_limit(web3):
    latest_block = web3.eth.getBlock(web3.eth.blockNumber)
    return latest_block['gasLimit']


@pytest.fixture
def deploy_fbc(unmigrated_chain, web3, FutureBlockCall):
    chain = unmigrated_chain

    def _deploy_fbc(contract=None,
                    method_name=None,
                    abi_signature=None,
                    arguments=None,
                    scheduler_address=None,
                    target_block=None,
                    grace_period=255,
                    required_gas=1000000,
                    payment=1,
                    donation=1,
                    endowment=None,
                    call_data="",
                    require_depth=0,
                    call_value=0):
        if arguments is not None and call_data:
            raise ValueError("Cannot specify both arguments and call_data")
        elif arguments is not None and not method_name:
            raise ValueError("Method name must be provided if providing arguments")

        if endowment is None:
            endowment = (
                get_block_gas_limit(web3) *
                web3.eth.gasPrice +
                payment +
                donation +
                call_value
            )

        if target_block is None:
            target_block = web3.eth.blockNumber

        if scheduler_address is None:
            scheduler_address = web3.eth.coinbase

        if contract is None:
            contract_address = web3.eth.coinbase
        else:
            contract_address = contract.address

        if method_name is not None:
            fn_abi, fn_selector, _ = contract._get_function_info(method_name, arguments)

            if abi_signature is None:
                abi_signature = decode_hex(fn_selector)

            if not call_data and arguments:
                hex_call_data = contract.encodeABI(method_name, arguments)
                call_data = decode_hex(hex_call_data)

        if abi_signature is None:
            abi_signature = ""

        deploy_txn_hash = FutureBlockCall.deploy(
            {'value': endowment},
            [
                scheduler_address,
                target_block,
                grace_period,
                contract_address,
                abi_signature,
                call_data,
                call_value,
                required_gas,
                require_depth,
                payment,
                donation,
            ],
        )

        contract_address = chain.wait.for_contract_address(deploy_txn_hash)
        fbc = FutureBlockCall(address=contract_address)
        return fbc
    return _deploy_fbc


@pytest.fixture
def Canary(unmigrated_chain):
    return unmigrated_chain.get_contract_factory('Canary')


@pytest.fixture()
def deploy_canary(chain, web3, denoms, Canary):
    def _deploy_canary(endowment=None,
                       scheduler_address=None,
                       frequency=480,
                       deploy_from=None):
        if scheduler_address is None:
            scheduler = chain.get_contract('Scheduler')
            scheduler_address = scheduler.address

        if endowment is None:
            endowment = 5 * denoms.ether

        transaction = {'value': endowment}

        if deploy_from is not None:
            transaction['from'] = deploy_from

        deploy_txn_hash = Canary.deploy(
            transaction=transaction,
            arguments=(scheduler_address, frequency),
        )
        canary_address = chain.wait.for_contract_address(deploy_txn_hash)

        canary = Canary(address=canary_address)
        return canary
    return _deploy_canary


#@pytest.fixture()
#def canary(deploy_canary_contract):
#    return deploy_canary_contract()
#
#
#@pytest.fixture(scope="module")
#def get_call(SchedulerLib, FutureBlockCall, deploy_client):
#    def _get_call(txn_hash):
#        call_scheduled_logs = SchedulerLib.CallScheduled.get_transaction_logs(txn_hash)
#        if not len(call_scheduled_logs):
#            call_rejected_logs = SchedulerLib.CallRejected.get_transaction_logs(txn_hash)
#            if len(call_rejected_logs):
#                reject_data = SchedulerLib.CallRejected.get_log_data(call_rejected_logs[0])
#                raise ValueError("CallRejected: {0}".format(reject_data))
#            raise ValueError("No scheduled call found")
#        call_scheduled_data = SchedulerLib.CallScheduled.get_log_data(call_scheduled_logs[0])
#
#        call_address = call_scheduled_data['call_address']
#        call = FutureBlockCall(call_address, deploy_client)
#        return call
#    return _get_call
#
#
#@pytest.fixture(scope="module")
#def get_call_rejection_data(SchedulerLib):
#    def _get_rejection_data(txn_hash):
#        rejection_logs = SchedulerLib.CallRejected.get_transaction_logs(txn_hash)
#        assert len(rejection_logs) == 1
#        rejection_data = SchedulerLib.CallRejected.get_log_data(rejection_logs[0])
#
#        return rejection_data
#    return _get_rejection_data
#
#
#@pytest.fixture(scope="module")
#def get_execution_data(CallLib):
#    def _get_execution_data(txn_hash):
#        execution_logs = CallLib.CallExecuted.get_transaction_logs(txn_hash)
#        assert len(execution_logs) == 1
#        execution_data = CallLib.CallExecuted.get_log_data(execution_logs[0])
#
#        return execution_data
#    return _get_execution_data

@pytest.fixture()
def denoms():
    from web3.utils.currency import units
    int_units = {
        key: int(value)
        for key, value in units.items()
    }
    return type('denoms', (object,), int_units)


@pytest.fixture()
def get_scheduled_fbc(chain, web3):
    scheduler = chain.get_contract('Scheduler')
    SchedulerLib = chain.get_contract_factory('SchedulerLib')
    FutureBlockCall = chain.get_contract_factory('FutureBlockCall')

    def _get_scheduled_fbc(scheduling_txn_hash):
        schedule_receipt = chain.wait.for_receipt(scheduling_txn_hash)

        schedule_filter = SchedulerLib.on(
            'CallScheduled',
            {
                'address': scheduler.address,
                'fromBlock': schedule_receipt['blockNumber'],
                'toBlock': schedule_receipt['blockNumber'],
            },
        )
        schedule_events = schedule_filter.get()
        assert len(schedule_events) == 1
        schedule_event_data = schedule_events[0]
        fbc_address = schedule_event_data['args']['call_address']

        fbc = FutureBlockCall(address=fbc_address)
        return fbc
    return _get_scheduled_fbc


@pytest.fixture()
def get_4byte_selector():
    from web3.utils.encoding import (
        decode_hex,
    )
    from web3.utils.abi import (
        function_abi_to_4byte_selector,
    )

    def _get_4byte_selector(contract, fn_name, args=None, kwargs=None):
        fn_abi = contract._find_matching_fn_abi(fn_name, args=args, kwargs=kwargs)
        fn_4byte_selector = decode_hex(function_abi_to_4byte_selector(fn_abi))
        return fn_4byte_selector
    return _get_4byte_selector


@pytest.fixture()
def CallStates():
    class States(object):
        Pending = 0
        Unclaimed = 1
        Claimed = 2
        Frozen = 3
        Callable = 4
        Executed = 5
        Cancelled = 6
        Missed = 7
    return States
