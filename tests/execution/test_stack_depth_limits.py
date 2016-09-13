MAX_DEPTH = 2048

OUTER_MAX = 1021
CHECK_MAX = 1021
INNER_MAX = 1021


def test_stack_depth_checking(chain, web3, deploy_fbc, CallLib):
    """
    This function is useful for finding out what the limits are for stack depth
    protection.
    """
    client_contract = chain.get_contract('TestErrors')

    def deploy_call(depth_check, depth_inner):
        _fbc = deploy_fbc(
            client_contract,
            method_name='doStackExtension',
            arguments=[depth_inner],
            require_depth=depth_check,
        )
        chain.wait.for_receipt(client_contract.transact().reset())
        chain.wait.for_receipt(client_contract.transact().setCallAddress(_fbc.address))
        chain.wait.for_block(_fbc.call().targetBlock())
        return _fbc

    def check(_fbc, depth_outer):
        assert client_contract.call().value() is False

        call_txn_hash = client_contract.transact().proxyCall(depth_outer)
        chain.wait.for_receipt(call_txn_hash)

        is_successful = _fbc.call().wasCalled() and client_contract.call().value() is True
        return is_successful

    def find_maxima(attr, **defaults):
        left = 0
        right = MAX_DEPTH

        while left < right:
            depth = (left + right) // 2
            defaults[attr] = depth
            fbc = deploy_call(defaults['depth_check'], defaults['depth_inner'])

            if check(fbc, defaults['depth_outer']):
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
    print("outer max", outer_max)
    check_max = find_maxima('depth_check', depth_outer=0, depth_inner=0)
    print("check max", check_max)
    inner_max = find_maxima('depth_inner', depth_outer=0, depth_check=0)
    print("inner max", inner_max)

    assert outer_max == OUTER_MAX
    assert check_max == CHECK_MAX
    assert inner_max == INNER_MAX
