import os
import click
import functools
import logging
import gevent

from web3 import (
    Web3,
    IPCProvider,
)

from .config import Config
from .client.main import (
    new_block_callback,
    executed_event_callback,
    aborted_event_callback,
    created_event_callback,
    cancelled_event_callback,
    claimed_event_callback,
)


BASE_DIR = os.path.dirname(__file__)


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


VALIDATION_ERRORS = (
    'InsufficientEndowment',
    'ReservedWindowBiggerThanExecutionWindow',
    'InvalidTemporalUnit',
    'ExecutionWindowTooSoon',
    'InvalidRequiredStackDepth',
    'CallGasTooHigh',
    'EmptyToAddress',
)


@main.command(
    'request:create',
    help="Schedule a transaction to be executed at a later time or block",
)
@click.option(
    '--to-address',
    '-a',
    default='0x199a239ec2f7c788ce324d28be96fab34f3577f7',
    help="The `toAddress` to be used",
)
@click.option(
    '--call-data',
    '-d',
    default='',
    help="The `callData` to be used",
)
@click.option(
    '--call-gas',
    '-g',
    default=150000,
    help="The `callGas` value to be used",
)
@click.option(
    '--call-value',
    '-v',
    default=0,
    help="The `callValue` value to be used",
)
@click.option(
    '--temporal-unit',
    '-t',
    type=click.Choice([1, 2]),
    default=1,
    help="The `temporalUnit` value to be used. 1:Blocks 2:Timestamp",
)
@click.option(
    '--window-start',
    '-w',
    type=click.IntRange(min=0),
    help="The `windowStart` value to be used",
)
@click.option(
    '--window-size',
    '-w',
    type=click.IntRange(min=0),
    default=255,
    help="The `windowSize` value to be used",
)
@click.option(
    '--endowment',
    '-e',
    type=click.IntRange(min=0),
    help="Manually control the endowment to be sent to the contract.",
)
@click.option(
    '--confirm/--no-confirm',
    default=True,
    help="Use --no-confirm to skip confirmation prompts.",
)
@click.option(
    '--deploy-from',
    '-f',
    help="Sets the `from` address for the scheduling transaction.  Defaults to the coinbase account if not provided.",
)
@click.option(
    '--no-wait',
    is_flag=True,
    default=False,
    help="Use --no-wait to skip waiting for the transaction to be mined",
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
                   confirm,
                   deploy_from,
                   no_wait):
    main_ctx = ctx.parent
    config = main_ctx.config
    wait = config.wait
    web3 = config.web3

    if deploy_from is not None:
        web3.eth.defaultAccount = deploy_from

    while True:
        try:
            click.echo(
                "Waiting for unlock on account: {0}".format(web3.eth.defaultAccount)
            )
            wait.for_unlock()
            break
        except gevent.Timeout:
            if confirm:
                wait_longer_for_unlock_msg = (
                    "Timed out waiting for {0} to be unlocked.  Would you like "
                    "to wait longer?"
                )
                if click.confirm(wait_longer_for_unlock_msg, default=True):
                    continue
            raise

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

    if no_wait:
        return
    while True:
        try:
            click.echo("Waiting for transaction to be mined...", nl=False)
            create_txn_receipt = config.wait.for_receipt(create_txn_hash, poll_interval=3)
            click.echo("MINED via block #{0}".format(
                create_txn_receipt['blockNumber']
            ))
            break
        except gevent.Timeout:
            if confirm:
                wait_longer_for_receipt_msg = (
                    "\n\nTimed out waiting for transaction receipt.  Would you like "
                    "to continue waiting?"
                )
                if click.confirm(wait_longer_for_receipt_msg, default=True):
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


@main.command('client:run')
@click.pass_context
def client_run(ctx):
    main_ctx = ctx.parent
    web3 = main_ctx.web3
    config = main_ctx.config
    factory = config.factory
    TransactionRequestFactory = config.get_transaction_request(None)

    new_block_filter = web3.eth.filter('latest')
    executed_event_filter = TransactionRequestFactory.on('Executed')
    aborted_event_filter = TransactionRequestFactory.on('Aborted')
    cancelled_event_filter = TransactionRequestFactory.on('Cancelled')
    claimed_event_filter = TransactionRequestFactory.on('Claimed')
    created_event_filter = factory.on('RequestCreated')

    new_block_filter.poll_interval = 2
    executed_event_filter.poll_interval = 17
    aborted_event_filter.poll_interval = 17
    cancelled_event_filter.poll_interval = 17
    claimed_event_filter.poll_interval = 17
    created_event_filter.poll_interval = 17

    click.echo("Starting client")

    new_block_filter.watch(functools.partial(new_block_callback, config))
    executed_event_filter.watch(functools.partial(executed_event_callback, config))
    aborted_event_filter.watch(functools.partial(aborted_event_callback, config))
    created_event_filter.watch(functools.partial(created_event_callback, config))
    claimed_event_filter.watch(functools.partial(claimed_event_callback, config))
    cancelled_event_filter.watch(functools.partial(cancelled_event_callback, config))

    try:
        while True:
            gevent.sleep(1)
            all_still_running = all((
                new_block_filter.running,
                executed_event_filter.running,
                aborted_event_filter.running,
                cancelled_event_filter.running,
                created_event_filter.running,
                claimed_event_filter.running,
            ))
            if not all_still_running:
                break
    finally:
        if new_block_filter.running:
            click.echo("Stopping Block Filter")
            new_block_filter.stop_watching()
        if executed_event_filter.running:
            click.echo("Stopping Executed Event Filter")
            executed_event_filter.stop_watching()
        if aborted_event_filter.running:
            click.echo("Stopping Aborted Event Filter")
            aborted_event_filter.stop_watching()
        if cancelled_event_filter.running:
            click.echo("Stopping Cancelled Event Filter")
            cancelled_event_filter.stop_watching()
        if claimed_event_filter.running:
            click.echo("Stopping Cancelled Event Filter")
            claimed_event_filter.stop_watching()
        if created_event_filter.running:
            click.echo("Stopping RequestCreated Filter")
            created_event_filter.stop_watching()


@main.command('client:monitor')
@click.pass_context
def client_monitor(ctx):
    main_ctx = ctx.parent
    config = main_ctx.config
    TransactionRequestFactory = config.get_transaction_request(None)
    factory = config.factory

    executed_event_filter = TransactionRequestFactory.on('Executed')
    aborted_event_filter = TransactionRequestFactory.on('Aborted')
    cancelled_event_filter = TransactionRequestFactory.on('Cancelled')
    claimed_event_filter = TransactionRequestFactory.on('Claimed')
    created_event_filter = factory.on('RequestCreated')

    executed_event_filter.poll_interval = 17
    aborted_event_filter.poll_interval = 17
    cancelled_event_filter.poll_interval = 17
    claimed_event_filter.poll_interval = 17
    created_event_filter.poll_interval = 17

    click.echo("Watching for events")

    executed_event_filter.watch(functools.partial(executed_event_callback, config))
    aborted_event_filter.watch(functools.partial(aborted_event_callback, config))
    created_event_filter.watch(functools.partial(created_event_callback, config))
    claimed_event_filter.watch(functools.partial(claimed_event_callback, config))
    cancelled_event_filter.watch(functools.partial(cancelled_event_callback, config))

    try:
        while True:
            gevent.sleep(1)
            all_still_running = all((
                executed_event_filter.running,
                aborted_event_filter.running,
                cancelled_event_filter.running,
                created_event_filter.running,
                claimed_event_filter.running,
            ))
            if not all_still_running:
                break
    finally:
        if executed_event_filter.running:
            click.echo("Stopping Executed Event Filter")
            executed_event_filter.stop_watching()
        if aborted_event_filter.running:
            click.echo("Stopping Aborted Event Filter")
            aborted_event_filter.stop_watching()
        if cancelled_event_filter.running:
            click.echo("Stopping Cancelled Event Filter")
            cancelled_event_filter.stop_watching()
        if claimed_event_filter.running:
            click.echo("Stopping Cancelled Event Filter")
            claimed_event_filter.stop_watching()
        if created_event_filter.running:
            click.echo("Stopping RequestCreated Filter")
            created_event_filter.stop_watching()


@main.command()
@click.pass_context
def repl(ctx):
    """
    Drop into a debugger shell with most of what you might want available in
    the local context.
    """
    main_ctx = ctx.parent
    web3 = main_ctx.web3  # noqa
    config = main_ctx.config

    tracker = config.tracker  # noqa
    factory = config.factory  # noqa

    import pdb
    pdb.set_trace()  # noqa
