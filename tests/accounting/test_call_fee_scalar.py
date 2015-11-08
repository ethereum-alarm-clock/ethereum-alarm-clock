test_values = (
    (20, (
        (4, 145),
        (8, 138),
        (12, 129),
        (16, 117),
        (20, 100),
        (24, 83),
        (28, 71),
        (32, 62),
        (36, 55),
    )),
    (500, (
        (50, 148),
        (125, 143),
        (275, 132),
        (400, 117),
        (475, 105),
        (500, 100),
        (525, 95),
        (600, 83),
        (700, 71),
        (900, 55),
        (1200, 41),
    )),
)


deploy_contracts = [
    "CallLib",
]

def test_call_fee_scalar_values(CallLib):
    for base_gas_price, values in test_values:
        actual_values = [
            (CallLib.getCallFeeScalar(base_gas_price, gas_price), expected)
            for gas_price, expected in values
        ]
        assert all(actual == expected for actual, expected in actual_values)
