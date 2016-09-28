import click
import functools
import random
import gevent

from web3 import (
    Web3,
    IPCProvider,
)
from .db import MemoryDB as DB
from .config import Config
from .contracts.recorder import get_recorder


def root(latest_block_hash, web3, db, config):
    click.echo("New Block:", latest_block_hash)


def find_upcoming_block_scheduled_transaction_requests():
    pass


@click.group()
@click.option(
    '--tracker-address',
    '-t',
)
@click.option(
    '--factory-address',
    '-f',
)
@click.option(
    '--scheduler-address',
    '-s',
)
@click.option(
    '--log-level',
    '-l',
)
@click.option(
    '--provider',
    '-p',
    type=click.Choice(['ipc']),
    default='ipc',
)
@click.option(
    '--ipc-path',
    '-i',
)
@click.pass_context()
def main(ctx,
         tracker_address,
         factory_address,
         scheduler_address,
         log_level,
         provider,
         ipc_path):
    if provider == 'ipc':
        web3 = Web3(IPCProvider(ipc_path=ipc_path))
    else:
        raise click.ClickException("This shouldn't be possible")

    db = DB()
    config = Config()

    ctx.web3 = web3
    ctx.db = db
    ctx.config = config


@click.command()
@click.option(
    '--to-address',
    '-a',
    default='0x199a239ec2f7c788ce324d28be96fab34f3577f7',
)
@click.option(
    '--call-data',
    '-d',
    default='this-is-test-call-data',
)
@click.option(
    '--call-gas',
    '-g',
    default=150000,
)
@click.option(
    '--call-value',
    '-v',
    default=0,
)
@click.option(
    '--temporal-unit',
    '-t',
    type=click.Choice([1, 2]),
    default=1,
)
@click.pass_context()
def schedule(ctx, to_address, call_data, call_gas, call_value):
    main_ctx = ctx.parent
    recorder = get_recorder(main_ctx.web3, to_address)


@click.command()
def client():
    new_block_filter = web3.eth.filter('latest')

    click.echo("Starting client")

    client = functools.partial(root, web3=web3, db=db, config=config)

    new_block_filter.watch(client)

    # give it a moment to spin up.
    gevent.sleep(1)

    try:
        while new_block_filter.running is True:
            gevent.sleep(random.random())
    finally:
        if new_block_filter.running:
            click.echo("Stopping Client")
            new_block_filter.stop_watching()
