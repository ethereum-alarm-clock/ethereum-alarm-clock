from web3.contract import Contract


class RequestLibFactory(Contract):
    pass


def get_request_lib(web3, address, abi):
    return web3.eth.contract(
        abi=abi,
        address=address,
        base_contract_factory_class=RequestLibFactory,
    )
