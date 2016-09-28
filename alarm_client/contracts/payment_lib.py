import json
from web3.contract import Contract


PAYMENT_LIB_ABI = json.loads('[{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"},{"name":"sendGas","type":"uint256"}],"name":"sendPayment","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[{"name":"endowment","type":"uint256"},{"name":"payment","type":"uint256"},{"name":"donation","type":"uint256"},{"name":"callGas","type":"uint256"},{"name":"callValue","type":"uint256"},{"name":"requiredStackDepth","type":"uint256"},{"name":"gasOverhead","type":"uint256"}],"name":"validateEndowment","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"}],"name":"sendDonation","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"},{"name":"sendGas","type":"uint256"}],"name":"sendDonation","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[{"name":"payment","type":"uint256"},{"name":"donation","type":"uint256"},{"name":"callGas","type":"uint256"},{"name":"callValue","type":"uint256"},{"name":"requiredStackDepth","type":"uint256"},{"name":"gasOverhead","type":"uint256"}],"name":"computeEndowment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"}],"name":"hasBenefactor","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"}],"name":"getMultiplier","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"}],"name":"getPayment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"},{"name":"paymentModifier","type":"uint8"}],"name":"getPaymentWithModifier","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"}],"name":"getDonation","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"self","type":"PaymentLib.PaymentDatastorage"}],"name":"sendPayment","outputs":[{"name":"","type":"bool"}],"type":"function"}]')  # noqa


class PaymentLibFactory(Contract):
    pass


def get_payment_lib(web3, address, abi=PAYMENT_LIB_ABI):
    return web3.eth.contract(
        abi=abi,
        address=address,
        base_contract_factory_class=PaymentLibFactory,
    )
