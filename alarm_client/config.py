import logging

import pylru

from gevent.lock import BoundedSemaphore

from populus.utils.wait import (
    Wait,
)

from .contracts.tracker import get_tracker
from .contracts.factory import get_factory
from .contracts.scheduler import get_scheduler
from .contracts.payment_lib import get_payment_lib
from .contracts.request_lib import get_request_lib
from .contracts.transaction_request import get_transaction_request


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('eth_alarm.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


MINUTE = 60


KNOWN_CHAINS = {
    # local test chain.
    '0x158e9d2f6f3082a1168619e1d59e789e210bb17c9bf9e39041e42b922753a2f9': {
        'contracts': {
            'tracker': '0xca60abb98e780a0f6d83e854c20b7431396bb3f5',
            'factory': '0xdd2d26ff972715fd89a394a01476cf6ef94eb070',
            #'block_scheduler': '0xb6b5e12e7db3ed8af10ca273a88c991a1ed3e177',
            #'timestamp_scheduler': '0x68e3669cad1bd372f44161992a5ab13be281cb80',
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
    logger = logger

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
                 tracker_address=None,
                 factory_address=None,
                 block_scheduler_address=None,
                 timestamp_scheduler_address=None,
                 payment_lib_address=None,
                 request_lib_address=None):
        self.web3 = web3
        self._tracker_address = tracker_address
        self._factory_address = factory_address
        self._block_scheduler_address = block_scheduler_address
        self._timestamp_scheduler_address = timestamp_scheduler_address
        self._payment_lib_address = payment_lib_address
        self._request_lib_address = request_lib_address
        self._locks = pylru.lrucache(2048)

    @property
    def wait(self):
        return Wait(self.web3)

    def lock(self, key):
        try:
            sem = self._locks[key]
        except KeyError:
            sem = BoundedSemaphore()
            self._locks[key] = sem
        return sem

    @property
    def chain_context(self):
        first_block_hash = self.web3.eth.getBlock('earliest')['hash']

        try:
            return KNOWN_CHAINS[first_block_hash]
        except KeyError:
            return {
                'contracts': {},
            }

    @property
    def contract_addresses(self):
        return self.chain_context['contracts']

    @property
    def tracker_address(self):
        if self._tracker_address is not None:
            return self._tracker_address

        try:
            return self.contract_addresses['tracker']
        except KeyError:
            raise KeyError("No known address for the RequestTracker.")

    @property
    def tracker(self):
        return get_tracker(self.web3, self.tracker_address)

    @property
    def factory_address(self):
        if self._factory_address is not None:
            return self._factory_address

        try:
            return self.contract_addresses['factory']
        except KeyError:
            raise KeyError("No known address for the RequestFactory.")

    @property
    def factory(self):
        return get_factory(self.web3, self.factory_address)

    @property
    def block_scheduler_address(self):
        if self._block_scheduler_address is not None:
            return self._block_scheduler_address

        try:
            return self.contract_addresses['block_scheduler']
        except KeyError:
            raise KeyError("No known address for the BlockScheduler.")

    @property
    def block_scheduler(self):
        return get_scheduler(self.web3, self.block_scheduler_address)

    @property
    def timestamp_scheduler_address(self):
        if self._timestamp_scheduler_address is not None:
            return self._timestamp_scheduler_address

        try:
            return self.contract_addresses['timestamp_scheduler']
        except KeyError:
            raise KeyError("No known address for the TimestampScheduler.")

    @property
    def timestamp_scheduler(self):
        return get_scheduler(self.web3, self.timestamp_scheduler_address)

    @property
    def payment_lib_address(self):
        if self._payment_lib_address is not None:
            return self._payment_lib_address

        try:
            return self.contract_addresses['payment_lib']
        except KeyError:
            raise KeyError("No known address for the PaymentLib.")

    @property
    def payment_lib(self):
        return get_payment_lib(self.web3, self.payment_lib_address)

    @property
    def request_lib_address(self):
        if self._request_lib_address is not None:
            return self._request_lib_address

        try:
            return self.contract_addresses['request_lib']
        except KeyError:
            raise KeyError("No known address for the RequestLib.")

    @property
    def request_lib(self):
        return get_request_lib(self.web3, self.request_lib_address)

    def get_transaction_request(self, address):
        return get_transaction_request(self.web3, address=address)
