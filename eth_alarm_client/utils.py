import logging
from logging import handlers


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


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(
        logging.Formatter(name.upper() + ': %(levelname)s: %(asctime)s %(message)s')
    )
    logger.addHandler(stream_handler)
    file_handler = handlers.RotatingFileHandler('logs/{0}.log'.format(name), maxBytes=10000000)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s %(message)s'))
    logger.addHandler(file_handler)
    return logger


def enumerate_upcoming_calls(alarm, anchor_block):
    block_cutoff = anchor_block + 40

    call_keys = []

    while anchor_block > 0 and anchor_block < block_cutoff:
        call_key = alarm.getNextCallKey.call(anchor_block)

        if call_key is None:
            break

        if alarm.getCallTargetBlock.call(call_key) > block_cutoff:
            break

        call_keys.append(call_key)

        sibling = call_key
        while sibling:
            sibling = alarm.getNextCallSibling.call(sibling)
            if sibling is not None:
                call_keys.append(sibling)

        anchor_block = alarm.getNextBlockWithCall.call(anchor_block + 1)

    return tuple(call_keys)
