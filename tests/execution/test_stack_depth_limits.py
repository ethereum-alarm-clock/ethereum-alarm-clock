import pytest

from ethereum import abi
from ethereum import utils
from ethereum.tester import TransactionFailed


deploy_contracts = [
    "Scheduler",
    "TestErrors",
]


MAX_DEPTH = 2048

OUTER_MAX = 1020
CHECK_MAX = 1022
INNER_MAX = 1022


def test_stack_depth(deploy_client, deployed_contracts,
                     deploy_future_block_call):
    """
    This function is useful for finding out what the limits are for stack depth
    protection.
    """
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestErrors

    def deploy_call(depth_check, depth_inner):
        call = deploy_future_block_call(
            client_contract.doStackExtension,
            call_data=client_contract.doStackExtension.abi_args_signature([depth_inner]),
            require_depth=depth_check,
        )
        deploy_client.wait_for_transaction(client_contract.reset())
        deploy_client.wait_for_transaction(client_contract.setCallAddress(call._meta.address))
        deploy_client.wait_for_block(call.targetBlock())
        return call

    def check(call, depth_outer):
        assert client_contract.value() is False

        call_txn_hash = client_contract.proxyCall(depth_outer)
        call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

        return call.wasCalled() and client_contract.value()

    def find_maxima(attr, **defaults):
        left = 0
        right = MAX_DEPTH
        while left < right:
            depth = (left + right) / 2
            defaults[attr] = depth
            call = deploy_call(defaults['depth_check'], defaults['depth_inner'])

            if check(call, defaults['depth_outer']):
                if left == depth:
                    break
                left = depth
            else:
                if right == depth:
                    break
                right = depth

        assert depth != 0 and depth != MAX_DEPTH
        return depth

    outer_max = find_maxima('depth_outer', depth_check=0, depth_inner=0)
    print "outer max", outer_max
    check_max = find_maxima('depth_check', depth_outer=0, depth_inner=0)
    print "check max", check_max
    inner_max = find_maxima('depth_inner', depth_outer=0, depth_check=0)
    print "inner max", inner_max

    assert outer_max == OUTER_MAX
    assert check_max == CHECK_MAX
    assert inner_max == INNER_MAX
