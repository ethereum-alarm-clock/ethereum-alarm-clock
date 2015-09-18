def test_function_signatures(contracts):
    """
    Test that all of the ABI signatures between the actual and stub contracts
    match.
    """
    Alarm = contracts.Alarm
    AlarmAPI = contracts.AlarmAPI

    expected_abi = {
        hex(function.abi_function_signature): function.name
        for function in Alarm._config._functions
    }

    actual_abi = {
        hex(function.abi_function_signature): function.name
        for function in AlarmAPI._config._functions
    }

    assert actual_abi == expected_abi


def test_events(contracts):
    """
    Test that all of the ABI signatures between the actual and stub contracts
    match.
    """
    Alarm = contracts.Alarm
    AlarmAPI = contracts.AlarmAPI

    expected_events = {
        event.name for event in Alarm._config._events
    }

    actual_events = {
        event.name for event in AlarmAPI._config._events
    }

    assert actual_events == expected_events
