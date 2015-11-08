import threading
import time

from .block_sage import BlockSage
from .utils import (
    get_logger,
    cached_property,
)


class PoolManager(object):
    logger = get_logger('pool_manager')

    def __init__(self, scheduler, block_sage=None):
        self.scheduler = scheduler

        if block_sage is None:
            block_sage = BlockSage(self.blockchain_client)
        self.block_sage = block_sage

    @property
    def blockchain_client(self):
        return self.scheduler._meta.blockchain_client

    @cached_property
    def coinbase(self):
        return self.blockchain_client.get_coinbase()

    #
    # Main event loop
    #
    _run = True

    def stop(self):
        self._run = False

    def monitor(self):
        while self._run:
            self.manage_bond()
            self.manage_membership()
            snooze_time = self.get_snooze_time()
            self.logger.debug("Snoozing for %s seconds", int(snooze_time))
            time.sleep(snooze_time)

    def monitor_async(self):
        self._run = True
        self._thread = threading.Thread(target=self.monitor)
        self._thread.daemon = True
        self._thread.start()

    def get_snooze_time(self):
        if self.next_generation_id:
            return 0.8 * self.block_sage.estimated_time_to_block(self.next_generation_start_at)

        # If there is no next pool, snooze for about 1/2 of the minimum number
        # of blocks before something interesting could happen.
        return 0.8 * self.block_sage.estimated_time_to_block(
            self.block_sage.current_block_number + (
                (self.pool_freeze_duration + self.pool_rotation_delay) / 2
            )
        )

    def manage_membership(self):
        if self.in_any_pool:
            return

        # check bond balance.
        if self.bond_balance < self.minimum_bond:
            self.logger.error("Insufficient bond balance to enter the caller pool")
            self.stop()

        # check the next pool is not currently frozen.
        if self.next_generation_id and self.is_generation_frozen(self.next_generation_id):
            self.logger.info("Next pool is frozen and cannot be joined")
            return

        # double check the API agrees with our other checks.
        if not self.can_enter_pool:
            self.logger.warning("CallerPool unexpectedly said we couldn't enter")
            return

        self.logger.info("Entering caller pool")
        txn_hash = self.enter_pool()
        self.logger.debug("Entered caller pool with txn: %s", txn_hash)
        self.blockchain_client.wait_for_transaction(txn_hash, 60)
        self.logger.info("Entered caller pool at generation #%s", self.next_generation_id)

    def manage_bond(self):
        """
        This function is intentionally commented out and empty.  Having a
        hastily piece of code manage dumping funds into a system seems sketchy.
        For now, it'll have to be managed manually.
        """
        pass
        # if self.bond_balance < self.minimum_bond * 2:
        #     deficit = self.minimum_bond * 2 - self.bond_balance
        #     self.logger.info("Bond value below threshold.  Depositing %s", deficit)
        #     txn_hash = self.scheduler.deposit(value=deficit)
        #     self.logger.debug("Deposited %s: Txn Hash: %s", deficit, txn_hash)
        #     wait_for_transaction(
        #         self.blockchain_client,
        #         txn_hash,
        #         4 * self.block_sage.block_time,
        #     )
        #     self.logger.debug("Received receipt for deposit transaction")

    #
    # Caller Pool API
    #
    @property
    def freeze_horizon(self):
        return sum((
            self.block_sage.current_block_number,
            self.pool_freeze_duration,
            self.pool_rotation_delay,
        ))

    def is_generation_frozen(self, generation_id):
        generation_start_at = self.scheduler.getGenerationStartAt(generation_id)
        if self.block_sage.current_block_number < generation_start_at < self.freeze_horizon:
            return True
        return False

    def get_generation_size(self, generation_id):
        return self.scheduler.getGenerationSize(generation_id)

    @property
    def pool_freeze_duration(self):
        return self.scheduler.getPoolFreezePeriod()

    @property
    def pool_rotation_delay(self):
        return self.scheduler.getPoolRotationDelay()

    @property
    def pool_overlap_size(self):
        return self.scheduler.getPoolOverlapSize()

    @property
    def minimum_pool_length(self):
        assert False  # TODO
        return self.scheduler.getPoolFreezeDuration()

    @property
    def current_generation_id(self):
        return self.scheduler.getCurrentGenerationId()

    @property
    def current_generation_start_at(self):
        return self.scheduler.getGenerationStartAt(self.current_generation_id)

    @property
    def current_generation_end_at(self):
        return self.scheduler.getGenerationEndAt(self.current_generation_id)

    @property
    def next_generation_id(self):
        return self.scheduler.getNextGenerationId()

    @property
    def next_generation_start_at(self):
        return self.scheduler.getGenerationStartAt(self.next_generation_id)

    @property
    def next_generation_end_at(self):
        return self.scheduler.getGenerationEndAt(self.next_generation_id)

    @property
    def in_any_pool(self):
        return self.scheduler.isInPool()

    @property
    def in_current_generation(self):
        return self.scheduler.isInGeneration(self.coinbase, self.current_generation_id)

    @property
    def in_next_generation(self):
        return self.scheduler.isInGeneration(self.coinbase, self.next_generation_id)

    @property
    def can_enter_pool(self):
        return self.scheduler.canEnterPool(self.coinbase)

    @property
    def can_exit_pool(self):
        return self.scheduler.canExitPool(self.coinbase)

    def enter_pool(self):
        return self.scheduler.enterPool()

    def exit_pool(self):
        return self.scheduler.exitPool()

    #
    # Bond API
    #
    @property
    def bond_balance(self):
        return self.scheduler.getBondBalance()

    @property
    def minimum_bond(self):
        return self.scheduler.getMinimumBond()

    def deposit(self, value):
        return self.scheduler.deposit(value=value)
