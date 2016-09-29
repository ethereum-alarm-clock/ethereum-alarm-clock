import functools
from web3.contract import Contract

import pylru

from ..utils import (
    find_block_left_of_timestamp,
    find_block_right_of_timestamp,
    cached_property,
    cache_if_not_eq,
)
from ..constants import NULL_ADDRESS


class BlockCache(object):
    """
    A global cache used to prevent duplicate lookups during a single block.  If
    the block number has not changed then any function decorated with this will
    return the previous value that was computed on that block.
    """
    def __init__(self, size=256):
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
    """
    Sets a `property` on the class that looks up the attr_name off of the
    request_data.
    """
    def inner(self):
        return self.request_data[attr_name]

    inner.__name__ = attr_name
    return property(inner)


def immutable_txn_request_attr(attr_name):
    """
    Sets a `property` on the class that looks up the attr_name off of the
    request_data and caches the return value since it cannot be changed.
    """
    def inner(self):
        return self.request_data[attr_name]

    inner.__name__ = attr_name
    return cached_property(inner)


def cached_once_not_eq_txn_request_attr(attr_name, default_value):
    """
    Sets a `property` on the class that looks up the attr_name off of the
    request_data and caches the return value once it deviates from the
    `default_value` since it cannot change after this.
    """
    def inner(self):
        return self.request_data[attr_name]

    inner.__name__ = attr_name
    return cache_if_not_eq(default_value)(inner)


class TransactionRequestFactory(Contract):
    def __str__(self):
        return "Transaction Request:\n{0}".format(self.get_props_display())

    def __repr__(self):
        return str(self)

    def get_props_display(self):
        return '\n'.join((
            "- claimedBy: {s.claimedBy}",
            "- createdBy: {s.createdBy}",
            "- owner: {s.owner}",
            "- donationBenefactor: {s.donationBenefactor}",
            "- paymentBenefactor: {s.paymentBenefactor}",
            "- toAddress: {s.toAddress}",
            "- wasCalled: {s.wasCalled}",
            "- wasSuccessful: {s.wasSuccessful}",
            "- isCancelled: {s.isCancelled}",
            "- paymentModifier: {s.paymentModifier}",
            "- claimDeposit: {s.claimDeposit}",
            "- anchorGasPrice: {s.anchorGasPrice}",
            "- donation: {s.donation}",
            "- donationOwed: {s.donationOwed}",
            "- payment: {s.payment}",
            "- paymentOwed: {s.paymentOwed}",
            "- claimWindowSize: {s.claimWindowSize}",
            "- freezePeriod: {s.freezePeriod}",
            "- reservedWindowSize: {s.reservedWindowSize}",
            "- temporalUnit: {s.temporalUnit}",
            "- windowSize: {s.windowSize}",
            "- windowStart: {s.windowStart}",
            "- callGas: {s.callGas}",
            "- callValue: {s.callValue}",
            "- requiredStackDepth: {s.requiredStackDepth}",
            "- callData: {s.callData}",
        )).format(s=self)

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

    claimedBy = cached_once_not_eq_txn_request_attr('claimedBy', NULL_ADDRESS)
    createdBy = immutable_txn_request_attr('createdBy')
    owner = immutable_txn_request_attr('owner')
    donationBenefactor = immutable_txn_request_attr('donationBenefactor')
    paymentBenefactor = cached_once_not_eq_txn_request_attr(
        'paymentBenefactor',
        NULL_ADDRESS,
    )
    toAddress = immutable_txn_request_attr('toAddress')
    wasCalled = cached_once_not_eq_txn_request_attr('wasCalled', False)
    wasSuccessful = cached_once_not_eq_txn_request_attr('wasSuccessful', False)
    isCancelled = cached_once_not_eq_txn_request_attr('isCancelled', False)
    paymentModifier = cached_once_not_eq_txn_request_attr('paymentModifier', 0)
    claimDeposit = txn_request_attr('claimDeposit')
    anchorGasPrice = immutable_txn_request_attr('anchorGasPrice')
    donation = immutable_txn_request_attr('donation')
    donationOwed = txn_request_attr('donationOwed')
    payment = immutable_txn_request_attr('payment')
    paymentOwed = txn_request_attr('paymentOwed')
    claimWindowSize = immutable_txn_request_attr('claimWindowSize')
    freezePeriod = immutable_txn_request_attr('freezePeriod')
    reservedWindowSize = immutable_txn_request_attr('reservedWindowSize')
    temporalUnit = immutable_txn_request_attr('temporalUnit')
    windowSize = immutable_txn_request_attr('windowSize')
    windowStart = immutable_txn_request_attr('windowStart')
    callGas = immutable_txn_request_attr('callGas')
    callValue = immutable_txn_request_attr('callValue')
    requiredStackDepth = immutable_txn_request_attr('requiredStackDepth')
    callData = immutable_txn_request_attr('callData')

    @property
    @block_cached
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

    @cached_property
    def claimWindowStart(self):
        return self.windowStart - self.freezePeriod - self.claimWindowSize

    @cached_property
    def claimWindowEnd(self):
        return self.windowStart - self.freezePeriod

    @property
    @block_cached
    def claimPaymentModifier(self):
        return 100 * (
            self.now - self.claimWindowStart
        ) // self.claimWindowSize

    @cache_if_not_eq(False)
    def isClaimed(self):
        return self.claimedBy != NULL_ADDRESS

    def isClaimedBy(self, address):
        return self.claimedBy == address

    @property
    @block_cached
    def inClaimWindow(self):
        return self.claimWindowStart <= self.now < self.claimWindowEnd

    @property
    @block_cached
    def beforeClaimWindow(self):
        return self.now < self.claimWindowStart

    @property
    @block_cached
    def isClaimable(self):
        return not self.isClaimed and self.inClaimWindow

    @cached_property
    def freezeWindowStart(self):
        return self.windowStart - self.freezePeriod

    @property
    @block_cached
    def inFreezePeriod(self):
        return self.freezeWindowStart <= self.now < self.windowStart

    @cached_property
    def executionWindowEnd(self):
        return self.windowStart + self.windowSize

    @cache_if_not_eq('latest')
    def executionWindowStartBlock(self):
        if self.temporalUnit == 1:
            return self.windowStart
        else:
            return find_block_right_of_timestamp(self.web3, self.windowStart)

    @cache_if_not_eq('latest')
    def executionWindowEndBlock(self):
        if self.temporalUnit == 1:
            return self.executionWindowEnd
        else:
            return find_block_left_of_timestamp(self.web3, self.executionWindowEnd)

    @cached_property
    def reservedExecutionWindowEnd(self):
        return self.windowStart + self.reservedWindowSize

    @property
    @block_cached
    def inExecutionWindow(self):
        return self.windowStart <= self.now <= self.executionWindowEnd

    @property
    @block_cached
    def inReservedWindow(self):
        return self.windowStart <= self.now < self.reservedExecutionWindowEnd

    @property
    @block_cached
    def afterExecutionWindow(self):
        return self.now > self.executionWindowEnd

    @property
    @block_cached
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


def get_transaction_request(web3, address, abi):
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
