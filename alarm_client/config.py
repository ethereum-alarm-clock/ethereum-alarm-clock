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
        }
    },
}


class Config(object):
    web3 = None

    forward_scan_blocks = 512
    back_scan_blocks = 512

    forward_scan_seconds = 120 * MINUTE
    back_scan_seconds = 120 * MINUTE

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
                 request_lib_address=None):
        self.web3 = web3
        self.compiled_assets_path = compiled_assets_path
        self.log_level = log_level
        self.logfile_root = logfile_root
        self._tracker_address = tracker_address
        self._factory_address = factory_address
        self._payment_lib_address = payment_lib_address
        self._request_lib_address = request_lib_address
        self._locks = pylru.lrucache(2048)

    def get_logger(self, name):
        logger = logging.getLogger(name)
        has_stream_handler = any(
            isinstance(handler, logging.StreamHandler) for handler in logger.handlers
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
            file_handler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s %(message)s'))
            logger.addHandler(file_handler)
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
