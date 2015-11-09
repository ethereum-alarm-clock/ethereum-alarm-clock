import threading
import time

from ethereum import utils as ethereum_utils

from .block_sage import BlockSage
from .utils import (
    cached_property,
    cache_once,
    get_logger
)

from .contracts import FutureBlockCall


EMPTY_ADDRESS = '0x0000000000000000000000000000000000000000'
CANCELLATION_WINDOW = 8

MAX_CALL_OVERHEAD_GAS = 200000
DEFAULT_CALL_GAS = 1000000


class ScheduledCall(object):
    """
    Abstraction to represent an upcoming function call.  Can monitor for
    """
    txn_hash = None
    txn_receipt = None
    txn = None

    def __init__(self, scheduler, call_address, block_sage=None):
        self.call_address = call_address
        self.scheduler = scheduler
        self.call = FutureBlockCall(call_address, self.blockchain_client)
        self.logger = get_logger('call-{0}'.format(self.call_address))

        if block_sage is None:
            block_sage = BlockSage(self.blockchain_client)
        self.block_sage = block_sage
        if self.blockchain_client.get_block_number() < self.target_block - 80:
            self.logger.warning(
                "It is not advisable to work with a ScheduledCall until the "
                "40-80 blocks before its target block"
            )

    #
    # Execution Pre Requesites
    #
    @cached_property
    def is_designated_caller(self):
        if not self.is_designated:
            return True
        return self.designated_caller_addresses.intersection((
            self.coinbase, EMPTY_ADDRESS,
        ))

    @property
    def is_expired(self):
        return self.block_sage.current_block_number >= self.last_block

    @property
    def call_gas(self):
        if self.suggested_gas:
            return MAX_CALL_OVERHEAD_GAS + self.suggested_gas
        else:
            return MAX_CALL_OVERHEAD_GAS + DEFAULT_CALL_GAS

    @property
    def scheduler_can_pay(self):
        gas_cost = self.call_gas * self.blockchain_client.get_gas_price()
        max_payment = 2 * self.base_payment
        max_fee = 2 * self.base_fee

        return gas_cost + max_payment + max_fee < self.balance

    def stop(self):
        self._run = False

    def validate_call(self):
        if not self.is_designated_caller:
            raise ValueError("Not in the designated callers")

        if self.has_been_suicided:
            raise ValueError("Contract Suicided")

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
                time.sleep(2)
                continue

            # Execute the transaction
            self.logger.info("Attempting to execute call")
            txn_hash = self.scheduler.execute(self.call_address)

            # Wait for the transaction receipt.
            try:
                self.logger.debug("Waiting for transaction: %s", txn_hash)
                txn_receipt = self.blockchain_client.wait_for_transaction(
                    txn_hash,
                    self.block_sage.estimated_time_to_block(self.last_block) * 2,
                )
            except ValueError:
                self.logger.error("Unable to get transaction receipt: %s", txn_hash)
            else:
                self.logger.info("Transaction accepted.")
                self.txn_hash = txn_hash
                self.txn_receipt = txn_receipt
                self.txn = self.blockchain_client.get_transaction_by_hash(txn_hash)
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
            time.sleep(self.block_sage.estimated_time_to_block(self.target_block - buffer))

    #
    #  Meta Properties
    #
    @property
    def blockchain_client(self):
        return self.scheduler._meta.blockchain_client

    @cached_property
    def coinbase(self):
        return self.blockchain_client.get_coinbase()

    @property
    def balance(self):
        """
        The account balance of the scheduler for this call.
        """
        return self.blockchain_client.get_balance(self.call_address)

    @cached_property
    def last_block(self):
        """
        The last block number that this call can be executed on.
        """
        return self.target_block + self.grace_period

    @cached_property
    def is_designated(self):
        return self.scheduler.getDesignatedCaller(self.call_address, self.target_block)[0]

    @cached_property
    def designated_caller_addresses(self):
        return set(self.designated_callers.values())

    @cached_property
    def designated_callers(self):
        """
        Mapping of block number to designated caller address.
        """
        return {
            block_number: self.scheduler.getDesignatedCaller(self.call_address, block_number)[1]
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
        return self.call.contractAddress()

    @cached_property
    def scheduled_by(self):
        return self.call.schedulerAddress()

    @cached_property
    def target_block(self):
        return self.call.targetBlock()

    @cached_property
    def grace_period(self):
        return self.call.gracePeriod()

    @cached_property
    def anchor_gas_price(self):
        return self.call.anchorGasPrice()

    @cached_property
    def suggested_gas(self):
        return self.call.suggestedGas()

    @cached_property
    def base_payment(self):
        return self.call.basePayment()

    @cached_property
    def base_fee(self):
        return self.call.baseFee()

    @cached_property
    def abi_signature(self):
        return self.call.abiSignature()

    @property
    def has_been_suicided(self):
        return len(self.blockchain_client.get_code(self.call_address)) <= 2
