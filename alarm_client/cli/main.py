import os
import click
import logging

from web3 import (
    Web3,
    IPCProvider,
    RPCProvider,
)

from alarm_client.config import Config
from alarm_client.utils import (
    import_string,
)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MINUTE = 60


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
    envvar='FACTORY_ADDRESS',
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
    default='ipc',
    envvar='PROVIDER',
    help=(
        "Web3.py provider type to use to connect to the chain.  Supported "
        "values are 'rpc', 'ipc', or any dot-separated python path to a web3 "
        "provider class"
    ),
)
@click.option(
    '--ipc-path',
    envvar='IPC_PATH',
    help='Path to the IPC socket that the IPCProvider will connect to.',
)
@click.option(
    '--rpc-host',
    envvar='RPC_HOST',
    help='Hostname or IP address of the RPC server',
    default='localhost',
)
@click.option(
    '--rpc-port',
    envvar='RPC_PORT',
    type=int,
    default=8545,
    help='The port to use when connecting to the RPC server',
)
@click.option(
    '--compiled-assets-path',
    '-a',
    type=click.Path(dir_okay=False),
    default=os.path.join(BASE_DIR, 'assets', 'v0.8.0.json'),
    envvar='COMPILED_ASSETS_PATH',
    help='Path to JSON file which contains the compiled contract assets',
)
@click.option(
    '--back-scan-seconds',
    type=int,
    default=120 * MINUTE,
    envvar='BACK_SCAN_SECONDS',
    help='Number of seconds to scan into the past for timestamp based calls',
)
@click.option(
    '--forward-scan-seconds',
    type=int,
    default=70 * MINUTE,
    envvar='FORWARD_SCAN_SECONDS',
    help='Number of seconds to scan into the future for timestamp based calls',
)
@click.option(
    '--back-scan-blocks',
    type=int,
    default=512,
    envvar='BACK_SCAN_SECONDS',
    help='Number of blocks to scan into the past for block based calls',
)
@click.option(
    '--forward-scan-blocks',
    type=int,
    default=300,
    envvar='FORWARD_SCAN_BLOCKS',
    help='Number of blocks to scan into the future for block based calls',
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
         rpc_host,
         rpc_port,
         compiled_assets_path,
         back_scan_seconds,
         forward_scan_seconds,
         back_scan_blocks,
         forward_scan_blocks):
    if provider == 'ipc':
        web3 = Web3(IPCProvider(ipc_path=ipc_path))
    elif provider == 'rpc':
        web3 = Web3(RPCProvider(host=rpc_host, port=rpc_port))
    elif provider:
        provider_class = import_string(provider)
        web3 = Web3(provider_class())
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
        scan_timestamp_range=(back_scan_seconds, forward_scan_seconds),
        scan_blocks_range=(back_scan_blocks, forward_scan_blocks),
    )

    ctx.web3 = web3
    ctx.config = config
