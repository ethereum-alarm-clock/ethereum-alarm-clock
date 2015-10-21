from populus.contracts.functions import (
    Function,
    FunctionGroup,
)


def enumerate_functions(config):
    for f in config._functions:
        if isinstance(f, FunctionGroup):
            for sub_f in f.functions:
                yield sub_f
        else:
            yield f


def test_alarm_function_signatures(contracts):
    """
    Test that all of the ABI signatures between the actual and stub contracts
    match.
    """
    Alarm = contracts.Alarm
    AlarmAPI = contracts.AlarmAPI

    exclude = {
        'registerData',
    }

    expected_abi = {
        hex(function.abi_signature): function.name
        for function in enumerate_functions(Alarm._config)
        if function.name not in exclude
    }

    actual_abi = {
        hex(function.abi_signature): function.name
        for function in enumerate_functions(AlarmAPI._config)
    }

    assert actual_abi == expected_abi


def test_alarm_events(contracts):
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
