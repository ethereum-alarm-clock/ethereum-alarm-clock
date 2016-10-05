import os
import logging
from logging import handlers
import json

import pylru

from gevent.lock import BoundedSemaphore

from web3.utils.abi import (
    filter_by_type,
)

from populus.utils.wait import (
    Wait,
)
from populus.utils.filesystem import (
    ensure_path_exists,
)

from .utils import cached_property

from .contracts.tracker import get_tracker
from .contracts.factory import get_factory
from .contracts.payment_lib import get_payment_lib
from .contracts.request_lib import get_request_lib
from .contracts.transaction_request import get_transaction_request


from gevent import monkey


monkey.patch_all()


MINUTE = 60


KNOWN_CHAINS = {
    # local test chain.
    '0x158e9d2f6f3082a1168619e1d59e789e210bb17c9bf9e39041e42b922753a2f9': {
        'contracts': {
            'tracker': '0xca60abb98e780a0f6d83e854c20b7431396bb3f5',
            'factory': '0xdd2d26ff972715fd89a394a01476cf6ef94eb070',
            'payment_lib': '0xde484f2fce8978b2d8a812519677e29200587de2',
            'request_lib': '0x26bbe3a895a5412483cf250fb6426ab3de0cd445',
        },
    },
    # mainnet
    '0xd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3': {
        'contracts': {
        }
    },
    # testnet
    '0x0cd786a2425d16f152c658316c423e6ce1181e15c3295826d7c9904cba9ce303': {
        'contracts': {
            'tracker': '0x8e67d439713b2022cac2ff4ebca21e173ccba4a0',
            'factory': '0x6005cb5aa9c4774c9f1f46ef3323c1337809cdb0',
            'payment_lib': '0xad4b2a1ec5b2ca6db05152cd099ff1f620e24469',
            'request_lib': '0xa941e3f9ed33fe66e0e71e1524f0508018ed7a9a',
            # not used yet but here for tracking purposes.
            'grove_lib': '0x1a0592f14999594357a6acc0842cf7aa2aaa17a1',
            'math_lib': '0x6ef5a43c15991e0c9d888819163de26a22d06a00',
            'execution_lib': '0x3336852437a0f2a81d8e3e45081b17fe6a7b5599',
            'itertools': '0x4b898f3ce9cf8ee05e9e800eb97267cc6fe56a78',
            'request_schedule_lib': '0x032635c4bac159d1b3b138f58e23f6a80d94717a',
            'safe_send_lib': '0xccb71bdec31b8d0f21f140940616b2d09334851b',
            'claim_lib': '0x1c868b2a0ecd8fd2bf2e893e18fb368d38cddd1f',
            'scheduler_lib': '0x102901670aa3997f63280d744b88aa174df57324',
            'block_scheduler': '0xbc5186e8aeacb8752454c3f62576f96209fc2395',
            'timestamp_scheduler': '0x3d919bb1e5c58a2dd99ea463d52045b112eb4330',
        }
    },
}


def is_rollbar_available():
    try:
        import rollbar  # noqa
    except ImportError:
        return False
    else:
        return (
            'ROLLBAR_SECRET' in os.environ and
            'ROLLBAR_ENVIRONMENT' in os.environ
        )


class Config(object):
    web3 = None

    forward_scan_blocks = None
    back_scan_blocks = None

    forward_scan_seconds = None
    back_scan_seconds = None

    _tracker_address = None
    _factory_address = None
    _block_scheduler_address = None
    _timestamp_scheduler_address = None
    _payment_lib_address = None

    def __init__(self,
                 web3,
                 compiled_assets_path,
                 log_level,
                 logfile_root='./logs',
                 tracker_address=None,
                 factory_address=None,
                 payment_lib_address=None,
                 request_lib_address=None,
                 scan_timestamp_range=(120 * MINUTE, 70 * MINUTE),
                 scan_blocks_range=(512, 300)):
        self.web3 = web3
        self.compiled_assets_path = compiled_assets_path
        self.log_level = log_level
        self.logfile_root = logfile_root
        self._tracker_address = tracker_address
        self._factory_address = factory_address
        self._payment_lib_address = payment_lib_address
        self._request_lib_address = request_lib_address
        self._locks = pylru.lrucache(2048)
        self.back_scan_seconds, self.forward_scan_seconds = scan_timestamp_range
        self.back_scan_blocks, self.forward_scan_blocks = scan_blocks_range

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)

        has_stream_handler = any(
            isinstance(handler, logging.StreamHandler)
            for handler in logger.handlers
        )
        if not has_stream_handler:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(self.log_level)
            stream_handler.setFormatter(logging.Formatter(
                name + ': %(levelname)s: %(asctime)s %(message)s'
            ))
            logger.addHandler(stream_handler)

        has_file_handler = any(
            isinstance(handler, handlers.RotatingFileHandler)
            for handler in logger.handlers
        )
        if self.logfile_root is not None and not has_file_handler:
            ensure_path_exists(self.logfile_root)
            logfile_path = os.path.join(self.logfile_root, "{0}.log".format(name))
            file_handler = handlers.RotatingFileHandler(logfile_path,
                                                        backupCount=20,
                                                        maxBytes=10000000)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(
                '%(levelname)s: %(asctime)s %(message)s'
            ))
            logger.addHandler(file_handler)

        if is_rollbar_available():
            import rollbar
            from rollbar.logger import RollbarHandler
            has_rollbar_handler = any(
                isinstance(handler, RollbarHandler)
                for handler in logger.handlers
            )
            if not has_rollbar_handler:
                rb_secret = os.environ['ROLLBAR_SECRET']
                rb_environment = os.environ['ROLLBAR_ENVIRONMENT']
                if not rollbar._initialized:
                    rollbar.init(rb_secret, rb_environment)

                rb_handler = RollbarHandler()
                rb_handler.setLevel(logging.WARNING)
                logger.addHandler(rb_handler)
        return logger

    @cached_property
    def wait(self):
        return Wait(self.web3)

    def lock(self, key):
        """
        Synchronization primitive for client functions to ensure that multiple
        functions are not trying to act on the same contract at the same time.
        """
        try:
            sem = self._locks[key]
        except KeyError:
            sem = BoundedSemaphore()
            self._locks[key] = sem
        return sem

    @cached_property
    def compiled_assets(self):
        with open(self.compiled_assets_path) as assets_file:
            return json.loads(assets_file.read())

    @cached_property
    def chain_context(self):
        first_block_hash = self.web3.eth.getBlock('earliest')['hash']

        try:
            return KNOWN_CHAINS[first_block_hash]
        except KeyError:
            return {
                'contracts': {},
            }

    @cached_property
    def contract_addresses(self):
        return self.chain_context['contracts']

    @cached_property
    def tracker_address(self):
        if self._tracker_address is not None:
            return self._tracker_address

        try:
            return self.contract_addresses['tracker']
        except KeyError:
            raise KeyError("No known address for the RequestTracker.")

    @cached_property
    def tracker_abi(self):
        return self.compiled_assets['RequestTracker']['abi']

    @cached_property
    def tracker(self):
        return get_tracker(self.web3,
                           address=self.tracker_address,
                           abi=self.tracker_abi)

    @cached_property
    def factory_address(self):
        if self._factory_address is not None:
            return self._factory_address

        try:
            return self.contract_addresses['factory']
        except KeyError:
            raise KeyError("No known address for the RequestFactory.")

    @cached_property
    def factory_abi(self):
        return self.compiled_assets['RequestFactory']['abi']

    @cached_property
    def factory(self):
        return get_factory(self.web3,
                           address=self.factory_address,
                           abi=self.factory_abi)

    @cached_property
    def payment_lib_address(self):
        if self._payment_lib_address is not None:
            return self._payment_lib_address

        try:
            return self.contract_addresses['payment_lib']
        except KeyError:
            raise KeyError("No known address for the PaymentLib.")

    @cached_property
    def payment_lib_abi(self):
        return self.compiled_assets['PaymentLib']['abi']

    @cached_property
    def payment_lib(self):
        return get_payment_lib(self.web3,
                               address=self.payment_lib_address,
                               abi=self.payment_lib_abi)

    @cached_property
    def request_lib_address(self):
        if self._request_lib_address is not None:
            return self._request_lib_address

        try:
            return self.contract_addresses['request_lib']
        except KeyError:
            raise KeyError("No known address for the RequestLib.")

    @cached_property
    def request_lib_abi(self):
        return self.compiled_assets['RequestLib']['abi']

    @cached_property
    def request_lib(self):
        return get_request_lib(self.web3,
                               address=self.request_lib_address,
                               abi=self.request_lib_abi)

    @cached_property
    def transaction_request_abi(self):
        return (
            self.compiled_assets['TransactionRequest']['abi'] +
            filter_by_type('event', self.request_lib_abi)
        )

    def get_transaction_request(self, address):
        return get_transaction_request(self.web3,
                                       address=address,
                                       abi=self.transaction_request_abi)
