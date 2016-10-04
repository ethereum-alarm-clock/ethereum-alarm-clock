import time
import functools
import uuid
from importlib import import_module


def import_string(dotted_path):
    """
    Source: django.utils.module_loading

    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        raise ImportError(msg)


def _bisect_blocks(web3, timestamp, use_left_bound=True):
    """
    Perform a binary search on the blockchain for the block that matches the
    given timestamp.  The `use_left_bound` parameter determines whether to
    return the block to the left or right of the timestamp in the event that no
    block matches the timestamp exactly.
    """
    left_bound = 1
    right_bound = web3.eth.blockNumber

    left_block = web3.eth.getBlock(left_bound)
    if left_block['timestamp'] >= timestamp:
        return 'earliest'
    right_block = web3.eth.getBlock(right_bound)
    if right_block['timestamp'] <= timestamp:
        return 'latest'

    while left_bound < right_bound - 1:
        middle = (left_bound + right_bound) // 2
        middle_block = web3.eth.getBlock(middle)

        if middle_block['timestamp'] < timestamp:
            left_bound = middle
        elif middle_block['timestamp'] > timestamp:
            right_bound = middle
        else:
            return middle
    else:
        if use_left_bound:
            return left_bound
        else:
            return right_bound


def find_block_left_of_timestamp(web3, timestamp):
    return _bisect_blocks(web3, timestamp, use_left_bound=True)


def find_block_right_of_timestamp(web3, timestamp):
    return _bisect_blocks(web3, timestamp, use_left_bound=False)


class cached_property(object):
    """
    Source: Django (django.utils.functional)

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


class _cache_if_not_eq(object):
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
        if instance is None:
            return self

        value = self.func(instance)

        if value != self.default_value:
            instance.__dict__[self.name] = value
        return value


def cache_if_not_eq(default_value):
    return type(
        'cache_if_not_eq',
        (_cache_if_not_eq,),
        {'default_value': default_value},
    )


def task(fn):
    @functools.wraps(fn)
    def inner(config, *args, **kwargs):
        exec_id = uuid.uuid4()
        logger = config.get_logger("client.timer")
        logger.debug("enter: %s | id: %s", fn.__name__, exec_id)
        start_at = time.time()
        return_value = fn(config, *args, **kwargs)
        elapsed = time.time() - start_at

        if elapsed > 10:
            logger.warning(
                "long runtime for task: %s | timed: %s | id: %s",
                fn.__name__,
                elapsed,
                exec_id,
            )
        else:
            logger.debug(
                "exit: %s | timed: %s | id: %s",
                fn.__name__,
                elapsed,
                exec_id,
            )
        return return_value
    return inner
