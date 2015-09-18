import threading
import json
import time

from ethereum import utils as ethereum_utils

from populus.contracts import Contract
from populus.utils import wait_for_transaction


def load_alarm_contract(src_path, contract_name='AlarmAPI'):
    with open(src_path) as src_file:
        src_data = json.loads(src_file.read())

    alarm_contract_meta = src_data[contract_name]

    return Contract(alarm_contract_meta, contract_name)


class BlockSage(object):
    """
    A single entity that can be queried for information on the latest block.
    """
    current_block_number = None
    current_block = None
    current_block_timestamp = None

    def __init__(self, rpc_client):
        self.rpc_client = rpc_client

        self._run = True

        self._thread = threading.Thread(target=self.monitor_block_times)
        self._thread.daemon = True
        self._thread.start()

    _block_time = 1.0
    _block_sample_window = 10

    @property
    def block_time(self):
        """
        Return the current observed average block time.
        """
        return self._block_time

    @block_time.setter
    def block_time(self, value):
        self._sleep_time = self._block_time = (
            ((self._block_sample_window - 1) * self._block_time + value) / self._block_sample_window
        )

    @property
    def expected_next_block_time(self):
        return self.current_block_timestamp + self.block_time

    _sleep_time = _block_time

    @property
    def sleep_time(self):
        self._sleep_time /= 2.0
        return max(self._sleep_time, 0.5)

    @sleep_time.setter
    def sleep_time(self, value):
        self._sleep_time = value

    def stop(self):
        """
        Signal to the monitor_block_times function that it can exit it's run
        loop.
        """
        self._run = False

    def monitor_block_times(self):
        """
        Monitor the latest block number as well as the time between blocks.
        """
        self.current_block_number = self.rpc_client.get_block_number()
        self.current_block = self.rpc_client.get_block_by_number(self.current_block_number, False)
        self.current_block_timestamp = int(self.current_block['timestamp'], 16)

        while self._run:
            time.sleep(self.sleep_time)
            if self.rpc_client.get_block_number() > self.current_block_number:
                # Update block time.
                next_block_timestamp = int(self.rpc_client.get_block_by_number(self.current_block_number + 1)['timestamp'], 16)
                self.block_time = next_block_timestamp - self.current_block_timestamp

                # Grab current block data
                self.current_block_number = self.rpc_client.get_block_number()
                self.current_block = self.rpc_client.get_block_by_number(self.current_block_number, False)
                self.current_block_timestamp = int(self.current_block['timestamp'], 16)


class ScheduledCall(object):
    """
    Abstraction to represent an upcoming function call.  Can monitor for
    """
    txn_hash = None
    txn_receipt = None
    txn = None

    def __init__(self, alarm, call_key, block_sage=None):
        self.call_key = call_key
        self.alarm = alarm

        if block_sage is None:
            block_sage = BlockSage(self.rpc_client)
        self.block_sage = block_sage

    @property
    def hex_call_key(self):
        return ethereum_utils.encode_hex(self.call_key)

    def should_execute(self):
        """
        - not cancelled.
        - not already called.
        - before target_block + grace_period.
        - scheduler has sufficient balance.
        """
        if self.was_called:
            # TODO: this check only needs to occur after self.target_block
            return False

        if self.is_cancelled:
            # TODO: this check only needs to occur once after self.target_block - 8
            return False

        if self.rpc_client.get_block_number() > self.target_block + self.grace_period:
            return False

        gas_limit = int(self.block_sage.current_block['gasLimit'], 16)
        gas_price = self.rpc_client.get_gas_price()

        # Require 110% of max gas to be sure.
        if self.scheduler_account_balance < gas_limit * gas_price * 1.1:
            return False

        return True

    def execute_async(self):
        self._run = True
        self._thread = threading.Thread(target=self.execute)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._run = False

    def execute(self):
        self.wait_for_call_window()
        if not self.should_execute():
            raise ValueError("Aborting")

        while getattr(self, '_run', True):
            if self.rpc_client.get_block_number() < self.target_block - 1:
                time.sleep(1)
            else:
                break

        while getattr(self, '_run', True):
            txn_hash = self.alarm.doCall.sendTransaction(self.call_key)
            try:
                txn_receipt = wait_for_transaction(self.rpc_client, txn_hash)
            except ValueError:
                if self.should_execute():
                    continue
                raise
            self.txn_hash = txn_hash
            self.txn_receipt = txn_receipt
            self.txn = self.rpc_client.get_transaction_by_hash(txn_hash)
            break

    def send_execute_transaction(self):
        """
        Send the transaction that will execute this scheduled call.
        """
        return self.alarm.doCall.sendTransaction(self.call_key)

    def wait_for_call_window(self, buffer=2):
        """
        wait for self.target_block - buffer (~30 seconds at 2 blocks)
        """
        if self.block_sage.current_block_number > self.target_block + self.grace_period:
            raise ValueError("Already passed call execution window")

        while self.block_sage.current_block_number < self.target_block - buffer:
            time.sleep(0.25)

    #
    #  Meta Properties
    #
    @property
    def rpc_client(self):
        return self.alarm._meta.rpc_client

    @property
    def scheduler_account_balance(self):
        return self.alarm.accountBalances.call(self.scheduled_by)

    #
    #  Call properties.
    #
    @property
    def contract_address(self):
        return self.alarm.getCallContractAddress.call(self.call_key)

    @property
    def scheduled_by(self):
        return self.alarm.getCallScheduledBy.call(self.call_key)

    @property
    def called_at_block(self):
        return self.alarm.getCallCalledAtBlock.call(self.call_key)

    @property
    def target_block(self):
        return self.alarm.getCallTargetBlock.call(self.call_key)

    @property
    def grace_period(self):
        return self.alarm.getCallGracePeriod.call(self.call_key)

    @property
    def base_gas_price(self):
        return self.alarm.getCallBaseGasPrice.call(self.call_key)

    @property
    def gas_price(self):
        return self.alarm.getCallGasPrice.call(self.call_key)

    @property
    def gas_used(self):
        return self.alarm.getCallGasUsed.call(self.call_key)

    @property
    def payout(self):
        return self.alarm.getCallPayout.call(self.call_key)

    @property
    def fee(self):
        return self.alarm.getCallFee.call(self.call_key)

    @property
    def abi_signature(self):
        return self.alarm.getCallABISignature.call(self.call_key)

    @property
    def is_cancelled(self):
        return self.alarm.checkIfCancelled.call(self.call_key)

    @property
    def was_called(self):
        return self.alarm.checkIfCalled.call(self.call_key)

    @property
    def was_successful(self):
        return self.alarm.checkIfSuccess.call(self.call_key)

    @property
    def data_hash(self):
        return self.alarm.getCallDataHash.call(self.call_key)


class Scheduler(object):
    def __init__(self, alarm, block_sage=None):
        self.alarm = alarm

        if block_sage is None:
            block_sage = BlockSage(self.rpc_client)
        self.block_sage = block_sage

        self.active_calls = {}

    @property
    def rpc_client(self):
        return self.alarm._meta.rpc_client

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

    def cleanup_finished_calls(self):
        for call_key, scheduled_call in tuple(self.active_calls.items()):
            if not scheduled_call._thread.is_alive():
                # TODO: log this?
                self.active_calls.pop(call_key)
            elif scheduled_call.txn_hash:
                self.active_calls.pop(call_key)
            elif scheduled_call.target_block + scheduled_call.grace_period < self.block_sage.current_block_number:
                self.active_calls.pop(call_key)

    def schedule_upcoming_calls(self):
        upcoming_calls = enumerate_upcoming_calls(self.alarm, self.block_sage.current_block_number)
        for call_key in upcoming_calls:
            if call_key in self.active_calls:
                continue

            scheduled_call = ScheduledCall(self.alarm, call_key, self.block_sage)

            if scheduled_call.is_cancelled:
                continue

            scheduled_call.execute_async()
            self.active_calls[call_key] = scheduled_call


def enumerate_upcoming_calls(alarm, anchor_block):
    block_cutoff = anchor_block + 40

    call_keys = []

    while anchor_block > 0 and anchor_block < block_cutoff:
        call_key = alarm.getNextCallKey.call(anchor_block)

        if call_key is None:
            break

        if alarm.getCallTargetBlock.call(call_key) > block_cutoff:
            break

        call_keys.append(call_key)

        sibling = call_key
        while sibling:
            sibling = alarm.getNextCallSibling.call(sibling)
            if sibling is not None:
                call_keys.append(sibling)

        anchor_block = alarm.getNextBlockWithCall.call(anchor_block + 1)

    return tuple(call_keys)
