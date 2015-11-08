import os
import logging
import collections
from logging import handlers

from .contracts import FutureBlockCall


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class empty(object):
    pass


class _cache_once(object):
    """
    Similar to cached property except that it doesn't cache the value until it
    differs from the default value.
    """
    _cache_value = empty

    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = func.__name__

    def __get__(self, instance, type=None):
        value = self.func(instance)

        if value != self.default_value:
            instance.logger.debug("Caching return value: %s for function: %s", value, self.name)
            instance.__dict__[self.name] = value
        return value


def cache_once(default_value):
    return type('cache_once', (_cache_once,), {'default_value': default_value})


LEVELS = collections.defaultdict(lambda: logging.INFO)
LEVELS.update({
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
})


def get_logger(name, level=None):
    if level is None:
        level = LEVELS[os.environ.get('LOG_LEVEL', logging.INFO)]
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(
        logging.Formatter(name.upper() + ': %(levelname)s: %(asctime)s %(message)s')
    )
    logger.addHandler(stream_handler)
    file_handler = handlers.RotatingFileHandler('logs/{0}.log'.format(name), maxBytes=10000000)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s %(message)s'))
    logger.addHandler(file_handler)
    return logger


EMPTY_ADDRESS = '0x0000000000000000000000000000000000000000'


def enumerate_upcoming_calls(alarm, anchor_block):
    block_cutoff = anchor_block + 40
    blockchain_client = alarm._meta.blockchain_client

    calls = []

    while anchor_block > 0 and anchor_block < block_cutoff:
        call_address = alarm.getNextCall(anchor_block)

        if call_address == EMPTY_ADDRESS:
            break

        call = FutureBlockCall(call_address, blockchain_client)

        try:
            target_block = call.targetBlock()
        except ValueError:
            if len(blockchain_client.get_code(call_address)) <= 2:
                continue
            raise

        if target_block > block_cutoff:
            break

        calls.append(call_address)

        sibling_call_address = call_address
        while sibling_call_address != EMPTY_ADDRESS:
            sibling_call_address = alarm.getNextCallSibling(sibling_call_address)

            if sibling_call_address != EMPTY_ADDRESS:
                call = FutureBlockCall(sibling_call_address, alarm._meta.blockchain_client)
                try:
                    sibling_target_block = call.targetBlock()
                except ValueError:
                    if len(blockchain_client.get_code(sibling_call_address)) <= 2:
                        continue
                    raise

                if sibling_target_block == target_block:
                    calls.append(sibling_call_address)
                else:
                    break

        anchor_block = target_block + 1

    return tuple(calls)
