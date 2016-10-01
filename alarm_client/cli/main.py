import os
import click
import logging

from web3 import (
    Web3,
    IPCProvider,
)

from alarm_client.config import Config


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@click.group()
@click.option(
    '--tracker-address',
    '-t',
    envvar='TRACKER_ADDRESS',
    help='The address of the RequestTracker contract that should be used.',
)
@click.option(
    '--factory-address',
    '-f',
    help='The address of the RequestFactory contract that should be used.',
)
@click.option(
    '--payment-lib-address',
    envvar='PAYMENT_LIB_ADDRESS',
    help='The address of the PaymentLib contract that should be used.',
)
@click.option(
    '--request-lib-address',
    '-r',
    envvar='REQUEST_LIB_ADDRESS',
    help='The address of the RequestLib contract that should be used.',
)
@click.option(
    '--log-level',
    '-l',
    type=int,
    default=logging.INFO,
    envvar='LOG_LEVEL',
    help='Integer logging level - 10:DEBUG 20:INFO 30:WARNING 40:ERROR',
)
@click.option(
    '--provider',
    '-p',
    type=click.Choice(['ipc']),
    default='ipc',
    envvar='PROVIDER',
    help='Web3.py provider type to use to connect to the chain.',
)
@click.option(
    '--ipc-path',
    '-i',
    envvar='IPC_PATH',
    help='Path to the IPC socket that the IPCProvider will connect to.',
)
@click.option(
    '--compiled-assets-path',
    '-a',
    type=click.Path(dir_okay=False),
    default=os.path.join(BASE_DIR, 'assets', 'v0.8.0.json'),
    envvar='COMPILED_ASSETS_PATH',
    help='Path to JSON file which contains the compiled contract assets',
)
@click.pass_context
def main(ctx,
         tracker_address,
         factory_address,
         payment_lib_address,
         request_lib_address,
         log_level,
         provider,
         ipc_path,
         compiled_assets_path):
    if provider == 'ipc':
        web3 = Web3(IPCProvider(ipc_path=ipc_path))
    else:
        raise click.ClickException("This shouldn't be possible")

    config = Config(
        web3,
        compiled_assets_path=compiled_assets_path,
        log_level=log_level,
        tracker_address=tracker_address,
        factory_address=factory_address,
        payment_lib_address=payment_lib_address,
        request_lib_address=request_lib_address,
    )

    ctx.web3 = web3
    ctx.config = config
