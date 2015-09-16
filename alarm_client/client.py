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


class ScheduledCall(object):
    txn_hash = None
    txn_receipt = None
    txn = None

    def __init__(self, alarm, call_key):
        self.call_key = call_key
        self.alarm = alarm

    @property
    def hex_call_key(self):
        return ethereum_utils.encode_hex(self.call_key)

    def should_execute(self):
        """
        1. not cancelled.
        2. before target_block + grace_period.
        3. scheduler has sufficient balance.
        """
        if self.is_cancelled:
            return False

        if self.rpc_client.get_block_number() > self.target_block + self.grace_period:
            return False

        latest_block = self.rpc_client.get_block_by_number("latest")
        gas_limit = int(latest_block['gasLimit'], 16)
        gas_price = self.rpc_client.get_gas_price()

        # Require 110% of max gas to be sure.
        if self.scheduler_account_balance < gas_limit * gas_price * 1.1:
            return False

        return True

    def execute(self):
        self.wait_for_call_window()
        if not self.should_execute():
            raise ValueError("Aborting")

        while self.rpc_client.get_block_number() < self.target_block - 1:
            time.sleep(1)

        while True:
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
        return self.alarm.doCall.sendTransaction(self.call_key)

    def wait_for_call_window(self, buffer=2):
        """
        wait for self.target_block - buffer (~30 seconds at 2 blocks)
        """
        current_block_number = self.rpc_client.get_block_number()
        current_block = self.rpc_client.get_block_by_number(current_block_number, False)
        current_block_timestamp = int(current_block['timestamp'], 16)

        if current_block_number > self.target_block + self.grace_period:
            raise ValueError("Already passed call execution window")

        print "Waiting for block #{0}".format(self.target_block)

        while current_block_number < self.target_block - buffer - 4:
            time.sleep(self.block_time * 0.75)
            if self.rpc_client.get_block_number() > current_block_number:
                # Update block time.
                next_block_timestamp = int(self.rpc_client.get_block_by_number(current_block_number + 1)['timestamp'], 16)
                self.block_time = next_block_timestamp - current_block_timestamp

                # Grab current block data
                current_block_number = self.rpc_client.get_block_number()
                current_block = self.rpc_client.get_block_by_number(current_block_number, False)
                current_block_timestamp = int(current_block['timestamp'], 16)
                print "At block #{0}. Approximately {1} seconds remaining".format(
                    current_block_number,
                    int((self.target_block - 2 - current_block_number) * self.block_time),
                )
            else:
                time.sleep(1)

        #  Now we're within a block
        while self.rpc_client.get_block_number() < self.target_block - buffer:
            time.sleep(0.5)

    #
    #  Meta Properties
    #
    @property
    def rpc_client(self):
        return self.alarm._meta.rpc_client

    @property
    def scheduler_account_balance(self):
        return self.alarm.accountBalances.call(self.scheduled_by)

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
        self._block_time = (
            ((self._block_sample_window - 1) * self._block_time + value) / self._block_sample_window
        )

    #
    #  Call properties.
    #
    @property
    def target_address(self):
        return self.alarm.getCallTargetAddress.call(self.call_key)

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
    def sig(self):
        return self.alarm.getCallSignature.call(self.call_key)

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
