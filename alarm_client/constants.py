NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


ABORTED_REASON_MAP = {
    0: "WasCancelled",
    1: "AlreadyCalled",
    2: "BeforeCallWindow",
    3: "AfterCallWindow",
    4: "ReservedForClaimer",
    5: "StackTooDeep",
    6: "InsufficientGas",
}


VALIDATION_ERRORS = {
    0: 'InsufficientEndowment',
    1: 'ReservedWindowBiggerThanExecutionWindow',
    2: 'InvalidTemporalUnit',
    3: 'ExecutionWindowTooSoon',
    4: 'InvalidRequiredStackDepth',
    5: 'CallGasTooHigh',
    6: 'EmptyToAddress',
}
