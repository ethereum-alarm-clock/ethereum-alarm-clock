import json
import functools
from web3.contract import Contract
from web3.utils.abi import (
    filter_by_type,
)

import pylru

from .request_lib import REQUEST_LIB_ABI


NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


BASE_TRANSACTION_REQUEST_ABI = json.loads('[{"constant":true,"inputs":[],"name":"callData","outputs":[{"name":"","type":"bytes"}],"type":"function"},{"constant":false,"inputs":[],"name":"claim","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":true,"inputs":[],"name":"requestData","outputs":[{"name":"","type":"address[6]"},{"name":"","type":"bool[3]"},{"name":"","type":"uint256[15]"},{"name":"","type":"uint8[1]"}],"type":"function"},{"constant":false,"inputs":[],"name":"execute","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[],"name":"sendPayment","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[],"name":"sendOwnerEther","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[],"name":"sendDonation","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[],"name":"refundClaimDeposit","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[],"name":"cancel","outputs":[{"name":"","type":"bool"}],"type":"function"}]')  # noqa


# Add all of the events from the RequestLib into the ABI
TRANSACTION_REQUEST_ABI = (
    BASE_TRANSACTION_REQUEST_ABI +
    filter_by_type('event', REQUEST_LIB_ABI)
)


class BlockCache(object):
    def __init__(self, size=128):
        self.cache = pylru.lrucache(size)

    def __call__(self, method):
        @functools.wraps(method)
        def inner(inner_self, *args, **kwargs):
            cache_key = (
                method.__name__,
                inner_self.web3.eth.blockNumber,
                inner_self.address,
                args,
                tuple(sorted(kwargs.items())),
            )
            try:
                return self.cache[cache_key]
            except KeyError:
                return_value = method(inner_self, *args, **kwargs)
                self.cache[cache_key] = return_value
                return return_value
        return inner


block_cached = BlockCache()


def txn_request_attr(attr_name):
    def inner(self):
        return self.request_data[attr_name]

    inner.__name__ = attr_name
    return property(inner)


class TransactionRequestFactory(Contract):
    @property
    @block_cached
    def request_data(self):
        data = self.call().requestData()
        call_data = self.call().callData()
        address_args, bool_args, uint_args, uint8_args = data

        request_properties = {
            'claimedBy': address_args[0],
            'createdBy': address_args[1],
            'owner': address_args[2],
            'donationBenefactor': address_args[3],
            'paymentBenefactor': address_args[4],
            'toAddress': address_args[5],
            'wasCalled': bool_args[1],
            'wasSuccessful': bool_args[2],
            'isCancelled': bool_args[0],
            'paymentModifier': uint8_args[0],
            'claimDeposit': uint_args[0],
            'anchorGasPrice': uint_args[1],
            'donation': uint_args[2],
            'donationOwed': uint_args[3],
            'payment': uint_args[4],
            'paymentOwed': uint_args[5],
            'claimWindowSize': uint_args[6],
            'freezePeriod': uint_args[7],
            'reservedWindowSize': uint_args[8],
            'temporalUnit': uint_args[9],
            'windowSize': uint_args[10],
            'windowStart': uint_args[11],
            'callGas': uint_args[12],
            'callValue': uint_args[13],
            'requiredStackDepth': uint_args[14],
            'callData': call_data,
        }

        BaseRequest = type(
            'BaseRequest',
            (object,),
            request_properties,
        )
        return type(
            'Request',
            (BaseRequest,),
            {
                '__getitem__': lambda s, k: request_properties.__getitem__(k),
                '__setitem__': lambda s, k, v: request_properties.__setitem__(k, v),
            },
        )()

    claimedBy = txn_request_attr('claimedBy')
    createdBy = txn_request_attr('createdBy')
    owner = txn_request_attr('owner')
    donationBenefactor = txn_request_attr('donationBenefactor')
    paymentBenefactor = txn_request_attr('paymentBenefactor')
    toAddress = txn_request_attr('toAddress')
    wasCalled = txn_request_attr('wasCalled')
    wasSuccessful = txn_request_attr('wasSuccessful')
    isCancelled = txn_request_attr('isCancelled')
    paymentModifier = txn_request_attr('paymentModifier')
    claimDeposit = txn_request_attr('claimDeposit')
    anchorGasPrice = txn_request_attr('anchorGasPrice')
    donation = txn_request_attr('donation')
    donationOwed = txn_request_attr('donationOwed')
    payment = txn_request_attr('payment')
    paymentOwed = txn_request_attr('paymentOwed')
    claimWindowSize = txn_request_attr('claimWindowSize')
    freezePeriod = txn_request_attr('freezePeriod')
    reservedWindowSize = txn_request_attr('reservedWindowSize')
    temporalUnit = txn_request_attr('temporalUnit')
    windowSize = txn_request_attr('windowSize')
    windowStart = txn_request_attr('windowStart')
    callGas = txn_request_attr('callGas')
    callValue = txn_request_attr('callValue')
    requiredStackDepth = txn_request_attr('requiredStackDepth')
    callData = txn_request_attr('callData')

    @property
    def now(self):
        if self.temporalUnit == 1:
            return self.web3.eth.blockNumber
        elif self.temporalUnit == 2:
            latest_block = self.web3.eth.getBlock('latest')
            return latest_block['timestamp']
        else:
            invalid_temporal_unit_msg = (
                "Invalid temporalUnit: {0} for Request @ {1}".format(
                    self.temporalUnit,
                    self.address,
                )
            )
            raise ValueError(invalid_temporal_unit_msg)

    @property
    def claimWindowStart(self):
        return self.windowStart - self.freezePeriod - self.claimWindowSize

    @property
    def claimWindowEnd(self):
        return self.windowStart - self.freezePeriod

    @property
    def claimPaymentModifier(self):
        return 100 * (
            self.now - self.claimWindowStart
        ) // self.claimWindowSize

    @property
    def isClaimed(self):
        return self.claimedBy != NULL_ADDRESS

    def isClaimedBy(self, address):
        return self.claimedBy == address

    @property
    def inClaimWindow(self):
        return self.claimWindowStart <= self.now < self.claimWindowEnd

    @property
    def beforeClaimWindow(self):
        return self.now < self.claimWindowStart

    @property
    def isClaimable(self):
        return not self.isClaimed and self.inClaimWindow

    @property
    def freezeWindowStart(self):
        return self.windowStart - self.freezePeriod

    @property
    def inFreezePeriod(self):
        return self.freezeWindowStart <= self.now < self.windowStart

    @property
    def executionWindowEnd(self):
        return self.windowStart + self.windowSize

    @property
    def reservedExecutionWindowEnd(self):
        return self.windowStart + self.reservedWindowSize

    @property
    def inExecutionWindow(self):
        return self.windowStart <= self.now <= self.executionWindowEnd

    @property
    def inReservedWindow(self):
        return self.windowStart <= self.now < self.reservedExecutionWindowEnd

    @property
    def afterExecutionWindow(self):
        return self.now > self.executionWindowEnd

    @property
    def paymentModifier(self):
        if self.web3.eth.gasPrice > self.anchorGasPrice:
            return self.anchorGasPrice * 100 // self.web3.eth.gasPrice
        else:
            return 200 - (
                self.anchorGasPrice * 100 // (
                    2 * self.anchorGasPrice - self.web3.eth.gasPrice
                )
            )


_txn_request_cache = pylru.lrucache(256)


def get_transaction_request(web3, address, abi=TRANSACTION_REQUEST_ABI):
    try:
        return _txn_request_cache[address]
    except KeyError:
        txn_request = web3.eth.contract(
            abi=abi,
            address=address,
            base_contract_factory_class=TransactionRequestFactory,
        )
        _txn_request_cache[address] = txn_request
        return txn_request
