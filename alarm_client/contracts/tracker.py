import json
from web3.contract import Contract


TRACKER_ABI = json.loads('[{"constant":false,"inputs":[{"name":"request","type":"address"},{"name":"startWindow","type":"uint256"}],"name":"addRequest","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":true,"inputs":[{"name":"factory","type":"address"},{"name":"request","type":"address"}],"name":"getNextRequest","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":true,"inputs":[{"name":"factory","type":"address"},{"name":"request","type":"address"}],"name":"getWindowStart","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"request","type":"address"}],"name":"removeRequest","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":true,"inputs":[{"name":"factory","type":"address"},{"name":"operator","type":"bytes2"},{"name":"value","type":"uint256"}],"name":"query","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":true,"inputs":[{"name":"factory","type":"address"},{"name":"request","type":"address"}],"name":"getPreviousRequest","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":true,"inputs":[{"name":"factory","type":"address"},{"name":"request","type":"address"}],"name":"isKnownRequest","outputs":[{"name":"","type":"bool"}],"type":"function"}]')  # noqa


class TrackerFactory(Contract):
    pass


def get_tracker(web3, address, abi=TRACKER_ABI):
    return web3.eth.contract(
        abi=abi,
        address=address,
        base_contract_factory_class=TrackerFactory,
    )
