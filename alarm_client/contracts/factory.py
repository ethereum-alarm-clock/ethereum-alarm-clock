import json
from web3.contract import Contract


FACTORY_ABI = json.loads('[{"constant":false,"inputs":[{"name":"addressArgs","type":"address[3]"},{"name":"uintArgs","type":"uint256[11]"},{"name":"callData","type":"bytes"},{"name":"endowment","type":"uint256"}],"name":"validateRequestParams","outputs":[{"name":"","type":"bool[7]"}],"type":"function"},{"constant":false,"inputs":[{"name":"addressArgs","type":"address[3]"},{"name":"uintArgs","type":"uint256[11]"},{"name":"callData","type":"bytes"}],"name":"createValidatedRequest","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":false,"inputs":[{"name":"addressArgs","type":"address[3]"},{"name":"uintArgs","type":"uint256[11]"},{"name":"callData","type":"bytes"}],"name":"createRequest","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":false,"inputs":[{"name":"_address","type":"address"}],"name":"isKnownRequest","outputs":[{"name":"","type":"bool"}],"type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"request","type":"address"}],"name":"RequestCreated","type":"event"}]')  # noqa


class RequestFactoryFactory(Contract):
    pass


def get_factory(web3, address):
    return web3.eth.contract(
        abi=FACTORY_ABI,
        address=address,
        base_contract_factory_class=RequestFactoryFactory,
    )
