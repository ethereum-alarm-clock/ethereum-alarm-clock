import threading

from .block_sage import BlockSage
from .scheduled_call import ScheduledCall
from .utils import (
    get_logger,
    cached_property,
    enumerate_upcoming_calls,
)


class Scheduler(object):
    logger = get_logger('scheduler')

    def __init__(self, alarm, pool_manager, block_sage=None):
        self.alarm = alarm
        self.pool_manager = pool_manager

        if block_sage is None:
            block_sage = BlockSage(self.rpc_client)
        self.block_sage = block_sage

        self.active_calls = {}

    @property
    def rpc_client(self):
        return self.alarm._meta.rpc_client

    @cached_property
    def coinbase(self):
        return self.rpc_client.get_coinbase()

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

    def schedule_upcoming_calls(self):
        upcoming_calls = enumerate_upcoming_calls(self.alarm, self.block_sage.current_block_number)
        for call_key in upcoming_calls:
            if call_key in self.active_calls:
                continue

            scheduled_call = ScheduledCall(
                self.alarm, self.pool_manager, call_key, self.block_sage,
            )

            if scheduled_call.is_cancelled:
                continue

            self.logger.info("Tracking call: %s", scheduled_call.hex_call_key[:5])
            scheduled_call.execute_async()
            self.active_calls[call_key] = scheduled_call

    def cleanup_finished_calls(self):
        for call_key, scheduled_call in tuple(self.active_calls.items()):
            hex_call_key = scheduled_call.hex_call_key[:5]

            if scheduled_call.txn_hash:
                self.logger.info("Removing finished call: %s", hex_call_key)
                self.active_calls.pop(call_key)
            elif scheduled_call.target_block + scheduled_call.grace_period < self.block_sage.current_block_number:
                scheduled_call.stop()
                self.logger.info("Removing expired call: %s", hex_call_key)
                self.active_calls.pop(call_key)
            elif not scheduled_call._thread.is_alive():
                self.logger.info("Removing dead call: %s", hex_call_key)
                self.active_calls.pop(call_key)
