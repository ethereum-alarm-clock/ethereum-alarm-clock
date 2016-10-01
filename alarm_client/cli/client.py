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
    created_event_callback,
    cancelled_event_callback,
    claimed_event_callback,
)


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
