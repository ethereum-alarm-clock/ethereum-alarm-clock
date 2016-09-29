from web3.contract import Contract


class PaymentLibFactory(Contract):
    pass


def get_payment_lib(web3, address, abi):
    return web3.eth.contract(
        abi=abi,
        address=address,
        base_contract_factory_class=PaymentLibFactory,
    )
