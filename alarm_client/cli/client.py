import functools

import gevent

import click

from .main import (
    main,
)
from alarm_client.tasks.main import (
    new_block_callback,
    executed_event_callback,
    aborted_event_callback,
    cancelled_event_callback,
    claimed_event_callback,
    created_event_callback,
    validation_error_event_callback,
)


FILTER_CALLBACK_MAP = {
    'Executed': executed_event_callback,
    'Aborted': aborted_event_callback,
    'Cancelled': cancelled_event_callback,
    'Claimed': claimed_event_callback,
    'RequestCreated': created_event_callback,
    'ValidationError': validation_error_event_callback,
}


FACTORY_EVENTS = {'RequestCreated', 'ValidationError'}
TRANSACTION_REQUEST_EVENTS = {'Executed', 'Aborted', 'Cancelled', 'Claimed'}


def setup_on_filter(config, event_name, poll_interval=20):
    if event_name in FACTORY_EVENTS:
        contract_factory = config.factory
    elif event_name in TRANSACTION_REQUEST_EVENTS:
        contract_factory = config.get_transaction_request(None)
    else:
        raise ValueError("Unknown Event: '{0}'".format(event_name))

    filter = contract_factory.on(event_name)
    filter.poll_interval = poll_interval
    callback = FILTER_CALLBACK_MAP[event_name]
    filter.watch(functools.partial(callback, config))
    return filter


def setup_pastEvents_filter(config,
                            event_name,
                            from_block,
                            to_block,
                            poll_interval=2):

    if event_name in FACTORY_EVENTS:
        contract_factory = config.factory
    elif event_name in TRANSACTION_REQUEST_EVENTS:
        contract_factory = config.get_transaction_request(None)
    else:
        raise ValueError("Unknown Event: '{0}'".format(event_name))

    filter_params = {}

    if from_block is not None:
        filter_params['fromBlock'] = from_block
    if to_block is not None:
        filter_params['toBlock'] = to_block

    filter = contract_factory.pastEvents(event_name, filter_params)
    filter.poll_interval = poll_interval
    callback = FILTER_CALLBACK_MAP[event_name]
    filter.watch(functools.partial(callback, config))
    return filter


execute_option = click.option(
    '--executed/--no-executed',
    default=True,
    help="Enables/Disables monitoring of the Executed event",
)
abort_option = click.option(
    '--aborted/--no-aborted',
    default=True,
    help="Enables/Disables monitoring of the Aborted event",
)
cancelled_option = click.option(
    '--cancelled/--no-cancelled',
    default=True,
    help="Enables/Disables monitoring of the Cancelled event",
)
claimed_option = click.option(
    '--claimed/--no-claimed',
    default=True,
    help="Enables/Disables monitoring of the Claimed event",
)
created_option = click.option(
    '--created/--no-created',
    default=True,
    help="Enables/Disables monitoring of the Created event",
)
validation_error_option = click.option(
    '--validation-error/--no-validation-error',
    default=True,
    help="Enables/Disables monitoring of the ValidationError event",
)


@main.command('client:run')
@execute_option
@abort_option
@cancelled_option
@claimed_option
@created_option
@validation_error_option
@click.pass_context
def client_run(ctx,
               executed,
               aborted,
               cancelled,
               claimed,
               created,
               validation_error):
    main_ctx = ctx.parent
    web3 = main_ctx.web3
    config = main_ctx.config

    click.echo("Starting client")

    new_block_filter = web3.eth.filter('latest')
    new_block_filter.poll_interval = 2
    new_block_filter.watch(functools.partial(new_block_callback, config))

    filters = [new_block_filter]

    if executed:
        filters.append(setup_on_filter(config, 'Executed'))
    if aborted:
        filters.append(setup_on_filter(config, 'Aborted'))
    if cancelled:
        filters.append(setup_on_filter(config, 'Cancelled'))
    if claimed:
        filters.append(setup_on_filter(config, 'Claimed'))
    if created:
        filters.append(setup_on_filter(config, 'RequestCreated'))
    if validation_error:
        filters.append(setup_on_filter(config, 'ValidationError'))

    try:
        while True:
            gevent.sleep(1)
            all_still_running = all((
                filter.running for filter in filters
            ))
            if not all_still_running:
                break
    finally:
        click.echo("Stopping client")
        for filter in filters:
            if filter.running:
                filter.stop_watching()
        click.echo("Fin")


@main.command('client:monitor')
@execute_option
@abort_option
@cancelled_option
@claimed_option
@created_option
@validation_error_option
@click.option(
    '--from-block',
    type=int,
)
@click.option(
    '--to-block',
    type=int,
)
@click.pass_context
def client_monitor(ctx,
                   executed,
                   aborted,
                   cancelled,
                   claimed,
                   created,
                   validation_error,
                   from_block,
                   to_block):
    """
    Scan the blockchain for events from the alarm service.  If --from-block or
    --to-block are specified this will find all past events between those block
    numbers.
    """
    main_ctx = ctx.parent
    config = main_ctx.config

    if to_block is not None or from_block is not None:
        setup_fn = functools.partial(
            setup_pastEvents_filter,
            from_block=from_block,
            to_block=to_block,
        )
    else:
        setup_fn = setup_on_filter

    filters = []

    if executed:
        filters.append(setup_fn(config, 'Executed'))
    if aborted:
        filters.append(setup_fn(config, 'Aborted'))
    if cancelled:
        filters.append(setup_fn(config, 'Cancelled'))
    if claimed:
        filters.append(setup_fn(config, 'Claimed'))
    if created:
        filters.append(setup_fn(config, 'RequestCreated'))
    if validation_error:
        filters.append(setup_fn(config, 'ValidationError'))

    click.echo('starting')

    try:
        while True:
            gevent.sleep(1)
            all_still_running = all((
                filter.running for filter in filters
            ))
            if not all_still_running:
                break
    finally:
        click.echo("Exiting client")
        for filter in filters:
            if filter.running:
                filter.stop_watching()
        click.echo("Fin")
