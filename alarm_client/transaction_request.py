NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


class RequestData(object):
    _contract = None

    def __init__(self,
                 # claim
                 claimedBy,
                 claimDeposit,
                 paymentModifier,
                 # meta
                 createdBy,
                 owner,
                 isCancelled,
                 wasCalled,
                 wasSuccessful,
                 # payment
                 anchorGasPrice,
                 donation,
                 donationBenefactor,
                 donationOwed,
                 payment,
                 paymentBenefactor,
                 paymentOwed,
                 # txnData
                 callData,
                 toAddress,
                 callGas,
                 callValue,
                 requiredStackDepth,
                 # schedule
                 claimWindowSize,
                 freezePeriod,
                 windowStart,
                 windowSize,
                 reservedWindowSize,
                 temporalUnit):

        if freezePeriod is None:
            if temporalUnit == 0:
                freezePeriod = 10 * 17
            else:
                freezePeriod = 10

        if windowSize is None:
            if temporalUnit == 0:
                windowSize = 255 * 17
            else:
                windowSize = 255

        if windowStart is None:
            if temporalUnit == 0:
                windowStart = web3.eth.getBlock('latest')['timestamp'] + freezePeriod
            else:
                windowStart = web3.eth.blockNumber + freezePeriod

        if reservedWindowSize is None:
            if temporalUnit == 0:
                reservedWindowSize = 16 * 17
            else:
                reservedWindowSize = 16

        self.claimData = type('claimData', (object,), {
            'claimedBy': claimedBy,
            'claimDeposit': claimDeposit,
            'paymentModifier': paymentModifier,
        })
        self.meta = type('meta', (object,), {
            'createdBy': createdBy,
            'owner': owner,
            'isCancelled': isCancelled,
            'wasCalled': wasCalled,
            'wasSuccessful': wasSuccessful,
        })
        self.paymentData = type('paymentData', (object,), {
            'anchorGasPrice': anchorGasPrice,
            'donation': donation,
            'donationBenefactor': donationBenefactor,
            'donationOwed': donationOwed,
            'payment': payment,
            'paymentBenefactor': paymentBenefactor,
            'paymentOwed': paymentOwed,
        })
        self.txnData = type('txnData', (object,), {
            'callData': callData,
            'toAddress': toAddress,
            'callGas': callGas,
            'callValue': callValue,
            'requiredStackDepth': requiredStackDepth,
        })
        self.schedule = type('schedule', (object,), {
            'claimWindowSize': claimWindowSize,
            'freezePeriod': freezePeriod,
            'reservedWindowSize': reservedWindowSize,
            'temporalUnit': temporalUnit,
            'windowStart': windowStart,
            'windowSize': windowSize,
        })

    def to_factory_kwargs(self):
        return {
            'addressArgs': [
                self.meta.owner,
                self.paymentData.donationBenefactor,
                self.txnData.toAddress,
            ],
            'uintArgs': [
                self.paymentData.donation,
                self.paymentData.payment,
                self.schedule.claimWindowSize,
                self.schedule.freezePeriod,
                self.schedule.reservedWindowSize,
                self.schedule.temporalUnit,
                self.schedule.windowStart,
                self.schedule.windowSize,
                self.txnData.callGas,
                self.txnData.callValue,
                self.txnData.requiredStackDepth,
            ],
            'callData': self.txnData.callData,
        }

    def deploy_via_factory(self, deploy_txn=None):
        if deploy_txn is None:
            deploy_txn = {'value': 10 * denoms.ether}
        create_txn_hash = request_factory.transact(
            deploy_txn,
        ).createRequest(
            **self.to_factory_kwargs()
        )
        txn_request = get_txn_request(create_txn_hash)
        return txn_request

    def to_init_kwargs(self):
        return {
            'addressArgs': [
                self.meta.createdBy,
                self.meta.owner,
                self.paymentData.donationBenefactor,
                self.txnData.toAddress,
            ],
            'uintArgs': [
                self.paymentData.donation,
                self.paymentData.payment,
                self.schedule.claimWindowSize,
                self.schedule.freezePeriod,
                self.schedule.reservedWindowSize,
                self.schedule.temporalUnit,
                self.schedule.windowStart,
                self.schedule.windowSize,
                self.txnData.callGas,
                self.txnData.callValue,
                self.txnData.requiredStackDepth,
            ],
            'callData': self.txnData.callData,
        }

    def direct_deploy(self, deploy_txn=None):
        if deploy_txn is None:
            deploy_txn = {'value': 10 * denoms.ether}
        deploy_txn_hash = TransactionRequest.deploy(
            transaction=deploy_txn,
            kwargs=self.to_init_kwargs(),
        )
        txn_request_address = chain.wait.for_contract_address(deploy_txn_hash)
        return TransactionRequest(address=txn_request_address)

    def refresh(self):
        if not self._contract:
            raise ValueError("No contract set")
        self.__dict__.update(self.from_contract(self._contract).__dict__)

    @classmethod
    def from_contract(cls, txn_request):
        address_args, bool_args, uint_args, uint8_args = txn_request.call().requestData()
        call_data = txn_request.call().callData()
        instance = cls.from_deserialize(
            address_args, bool_args, uint_args, uint8_args, call_data,
        )
        instance._contract = txn_request
        return instance

    @classmethod
    def from_deserialize(cls, address_args, bool_args, uint_args, uint8_args, call_data):
        init_kwargs = {
            'claimedBy': address_args[0],
            'createdBy': address_args[1],
            'owner': address_args[2],
            'donationBenefactor': address_args[3],
            'paymentBenefactor': address_args[4],
            'toAddress': address_args[5],
            'wasCalled': bool_args[1],
            'wasSuccessful': bool_args[2],
            'isCancelled': bool_args[0],
            'paymentModifier': uint8_args[0],
            'claimDeposit': uint_args[0],
            'anchorGasPrice': uint_args[1],
            'donation': uint_args[2],
            'donationOwed': uint_args[3],
            'payment': uint_args[4],
            'paymentOwed': uint_args[5],
            'claimWindowSize': uint_args[6],
            'freezePeriod': uint_args[7],
            'reservedWindowSize': uint_args[8],
            'temporalUnit': uint_args[9],
            'windowStart': uint_args[10],
            'windowSize': uint_args[11],
            'callGas': uint_args[12],
            'callValue': uint_args[13],
            'requiredStackDepth': uint_args[14],
            'callData': call_data,
        }
        return cls(**init_kwargs)
