from populus.contract import Contract as ContractFactory


NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


class TxnData(object):
    """
    callData="",
    toAddress=txn_recorder.address,
    callGas=1000000,
    callValue=0,
    requiredStackDepth=0,
    """
    def __init__(self, to_address, call_data, call_gas, call_value, required_stack_depth):
        self.to_address = to_ad
    pass


class Schedule(object):
    """
    claimWindowSize=255,
    freezePeriod=None,
    windowStart=None,
    windowSize=None,
    reservedWindowSize=None,
    temporalUnit=1):
    """
    pass


class ClaimData(object):
    """
    claimedBy=NULL_ADDRESS,
    claimDeposit=0,
    paymentModifier=0,
    """
    pass


class PaymentData(object):
    """
    anchorGasPrice=web3.eth.gasPrice,
    donation=12345,
    donationBenefactor='0xd3cda913deb6f67967b99d67acdfa1712c293601',
    donationOwed=0,
    payment=54321,
    paymentBenefactor=NULL_ADDRESS,
    paymentOwed=0,
    """
    pass


class Meta(object):
    """
    createdBy=web3.eth.coinbase,
    owner=web3.eth.coinbase,
    isCancelled=False,
    wasCalled=False,
    wasSuccessful=False,
    """
    pass


class BaseTransactionRequestFactory(ContractFactory):
