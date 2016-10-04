import click

import gevent

from alarm_client import constants

from .main import main


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
            constants.VALIDATION_ERRORS[idx]
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
