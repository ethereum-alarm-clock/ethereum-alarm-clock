import json
from web3.contract import Contract


SCHEDULER_ABI = json.loads('[{"constant":true,"inputs":[],"name":"temporalUnit","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"factoryAddress","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":false,"inputs":[{"name":"toAddress","type":"address"},{"name":"callData","type":"bytes"},{"name":"uintArgs","type":"uint256[7]"}],"name":"scheduleTransaction","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":false,"inputs":[{"name":"toAddress","type":"address"},{"name":"callData","type":"bytes"},{"name":"uintArgs","type":"uint256[4]"}],"name":"scheduleTransaction","outputs":[{"name":"","type":"address"}],"type":"function"}]')  # noqa


class SchedulerFactory(Contract):
    pass


def get_scheduler(web3, address):
    return web3.eth.contract(
        abi=SCHEDULER_ABI,
        address=address,
        base_contract_factory_class=SchedulerFactory,
    )
