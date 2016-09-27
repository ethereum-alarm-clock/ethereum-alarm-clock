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


def root(latest_block_hash, web3, db, config):
    click.echo("New Block:", latest_block_hash)


def find_upcoming_block_scheduled_transaction_requests():
    pass


@click.command()
@click.option(
    '--tracker-address',
    '-t',
)
@click.option(
    '--factory-address',
    '-f',
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
def main(tracker_address, factory_address, log_level, provider, ipc_path):
    if provider == 'ipc':
        web3 = Web3(IPCProvider(ipc_path=ipc_path))
    else:
        raise click.ClickException("This shouldn't be possible")

    db = DB()
    config = Config()

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
