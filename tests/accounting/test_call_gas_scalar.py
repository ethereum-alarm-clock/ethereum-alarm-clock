import pytest
import itertools


@pytest.mark.parametrize(
    'base_gas_price,gas_price_and_expected',
    itertools.chain(
        itertools.product(
            [20],
            [
                (4, 145),
                (8, 138),
                (12, 129),
                (16, 117),
                (20, 100),
                (24, 83),
                (28, 71),
                (32, 62),
                (36, 55),
            ],
        ),
        itertools.product(
            [500],
            [
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
            ],
        ),
    ),
)
def test_gas_scalar_values(unmigrated_chain, base_gas_price, gas_price_and_expected):
    gas_price, expected_gas_scalar = gas_price_and_expected

    chain = unmigrated_chain

    call_lib = chain.get_contract('CallLib')

    actual_gas_scalar = call_lib.call().getGasScalar(base_gas_price, gas_price)
    assert actual_gas_scalar == expected_gas_scalar
