import threading
import time

from ethereum import utils as ethereum_utils

from populus.utils import wait_for_transaction

from .block_sage import BlockSage
from .utils import (
    cached_property,
    cache_once,
    get_logger
)


EMPTY_ADDRESS = '0x0000000000000000000000000000000000000000'
CANCELLATION_WINDOW = 8


class ScheduledCall(object):
    """
    Abstraction to represent an upcoming function call.  Can monitor for
    """
    txn_hash = None
    txn_receipt = None
    txn = None

    def __init__(self, alarm, pool_manager, call_key, block_sage=None):
        self.call_key = call_key
        self.alarm = alarm
        self.pool_manager = pool_manager
        self.logger = get_logger('call-{0}'.format(self.hex_call_key[:5]))

        if block_sage is None:
            block_sage = BlockSage(self.rpc_client)
        self.block_sage = block_sage
        if self.rpc_client.get_block_number() < self.target_block - 80:
            self.logger.warning(
                "It is not advisable to work with a ScheduledCall until the "
                "40-80 blocks before its target block"
            )

    @cached_property
    def hex_call_key(self):
        return ethereum_utils.encode_hex(self.call_key)

    #
    # Execution Pre Requesites
    #
    @cached_property
    def is_designated_caller(self):
        return self.designated_caller_addresses.intersection((
            self.coinbase, EMPTY_ADDRESS,
        ))

    @property
    def call_window_passed(self):
        return self.block_sage.current_block_number >= self.last_block

    @property
    def scheduler_can_pay(self):
        gas_limit = int(self.block_sage.current_block['gasLimit'], 16)
        gas_price = self.rpc_client.get_gas_price()

        # Require 110% of max gas to be sure.
        return self.scheduler_account_balance >= gas_limit * gas_price * 1.1

    def stop(self):
        self._run = False

    def validate_call(self):
        if not self.is_designated_caller:
            raise ValueError("Not in the designated callers")

        if self.was_called:
            raise ValueError("Already Called")

        if self.is_cancelled:
            raise ValueError("Call was cancelled")

        if not self.scheduler_can_pay:
            raise ValueError("Scheduler cannot pay")

    def execute(self):
        # Blocks until we are within 3 blocks of the call window.
        self.wait_for_call_window()
        self.logger.info("Call window pending..")

        #
        # Do pre-requesite call checks.
        #
        self.validate_call()

        while getattr(self, '_run', True):
            if self.block_sage.current_block_number >= self.last_block:
                self.logger.error("Call window expired")
                break

            if self.block_sage.current_block_number not in self.callable_blocks:
                time.sleep(0.1)
                continue

            # Execute the transaction
            self.logger.info("Attempting to execute call")
            txn_hash = self.alarm.doCall.sendTransaction(self.call_key)

            # Wait for the transaction receipt.
            try:
                self.logger.debug("Waiting for transaction: %s", txn_hash)
                txn_receipt = wait_for_transaction(
                    self.rpc_client,
                    txn_hash,
                    self.block_sage.block_time * 1.5,
                )
            except ValueError:
                self.logger.info("Unable to get transaction receipt: %s", txn_hash)
                self.validate_call()
                self.logger.info("Retrying call")
                continue

            self.logger.info("Transaction accepted.")
            self.txn_hash = txn_hash
            self.txn_receipt = txn_receipt
            self.txn = self.rpc_client.get_transaction_by_hash(txn_hash)
            break

    def execute_async(self):
        self._run = True
        self._thread = threading.Thread(target=self.execute)
        self._thread.daemon = True
        self._thread.start()

    def wait_for_call_window(self, buffer=3):
        """
        wait for self.target_block - buffer (~30 seconds at 2 blocks)
        """
        if self.block_sage.current_block_number > self.last_block:
            raise ValueError("Already passed call execution window")

        self.logger.info("Waiting for block #%s", self.target_block - buffer)
        while getattr(self, '_run', True) and self.block_sage.current_block_number < self.target_block - buffer:
            time.sleep(0.25)

    #
    #  Meta Properties
    #
    @property
    def rpc_client(self):
        return self.alarm._meta.rpc_client

    @cached_property
    def coinbase(self):
        return self.rpc_client.get_coinbase()

    @property
    def scheduler_account_balance(self):
        """
        The account balance of the scheduler for this call.
        """
        return self.alarm.accountBalances.call(self.scheduled_by)

    @property
    def last_block(self):
        """
        The last block number that this call can be executed on.
        """
        return self.target_block + self.grace_period

    @cached_property
    def designated_caller_addresses(self):
        return set(self.designated_callers.values())

    @cached_property
    def designated_callers(self):
        """
        Mapping of block number to designated caller address.
        """
        return {
            block_number: self.pool_manager.caller_pool.getDesignatedCaller.call(self.call_key, self.target_block, self.grace_period, block_number)
            for block_number
            in range(self.target_block, self.last_block + 1)
        }

    def should_call_on_block(self, block_number):
        """
        Return whether an attempt to execute this call should be made on the
        provided block number.
        """
        # Before call window starts
        if self.target_block - 1 > block_number:
            return False

        # After call window ends.
        if block_number >= self.last_block:
            return False

        designated_caller = self.designated_callers.get(block_number + 1)

        # Not free for all or designated for our address.
        if designated_caller not in {EMPTY_ADDRESS, self.coinbase}:
            return False

        return True

    @cached_property
    def callable_blocks(self):
        """
        Set of block numbers that it's ok to try executing this call on.
        """
        return {
            block_number
            for block_number
            in range(self.target_block - 1, self.last_block)
            if self.should_call_on_block(block_number)
        }

    #
    #  Call properties.
    #
    @cached_property
    def contract_address(self):
        return self.alarm.getCallContractAddress.call(self.call_key)

    @cached_property
    def scheduled_by(self):
        return self.alarm.getCallScheduledBy.call(self.call_key)

    @cache_once(0)
    def called_at_block(self):
        return self.alarm.getCallCalledAtBlock.call(self.call_key)

    @cached_property
    def target_block(self):
        return self.alarm.getCallTargetBlock.call(self.call_key)

    @cached_property
    def grace_period(self):
        return self.alarm.getCallGracePeriod.call(self.call_key)

    @cached_property
    def base_gas_price(self):
        return self.alarm.getCallBaseGasPrice.call(self.call_key)

    @cache_once(0)
    def gas_price(self):
        return self.alarm.getCallGasPrice.call(self.call_key)

    @cache_once(0)
    def gas_used(self):
        return self.alarm.getCallGasUsed.call(self.call_key)

    @cache_once(0)
    def payout(self):
        return self.alarm.getCallPayout.call(self.call_key)

    @cache_once(0)
    def fee(self):
        return self.alarm.getCallFee.call(self.call_key)

    @cached_property
    def abi_signature(self):
        return self.alarm.getCallABISignature.call(self.call_key)

    _is_cancelled = None

    @property
    def is_cancelled(self):
        """
        This value can be cached as soon as it is either truthy or passed the
        cancellation window.
        """
        if self._is_cancelled is not None:
            return self._is_cancelled

        value = self.alarm.checkIfCancelled.call(self.call_key)
        if value or self.block_sage.current_block_number > self.target_block - CANCELLATION_WINDOW:
            self._is_cancelled = value
        return value

    @cache_once(False)
    def was_called(self):
        return self.alarm.checkIfCalled.call(self.call_key)

    _was_successful = None

    @property
    def was_successful(self):
        """
        Cached once `was_called` returns true.
        """
        if self._was_successful is None:
            if not self.was_called:
                return False
            self._was_successful = self.alarm.checkIfSuccess.call(self.call_key)
        return bool(self._was_successful)

    @cached_property
    def data_hash(self):
        return self.alarm.getCallDataHash.call(self.call_key)
