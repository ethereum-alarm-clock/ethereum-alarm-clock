import threading
import time

from populus.utils import wait_for_transaction

from .block_sage import BlockSage
from .utils import (
    get_logger,
    cached_property,
)


class PoolManager(object):
    logger = get_logger('pool_manager')

    def __init__(self, caller_pool, block_sage=None):
        self.caller_pool = caller_pool

        if block_sage is None:
            block_sage = BlockSage(self.rpc_client)
        self.block_sage = block_sage

    @property
    def rpc_client(self):
        return self.caller_pool._meta.rpc_client

    @cached_property
    def coinbase(self):
        return self.rpc_client.get_coinbase()

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
        if self.next_pool:
            block_delta = max(1, self.next_pool - self.block_sage.current_block_number)
            return 0.8 * self.block_sage.block_time * block_delta

        # If there is no next pool, snooze for about 1/2 of the minimum number
        # of blocks before something interesting could happen.
        return 0.8 * self.block_sage.block_time * self.pool_freeze_duration / 2

    def manage_membership(self):
        if self.in_any_pool:
            return

        # check bond balance.
        if self.bond_balance < self.minimum_bond:
            self.logger.error("Insufficient bond balance to enter the caller pool")
            self.stop()

        # check the next pool is not currently frozen.
        if self.next_pool and self.is_pool_frozen(self.next_pool):
            self.logger.info("Next pool is frozen and cannot be joined")
            return

        # double check the API agrees with our other checks.
        if not self.can_enter_pool:
            self.logger.warning("CallerPool unexpectedly said we couldn't enter")
            return

        self.logger.info("Entering caller pool")
        txn_hash = self.enter_pool()
        self.logger.debug("Entered caller pool with txn: %s", txn_hash)
        wait_for_transaction(self.rpc_client, txn_hash, 60)
        self.logger.info("Entered caller pool #%s", self.next_pool)

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
        #     txn_hash = self.caller_pool.deposit(value=deficit)
        #     self.logger.debug("Deposited %s: Txn Hash: %s", deficit, txn_hash)
        #     wait_for_transaction(
        #         self.rpc_client,
        #         txn_hash,
        #         4 * self.block_sage.block_time,
        #     )
        #     self.logger.debug("Received receipt for deposit transaction")

    #
    # Caller Pool API
    #
    @property
    def freeze_horizon(self):
        return self.block_sage.current_block_number + self.pool_freeze_duration

    def is_pool_frozen(self, pool_number):
        if self.block_sage.current_block_number < pool_number < self.freeze_horizon:
            return True
        return False

    def get_pool_size(self, pool_number):
        return self.caller_pool.getPoolSize.call(pool_number)

    @property
    def pool_freeze_duration(self):
        return self.caller_pool.getPoolFreezeDuration.call()

    @property
    def minimum_pool_length(self):
        return self.caller_pool.getPoolFreezeDuration.call()

    @property
    def active_pool(self):
        return self.caller_pool.getActivePoolKey.call()

    @property
    def next_pool(self):
        return self.caller_pool.getNextPoolKey.call()

    @property
    def in_any_pool(self):
        return self.caller_pool.isInAnyPool.call(self.coinbase)

    @property
    def in_active_pool(self):
        return self.caller_pool.isInPool.call(self.coinbase, self.active_pool)

    @property
    def in_next_pool(self):
        return self.caller_pool.isInPool.call(self.coinbase, self.next_pool)

    @property
    def can_enter_pool(self):
        return self.caller_pool.canEnterPool.call(self.coinbase)

    @property
    def can_exit_pool(self):
        return self.caller_pool.canExitPool.call(self.coinbase)

    def enter_pool(self):
        return self.caller_pool.enterPool.sendTransaction()

    def exit_pool(self):
        return self.caller_pool.exitPool.sendTransaction()

    #
    # Bond API
    #
    @property
    def bond_balance(self):
        return self.caller_pool.callerBonds.call(self.coinbase)

    @property
    def minimum_bond(self):
        return self.caller_pool.getMinimumBond.call()

    def deposit(self, value):
        return self.caller_pool.deposit.sendTransaction(value=value)
