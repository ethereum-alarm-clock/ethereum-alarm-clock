from eth_rpc_client import Client
from populus.contracts import Contract


def load_alarm_contract(src_path, contract_name='AlarmAPI'):
    with open(src_path) as src_file:
        src_data = json.loads(src_file.read())

    alarm_contract_meta = src_data[contract_name]

    return Contract(alarm_contract_meta, contract_name)


class ScheduledCall(object):
    def __init__(self, alarm, call_key):
        self.call_key = call_key
        self.alarm = alarm

    def execute(self):
        assert False

    #
    #  Meta Properties
    #
    @property
    def scheduler_account_balance(self):
        return self.alarm.accountBalances.call(self.scheduled_by)

    _block_time = 15.0
    _block_sample_window = 20

    @property
    def block_time(self):
        """
        Return the current observed average block time.
        """
        return self._block_time

    @block_time.setter
    def block_time(self, value):
        self._block_time = (
            (self._block_sample_window - 1) * self._block_time + value) / self._block_sample_window
        )

    #
    #  Call properties.
    #
    @property
    def target_block(self):
        return self.alarm.getCallTargetAddress.call(callKey)

    @property
    def scheduled_by(self):
        return self.alarm.getCallScheduledBy.call(callKey)

    @property
    def called_at_block(self):
        return self.alarm.getCallCalledAtBlock.call(callKey)

    @property
    def target_block(self):
        return self.alarm.getCallTargetBlock.call(callKey)

    @property
    def base_gas_price(self):
        return self.alarm.getCallBaseGasPrice.call(callKey)

    @property
    def gas_price(self):
        return self.alarm.getCallGasPrice.call(callKey)

    @property
    def gas_used(self):
        return self.alarm.getCallGasUsed.call(callKey)

    @property
    def payout(self):
        return self.alarm.getCallPayout.call(callKey)

    @property
    def fee(self):
        return self.alarm.getCallFee.call(callKey)

    @property
    def sig(self):
        return self.alarm.getCallSignature.call(callKey)

    @property
    def is_cancelled(self):
        return self.alarm.checkIfCancelled.call(callKey)

    @property
    def was_called(self):
        return self.alarm.checkIfCalled.call(callKey)

    @property
    def was_successful(self):
        return self.alarm.checkIfSuccess.call(callKey)

    @property
    def data_hash(self):
        return self.alarm.getCallData.call(callKey)
