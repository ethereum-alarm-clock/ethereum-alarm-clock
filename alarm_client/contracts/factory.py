from web3.contract import Contract


MINUTE = 60
BLOCKS = 1
TIMESTAMP = 2


class PendingTransactionRequest(object):
    owner = None
    donationBenefactor = None
    toAddress = None
    donation = None
    payment = None
    claimWindowSize = None
    freezePeriod = None
    reservedWindowSize = None
    temporalUnit = None
    windowSize = None
    windowStart = None
    callGas = None
    callValue = None
    requiredStackDepth = None
    callData = None

    def __init__(self,
                 owner,
                 donationBenefactor,
                 toAddress,
                 donation,
                 payment,
                 claimWindowSize,
                 freezePeriod,
                 reservedWindowSize,
                 temporalUnit,
                 windowSize,
                 windowStart,
                 callGas,
                 callValue,
                 requiredStackDepth,
                 callData):
        self.owner = owner
        self.donationBenefactor = donationBenefactor
        self.toAddress = toAddress
        self.donation = donation
        self.payment = payment
        self.claimWindowSize = claimWindowSize
        self.freezePeriod = freezePeriod
        self.reservedWindowSize = reservedWindowSize
        self.temporalUnit = temporalUnit
        self.windowSize = windowSize
        self.windowStart = windowStart
        self.callGas = callGas
        self.callValue = callValue
        self.requiredStackDepth = requiredStackDepth
        self.callData = callData

    def __str__(self):
        return "Transaction Request:\n{0}".format(self.get_props_display())

    def __repr__(self):
        return str(self)

    def get_props_display(self):
        return '\n'.join((
            "- owner: {s.owner}",
            "- donationBenefactor: {s.donationBenefactor}",
            "- toAddress: {s.toAddress}",
            "- donation: {s.donation}",
            "- payment: {s.payment}",
            "- claimWindowSize: {s.claimWindowSize}",
            "- freezePeriod: {s.freezePeriod}",
            "- reservedWindowSize: {s.reservedWindowSize}",
            "- temporalUnit: {s.temporalUnit}",
            "- windowSize: {s.windowSize}",
            "- windowStart: {s.windowStart}",
            "- callGas: {s.callGas}",
            "- callValue: {s.callValue}",
            "- requiredStackDepth: {s.requiredStackDepth}",
            "- callData: {s.callData}",
        )).format(s=self)

    def to_init_kwargs(self):
        return {
            'addressArgs': [
                self.owner,
                self.donationBenefactor,
                self.toAddress,
            ],
            'uintArgs': [
                self.donation,
                self.payment,
                self.claimWindowSize,
                self.freezePeriod,
                self.reservedWindowSize,
                self.temporalUnit,
                self.windowSize,
                self.windowStart,
                self.callGas,
                self.callValue,
                self.requiredStackDepth,
            ],
            'callData': self.callData,
        }


class RequestFactoryFactory(Contract):
    def construct_pending_request(self,
                                  toAddress,
                                  # meta
                                  owner=None,
                                  # payment
                                  donation=None,
                                  donationBenefactor='0xd3cda913deb6f67967b99d67acdfa1712c293601',
                                  payment=None,
                                  # txnData
                                  callData="",
                                  callGas=1000000,
                                  callValue=0,
                                  requiredStackDepth=10,
                                  # schedule
                                  claimWindowSize=None,
                                  freezePeriod=None,
                                  windowSize=None,
                                  windowStart=None,
                                  reservedWindowSize=None,
                                  temporalUnit=1):
            if payment is None:
                payment = self.web3.eth.gasPrice * 1000000

            if donation is None:
                donation = payment // 100

            if owner is None:
                owner = self.web3.eth.coinbase

            if freezePeriod is None:
                if temporalUnit == TIMESTAMP:
                    freezePeriod = 3 * MINUTE
                else:
                    freezePeriod = 10

            if windowSize is None:
                if temporalUnit == TIMESTAMP:
                    windowSize = 60 * MINUTE
                else:
                    windowSize = 255

            if windowStart is None:
                if temporalUnit == TIMESTAMP:
                    latest_block = self.web3.eth.getBlock('latest')
                    windowStart = latest_block['timestamp'] + freezePeriod + 2 * MINUTE
                else:
                    windowStart = self.web3.eth.blockNumber + freezePeriod + 8

            if reservedWindowSize is None:
                if temporalUnit == TIMESTAMP:
                    reservedWindowSize = 4 * MINUTE
                else:
                    reservedWindowSize = 16

            if claimWindowSize is None:
                if temporalUnit == TIMESTAMP:
                    claimWindowSize = 60 * MINUTE
                else:
                    claimWindowSize = 255

            return PendingTransactionRequest(
                owner=owner,
                donationBenefactor=donationBenefactor,
                toAddress=toAddress,
                donation=donation,
                payment=payment,
                claimWindowSize=claimWindowSize,
                freezePeriod=freezePeriod,
                reservedWindowSize=reservedWindowSize,
                temporalUnit=temporalUnit,
                windowSize=windowSize,
                windowStart=windowStart,
                callGas=callGas,
                callValue=callValue,
                requiredStackDepth=requiredStackDepth,
                callData=callData,
            )


def get_factory(web3, address, abi):
    return web3.eth.contract(
        abi=abi,
        address=address,
        base_contract_factory_class=RequestFactoryFactory,
    )
