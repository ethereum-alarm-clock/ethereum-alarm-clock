import click
import functools
import random
import gevent

from web3 import (
    Web3,
    IPCProvider,
)

from .config import Config
from .client.main import new_block_callback


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
    # TODO: remove this
    default='/Users/piper/sites/ethereum-alarm-clock/chains/local/geth.ipc',
)
@click.pass_context
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

    config = Config(web3)

    ctx.web3 = web3
    ctx.config = config


VALIDATION_ERRORS = (
    'InsufficientEndowment',
    'ReservedWindowBiggerThanExecutionWindow',
    'InvalidTemporalUnit',
    'ExecutionWindowTooSoon',
    'InvalidRequiredStackDepth',
    'CallGasTooHigh',
    'EmptyToAddress',
)


@main.command('request:create')
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
@click.option(
    '--window-start',
    '-w',
    type=click.IntRange(min=0),
)
@click.option(
    '--window-size',
    '-w',
    type=click.IntRange(min=0),
    default=255,
)
@click.option(
    '--endowment',
    '-e',
    type=click.IntRange(min=0),
)
@click.option(
    '--confirm/--no-confirm',
    default=True,
)
@click.pass_context
def request_create(ctx,
                   to_address,
                   call_data,
                   call_gas,
                   call_value,
                   temporal_unit,
                   window_start,
                   window_size,
                   endowment,
                   confirm):
    main_ctx = ctx.parent
    config = main_ctx.config

    factory = config.factory
    request_lib = config.request_lib
    payment_lib = config.payment_lib

    pending_request = factory.construct_pending_request(
        temporalUnit=temporal_unit,
        toAddress=to_address,
        callData=call_data,
        callGas=call_gas,
        callValue=call_value,
        windowStart=window_start,
        windowSize=window_size,
    )

    if endowment is None:
        gas_overhead = request_lib.call().EXECUTION_GAS_OVERHEAD()
        endowment = payment_lib.call().computeEndowment(
            payment=pending_request.payment,
            donation=pending_request.donation,
            callGas=pending_request.callGas,
            callValue=pending_request.callValue,
            requiredStackDepth=pending_request.requiredStackDepth,
            gasOverhead=gas_overhead,
        )

    factory_init_kwargs = pending_request.to_init_kwargs()

    validation_checks = factory.call().validateRequestParams(
        endowment=endowment,
        **factory_init_kwargs
    )
    if not all(validation_checks):
        errors = [
            VALIDATION_ERRORS[idx]
            for idx, is_valid in enumerate(validation_checks)
            if is_valid is False
        ]
        validation_error_message = (
            "Invalid Transaction Request Parameters:\n"
            "{0}".format('\n'.join([
                '- {error}'.format(error=error) for error in errors
            ]))
        )
        raise click.ClickException(validation_error_message)

    pre_create_message = '\n'.join((
        "Creating new Transaction Request:",
        pending_request.get_props_display(),
    ))
    click.echo(pre_create_message)
    if confirm:
        if not click.confirm("\n\nContinue with creation?", default=True):
            raise click.ClickException("Cancelled")

    create_txn_hash = factory.transact({
        'value': endowment,
    }).createValidatedRequest(**factory_init_kwargs)

    transaction_sent_message = (
        "\n\n"
        "Sent transaction to create new TransactionRequest:\n"
        " - RequestFactory @ {factory.address}\n"
        " - Txn Hash: {txn_hash}\n\n"
    ).format(factory=factory, txn_hash=create_txn_hash)
    click.echo(transaction_sent_message)

    while True:
        try:
            click.echo("Waiting for transaction to be mined...", nl=False)
            create_txn_receipt = config.wait.for_receipt(create_txn_hash)
            click.echo("MINED via block #{0}".format(
                create_txn_receipt['blockNumber']
            ))
            break
        except gevent.Timeout:
            if confirm:
                wait_longer_msg = (
                    "\n\nTimed out waiting for transaction receipt.  Would you like "
                    "to continue waiting?"
                )
                if click.confirm(wait_longer_msg, default=True):
                    continue
            raise click.ClickException(
                "Timed out waiting for transaction to be mined"
            )

    request_created_filter = factory.pastEvents('RequestCreated', {
        'fromBlock': create_txn_receipt['blockNumber'],
        'toBlock': create_txn_receipt['blockNumber'],
    })
    raw_request_created_logs = request_created_filter.get(False)
    request_created_logs = [
        log_entry for log_entry in raw_request_created_logs
        if log_entry['transactionHash'] == create_txn_hash
    ]

    if len(request_created_logs) == 1:
        txn_request_address = request_created_logs[0]['args']['request']
    else:
        not_found_message = (
            "Unable to find any newly created TransactionRequest contracts."
        )
        if create_txn_receipt['logs']:
            not_found_message += (
                "\nThe following log entries were found:\n{0}"
            ).format('\n'.join([
                '- topics: {0}\n  data: {1}'.format(
                    ', '.join(log_entry['topics']), log_entry['data'],
                ) for log_entry in create_txn_receipt['logs']
            ]))
        raise click.ClickException(not_found_message)

    success_message = (
        "\n\nSuccessfully created new TransactionRequest @ {0}".format(
            txn_request_address,
        )
    )
    click.echo(success_message)


@main.command()
@click.pass_context
def client(ctx):
    main_ctx = ctx.parent
    web3 = main_ctx.web3
    config = main_ctx.config

    new_block_filter = web3.eth.filter('latest')

    click.echo("Starting client")

    callback = functools.partial(new_block_callback, config=config)

    new_block_filter.watch(callback)

    # give it a moment to spin up.
    gevent.sleep(1)

    try:
        while new_block_filter.running is True:
            gevent.sleep(random.random())
    finally:
        if new_block_filter.running:
            click.echo("Stopping Client")
            new_block_filter.stop_watching()


@main.command()
@click.pass_context
def repl(ctx):
    main_ctx = ctx.parent
    web3 = main_ctx.web3  # noqa
    config = main_ctx.config

    tracker = config.tracker  # noqa
    factory = config.factory  # noqa

    import pdb
    pdb.set_trace()  # noqa
