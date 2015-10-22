import os
import json
import time
import decimal

import click

from eth_rpc_client import Client

from populus.contracts import Contract
from populus.utils import (
    wait_for_transaction,
)

from eth_alarm_client import (
    BlockSage,
    PoolManager,
    Scheduler,
)


alarm_addresses = (
    ('0.1.0', '0xb0059e72ae1802fa1e1add5e7d0cb0eec1cc0cc1'),
    ('0.2.0', '0xc1cfa6ac1d7cf99bd1e145dcd04ec462b3b0c4da'),
    ('0.3.0', '0xdb15058402c241b04a03846f6fb104b1fbeea10b'),
    ('0.4.0 (latest)', '0x30c9e568f133adce1f1ea91e189613223fc461b9'),
)

DEFAULT_ADDRESS = '0x30c9e568f133adce1f1ea91e189613223fc461b9'

rpc_client = Client('127.0.0.1', '8545')


def get_contract(contract_name):
    with open(os.path.join(os.path.dirname(__file__), 'alarm.json')) as contract_json:
        contracts = json.loads(contract_json.read())
    return Contract(contracts[contract_name], contract_name)


@click.group()
def main():
    pass


@main.command()
def addresses():
    """
    List the addresses for different versions of the alarm contract.
    """
    for version, address in alarm_addresses:
        click.echo("{0}: {1}".format(version.ljust(16), address))


@main.command()
@click.option(
    '--address',
    '-a',
    default=DEFAULT_ADDRESS,
    help="Return the current bond balance from the caller pool.",
)
def scheduler(address):
    """
    Run the call scheduler.
    """
    Alarm = get_contract('Alarm')

    alarm = Alarm(address, rpc_client)

    block_sage = BlockSage(rpc_client)
    pool_manager = PoolManager(alarm, block_sage=block_sage)
    pool_manager.monitor_async()
    scheduler = Scheduler(alarm, pool_manager, block_sage=block_sage)

    scheduler.monitor_async()

    try:
        while scheduler._thread.is_alive():
            time.sleep(1)

    except KeyboardInterrupt:
        scheduler.stop()
        scheduler.block_sage.stop()
        scheduler.pool_manager.stop()
        for scheduled_call in scheduler.active_calls.values():
            scheduled_call.stop()
        scheduler._thread.join(5)


#
#  Pool commands
#
@main.group()
def pool():
    """
    Commands for interacting with the caller pool.
    """
    pass


DENOMINATIONS = {
    'wei': 1,
    'babbage': 10 ** 3,
    'lovelace': 10 ** 6,
    'shannon': 10 ** 9,
    'szabo': 10 ** 12,
    'finney': 10 ** 15,
    'ether': 10 ** 18,
    'turing': 2 ** 256,
}


def convert_wei_to_denomination(value, denomination):
    return decimal.Decimal(value) / decimal.Decimal(DENOMINATIONS[denomination])


@pool.command('balance')
@click.option(
    '--denomination',
    '-d',
    type=click.Choice(DENOMINATIONS.keys()),
    default='wei',
    help="Return the current bond balance from the caller pool.",
)
@click.option(
    '--address',
    '-a',
    default=DEFAULT_ADDRESS,
    help="Return the current bond balance from the caller pool.",
)
def pool_balance(denomination, address):
    """
    Check your bond balance with the caller pool.
    """
    Alarm = get_contract('Alarm')
    alarm = Alarm(address, rpc_client)

    pool_manager = PoolManager(alarm)
    balance = pool_manager.bond_balance
    click.echo("Balance: {0}".format(
        convert_wei_to_denomination(balance, denomination),
    ))


@pool.command('minimum')
@click.option(
    '--denomination',
    '-d',
    type=click.Choice(DENOMINATIONS.keys()),
    default='wei',
    help="Return the current minimum bond amount for the caller pool.",
)
@click.option(
    '--address',
    '-a',
    default=DEFAULT_ADDRESS,
    help="Return the current bond balance from the caller pool.",
)
def pool_minimum(denomination, address):
    """
    Check the current minimum bond balance.
    """
    Alarm = get_contract('Alarm')
    alarm = Alarm(address, rpc_client)

    pool_manager = PoolManager(alarm)
    minimum_bond = pool_manager.minimum_bond
    click.echo("Minimum Bond: {0}".format(
        convert_wei_to_denomination(minimum_bond, denomination),
    ))


@pool.command('status')
@click.option(
    '--address',
    '-a',
    default=DEFAULT_ADDRESS,
    help="Return the current bond balance from the caller pool.",
)
def pool_status(address):
    """
    Display some status information about the caller pools.
    """
    Alarm = get_contract('Alarm')
    alarm = Alarm(address, rpc_client)
    pool_manager = PoolManager(alarm)

    status_msg = (
        "Current Block      : {b}\n"
        "Current Generation : {ap} - {ap_m} - ({ap_s})\n"
        "Next Generation    : {np} - {np_m} - ({np_s})"
    ).format(
        b=pool_manager.block_sage.current_block_number,
        ap=(pool_manager.current_generation_id or "N/A"),
        ap_m=pool_manager.get_generation_size(pool_manager.current_generation_id),
        ap_s="member" if pool_manager.in_current_generation else "not member",
        np=(pool_manager.next_generation_id or "N/A"),
        np_m=pool_manager.get_generation_size(pool_manager.next_generation_id),
        np_s="member" if pool_manager.in_next_generation else "not member",
    )
    click.echo(status_msg)


@pool.command('deposit')
@click.option(
    '--async/--no-async',
    is_flag=True,
    default=False,
    help="Deposit the bond amount in wei into the CallerPool",
)
@click.option(
    '--address',
    '-a',
    default=DEFAULT_ADDRESS,
    help="Return the current bond balance from the caller pool.",
)
@click.argument('value', type=click.INT)
def pool_deposit(async, address, value):
    """
    Deposit an amount in wei into your caller pool bond balance.
    """
    Alarm = get_contract('Alarm')
    alarm = Alarm(address, rpc_client)
    pool_manager = PoolManager(alarm)

    msg = (
        "Do you want to deposit {0} into the bond balance for the CallerPool "
        "contract at `{1}` for the address `{2}`"
    ).format(value, alarm._meta.address, pool_manager.coinbase)

    if click.confirm(msg):
        txn_hash = alarm.depositBond.sendTransaction(value=value)
    else:
        click.echo("Deposit cancelled")
        click.exit(1)

    if async:
        wait_for_transaction(rpc_client, txn_hash)
        click.echo("Deposit of {0} completed with txn: {1}.  Balance is now {2}".format(value, txn_hash, pool_manager.bond_balance))
    else:
        click.echo("Deposit of {0} initiated with txn: {1}".format(value, txn_hash))


if __name__ == '__main__':
    main()
