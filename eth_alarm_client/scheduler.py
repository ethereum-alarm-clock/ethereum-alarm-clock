import threading
import time

from .block_sage import BlockSage
from .scheduled_call import ScheduledCall
from .utils import (
    get_logger,
    cached_property,
    enumerate_upcoming_calls,
)


class Scheduler(object):
    def __init__(self, scheduler, pool_manager, block_sage=None):
        self.logger = get_logger('scheduler')
        self.scheduler = scheduler
        self.pool_manager = pool_manager

        if block_sage is None:
            block_sage = BlockSage(self.blockchain_client)
        self.block_sage = block_sage

        self.active_calls = {}

    @property
    def blockchain_client(self):
        return self.scheduler._meta.blockchain_client

    @cached_property
    def coinbase(self):
        return self.blockchain_client.get_coinbase()

    def monitor_async(self):
        self._run = True
        self._thread = threading.Thread(target=self.monitor)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._run = False

    def monitor(self):
        while getattr(self, '_run', True):
            self.schedule_upcoming_calls()
            self.cleanup_finished_calls()
            time.sleep(self.block_sage.block_time)

    def schedule_upcoming_calls(self):
        upcoming_calls = enumerate_upcoming_calls(
            self.scheduler,
            self.block_sage.current_block_number,
        )

        for call_address in upcoming_calls:
            if call_address in self.active_calls:
                continue

            scheduled_call = ScheduledCall(
                self.scheduler,
                call_address,
                block_sage=self.block_sage,
            )

            if scheduled_call.has_been_suicided:
                continue

            self.logger.info("Tracking call: %s", scheduled_call.call_address)
            scheduled_call.execute_async()
            self.active_calls[call_address] = scheduled_call

    def cleanup_finished_calls(self):
        for call_address, scheduled_call in tuple(self.active_calls.items()):

            if scheduled_call.txn_hash:
                self.logger.info("Removing finished call: %s", call_address)
                self.active_calls.pop(call_address)
            elif scheduled_call.last_block < self.block_sage.current_block_number:
                scheduled_call.stop()
                self.logger.info("Removing expired call: %s", call_address)
                self.active_calls.pop(call_address)
            elif not scheduled_call._thread.is_alive():
                self.logger.info("Removing dead call: %s", call_address)
                self.active_calls.pop(call_address)
