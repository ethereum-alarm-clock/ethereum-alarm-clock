import threading
import time
import decimal


from .utils import get_logger


class BlockSage(object):
    """
    A single entity that can be queried for information on the latest block.
    """
    current_block_number = None
    current_block = None
    current_block_timestamp = None
    heartbeat = None

    def __init__(self, rpc_client, heartbeat=4):
        self.logger = get_logger('blocksage')
        self.rpc_client = rpc_client

        self.current_block_number = rpc_client.get_block_number()
        self.current_block = rpc_client.get_block_by_number(
            self.current_block_number, False,
        )
        self.current_block_timestamp = int(self.current_block['timestamp'], 16)

        self._run = True

        self.logger.info("Starting block sage")
        self._thread = threading.Thread(target=self.monitor_block_times)
        self._thread.daemon = True
        self._thread.start()

        self.heartbeat = heartbeat

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

    def estimated_time_to_block(self, block_number):
        return self.block_time * max(0, block_number - self.current_block_number)

    @property
    def expected_next_block_time(self):
        return self.current_block_timestamp + self.block_time

    _next_heartbeat = 0

    @property
    def next_heartbeat(self):
        if self.heartbeat and self._next_heartbeat is None:
            self._next_heartbeat = self.current_block_number + self.heartbeat
        return self._next_heartbeat

    @next_heartbeat.setter
    def next_heartbeat(self, value):
        self._next_heartbeat = value

    def do_heartbeat(self):
        if self.heartbeat:
            if self.current_block_number > self.next_heartbeat:
                self.logger.info(
                    "> Heartbeat: block #%s : block_time: %s",
                    self.current_block_number,
                    self.block_time,
                )
                self.next_heartbeat = self.current_block_number + self.heartbeat


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
        self.logger.info("Stopping Block Sage")
        self._run = False

    def monitor_block_times(self):
        """
        Monitor the latest block number as well as the time between blocks.
        """
        self.current_block_number = self.rpc_client.get_block_number()
        self.current_block = self.rpc_client.get_block_by_number(self.current_block_number, False)
        self.current_block_timestamp = int(self.current_block['timestamp'], 16)

        while self._run:
            self.do_heartbeat()
            sleep_time = self.sleep_time
            time.sleep(sleep_time)
            if self.rpc_client.get_block_number() > self.current_block_number:
                # Update block time.
                next_block = self.rpc_client.get_block_by_number(self.current_block_number + 1)
                if next_block is None:
                    logger.warning("Got `None` while fetching block %s", self.current_block_number + 1)
                    continue
                next_block_timestamp = int(next_block['timestamp'], 16)
                self.block_time = next_block_timestamp - self.current_block_timestamp

                # Grab current block data
                self.current_block_number = self.rpc_client.get_block_number()
                self.current_block = self.rpc_client.get_block_by_number(self.current_block_number, False)
                self.current_block_timestamp = int(self.current_block['timestamp'], 16)
                self.logger.debug(
                    "Block Number: %s - Block Time: %s",
                    self.current_block_number,
                    decimal.Decimal(str(self._block_time)).quantize(decimal.Decimal('1.00')),
                )
            elif time.time() > self.expected_next_block_time + 20 * self.block_time:
                delta = time.time() - self.expected_next_block_time
                if delta > 120 and int(delta) % 10 == 0:
                    self.logger.warning(
                        "Potentially stuck at block %s - Have waited %s seconds.",
                        self.current_block_number,
                        time.time() - self.current_block_timestamp,
                    )
