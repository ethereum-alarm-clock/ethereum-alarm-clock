import functools
import itertools

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


def setup_request_filters(config,
                          executed=True,
                          aborted=True,
                          cancelled=True,
                          claimed=True):
    TransactionRequestFactory = config.get_transaction_request(None)
    filters = []

    if executed:
        executed_event_filter = TransactionRequestFactory.on('Executed')
        executed_event_filter.watch(
            functools.partial(executed_event_callback, config)
        )
        filters.append(executed_event_filter)

    if aborted:
        aborted_event_filter = TransactionRequestFactory.on('Aborted')
        aborted_event_filter.watch(
            functools.partial(aborted_event_callback, config)
        )
        filters.append(aborted_event_filter)

    if cancelled:
        cancelled_event_filter = TransactionRequestFactory.on('Cancelled')
        cancelled_event_filter.watch(
            functools.partial(cancelled_event_callback, config)
        )
        filters.append(cancelled_event_filter)

    if claimed:
        claimed_event_filter = TransactionRequestFactory.on('Claimed')
        claimed_event_filter.watch(
            functools.partial(claimed_event_callback, config)
        )
        filters.append(claimed_event_filter)

    return filters


def setup_factory_filters(config,
                          created=True,
                          validation_error=True):
    factory = config.factory

    filters = []

    if created:
        created_event_filter = factory.on('RequestCreated')
        created_event_filter.watch(
            functools.partial(created_event_callback, config)
        )
        filters.append(created_event_filter)

    if validation_error:
        validation_error_event_filter = factory.on('ValidationError')
        validation_error_event_filter.watch(
            functools.partial(validation_error_event_callback, config)
        )
        filters.append(validation_error_event_filter)

    return filters


@main.command('client:run')
@click.option(
    '--executed/--no-executed',
    default=True,
    help="Enables/Disables monitoring of the Executed event",
)
@click.option(
    '--aborted/--no-aborted',
    default=True,
    help="Enables/Disables monitoring of the Aborted event",
)
@click.option(
    '--cancelled/--no-cancelled',
    default=True,
    help="Enables/Disables monitoring of the Cancelled event",
)
@click.option(
    '--claimed/--no-claimed',
    default=True,
    help="Enables/Disables monitoring of the Claimed event",
)
@click.option(
    '--created/--no-created',
    default=True,
    help="Enables/Disables monitoring of the Created event",
)
@click.option(
    '--validation-error/--no-validation-error',
    default=True,
    help="Enables/Disables monitoring of the ValidationError event",
)
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

    filters = tuple(itertools.chain(
        [new_block_filter],
        setup_request_filters(
            config,
            executed=executed,
            aborted=aborted,
            cancelled=cancelled,
            claimed=claimed,
        ),
        setup_factory_filters(
            config,
            created=created,
            validation_error=validation_error,
        )
    ))
    for filter in filters[1:]:
        filter.poll_interval = 25

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
@click.option(
    '--executed/--no-executed',
    default=True,
    help="Enables/Disables monitoring of the Executed event",
)
@click.option(
    '--aborted/--no-aborted',
    default=True,
    help="Enables/Disables monitoring of the Aborted event",
)
@click.option(
    '--cancelled/--no-cancelled',
    default=True,
    help="Enables/Disables monitoring of the Cancelled event",
)
@click.option(
    '--claimed/--no-claimed',
    default=True,
    help="Enables/Disables monitoring of the Claimed event",
)
@click.option(
    '--created/--no-created',
    default=True,
    help="Enables/Disables monitoring of the Created event",
)
@click.option(
    '--validation-error/--no-validation-error',
    default=True,
    help="Enables/Disables monitoring of the ValidationError event",
)
@click.pass_context
def client_monitor(ctx,
                   executed,
                   aborted,
                   cancelled,
                   claimed,
                   created,
                   validation_error):
    main_ctx = ctx.parent
    config = main_ctx.config

    click.echo("Watching for events")

    filters = tuple(itertools.chain(
        setup_request_filters(
            config,
            executed=executed,
            aborted=aborted,
            cancelled=cancelled,
            claimed=claimed,
        ),
        setup_factory_filters(
            config,
            created=created,
            validation_error=validation_error,
        )
    ))
    for filter in filters[1:]:
        filter.poll_interval = 20

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
