from web3.contract import Contract


class TrackerFactory(Contract):
    pass


def get_tracker(web3, address, abi):
    return web3.eth.contract(
        abi=abi,
        address=address,
        base_contract_factory_class=TrackerFactory,
    )
