require('chai')
    .use(require('chai-as-promised'))
    .should()   

const expect = require('chai').expect

/// Contracts
const RequestFactory = artifacts.require('./RequestFactory.sol')
const RequestLib = artifacts.require('./RequestLib.sol')
const RequestTracker = artifacts.require('./RequestTracker.sol')
const TransactionRequest  = artifacts.require('./TransactionRequest.sol')

/// Brings in config.web3 (v1.0.0)
const config = require('../../config')
const ethUtil = require('ethereumjs-util')
const { parseRequestData } = require('../dataHelpers.js')

const NULL_ADDR = '0x0000000000000000000000000000000000000000'

/// Note - these tests were checked very well and should never be wrong.
/// If they start failing - look in the contracts.
contract('Request factory', async function(accounts) {

    it('should create a request with provided properties', async function() {
        /// Get the instance of the deployed RequestLib
        const requestLib = await RequestLib.deployed()
        expect(requestLib.address)
        .to.exist

        /// Get the current block
        const curBlock = await config.web3.eth.getBlockNumber()

        /// Set up the data for our transaction request
        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 10
        const windowStart = curBlock + 20
        const windowSize = 511
        const reservedWindowSize = 16
        const temporalUnit = 1
        const callValue = 123456789
        const callGas = 1000000
        const requiredDeposit = config.web3.utils.toWei('45', 'kwei')
        const testCallData = 'this-is-call-data'
        
        /// Validate the data with the RequestLib
        const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                accounts[2]
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            config.web3.utils.toWei('10') //endowment calculate actual endowment
        )

        isValid.forEach(bool => expect(bool).to.be.true)

        /// Now let's set up a factory and launch the request.
        
        /// We need a request tracker for the factory
        const requestTracker = await RequestTracker.deployed()
        expect(requestTracker.address)
        .to.exist

        /// Pass the request tracker to the factory
        const requestFactory = await RequestFactory.new(requestTracker.address)
        expect(requestFactory.address)
        .to.exist 

        /// Create a request with the same args we validated
        const createTx = await requestFactory.createRequest(
            [
                accounts[0],
                accounts[1], //donation benefactor
                accounts[2] // to
            ], [
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
                requiredDeposit
            ],
            testCallData
        )

        const logRequestCreated = createTx.logs.find(e => e.event === 'RequestCreated')
        expect(logRequestCreated.args.request)
        .to.exist
        
        /// Now let's create a transactionRequest instance
        const txRequest = await TransactionRequest.at(logRequestCreated.args.request)
        const requestData = await parseRequestData(txRequest)
    
        expect(requestData.meta.owner)
        .to.equal(accounts[0])

        expect(requestData.meta.createdBy)
        .to.equal(accounts[0])

        expect(requestData.meta.isCancelled)
        .to.be.false 

        expect(requestData.meta.wasCalled)
        .to.be.false 

        expect(requestData.meta.wasSuccessful)
        .to.be.false 

        expect(requestData.claimData.claimedBy)
        .to.equal(NULL_ADDR)

        expect(requestData.claimData.claimDeposit)
        .to.equal(0)

        expect(requestData.claimData.paymentModifier)
        .to.equal(0)

        expect(requestData.paymentData.donation)
        .to.equal(donation)

        expect(requestData.paymentData.donationBenefactor)
        .to.equal(accounts[1])

        expect(requestData.paymentData.donationOwed)
        .to.equal(0)

        expect(requestData.paymentData.payment)
        .to.equal(payment) 

        expect(requestData.paymentData.paymentBenefactor)
        .to.equal(NULL_ADDR)

        expect(requestData.paymentData.paymentOwed)
        .to.equal(0)

        expect(requestData.schedule.claimWindowSize)
        .to.equal(claimWindowSize)

        expect(requestData.schedule.freezePeriod)
        .to.equal(freezePeriod)

        expect(requestData.schedule.windowStart)
        .to.equal(windowStart)

        expect(requestData.schedule.reservedWindowSize)
        .to.equal(reservedWindowSize)

        expect(requestData.schedule.temporalUnit)
        .to.equal(1)

        expect(requestData.txData.toAddress)
        .to.equal(accounts[2])

        expect(await txRequest.callData())
        .to.equal(ethUtil.bufferToHex(
            Buffer.from(testCallData)
        ))

        expect(requestData.txData.callValue)
        .to.equal(callValue)

        expect(requestData.txData.callGas)
        .to.equal(callGas)

        /// Lastly, we just make sure that the transaction request
        ///  address is a known request for the factory.
        expect(await requestFactory.isKnownRequest(NULL_ADDR))
        .to.be.false //sanity check

        expect(await requestFactory.isKnownRequest(txRequest.address))
        .to.be.true
    })

    it('should test request factory insufficient endowment validation error', async function() {
        const curBlock = await config.web3.eth.getBlockNumber()

        const requestLib = await RequestLib.deployed()
        expect(requestLib.address).to.exist

        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 10
        const windowStart = curBlock + 20
        const windowSize = 255
        const reservedWindowSize = 16
        const temporalUnit = 1
        const callValue = 123456789
        const callGas = 1000000

        /// Validate the data with the RequestLib
        const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                accounts[2]
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            1 //endowment ATTENTION THIS IS TOO SMALL, HENCE WHY IT FAILS
        )

        expect(isValid[0])
        .to.be.false 

        isValid.slice(1).forEach(bool => expect(bool).to.be.true)
    })

    it('should test request factory throws validation error on too large of a reserve window', async function() {
        const curBlock = await config.web3.eth.getBlockNumber()
        
        const requestLib = await RequestLib.deployed()
        expect(requestLib.address).to.exist

        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 10
        const windowStart = curBlock + 20
        const windowSize = 255
        const reservedWindowSize = 255 + 2 // 2 more than window size
        const temporalUnit = 1
        const callValue = 123456789
        const callGas = 1000000

         /// Validate the data with the RequestLib
         const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                accounts[2]
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            config.web3.utils.toWei('10') //endowment
        )

        expect(isValid[1])
        .to.be.false

        expect(isValid[0])
        .to.be.true 

        isValid.slice(2).forEach(bool => expect(bool).to.be.true)
    })

    it('should test request factory throws invalid temporal unit validation error', async function() {
        const curBlock = await config.web3.eth.getBlockNumber()
        
        const requestLib = await RequestLib.deployed()
        expect(requestLib.address).to.exist

        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 10
        const windowStart = curBlock + 20
        const windowSize = 255
        const reservedWindowSize = 16
        const temporalUnit = 3 // Only 1 and 2 are supported
        const callValue = 123456789
        const callGas = 1000000

         /// Validate the data with the RequestLib
         const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                accounts[2]
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            config.web3.utils.toWei('10') //endowment
        )

        expect(isValid[2])
        .to.be.false 

        expect(isValid[3])
        .to.be.false 

        isValid.slice(0, 2).forEach(bool => expect(bool).to.be.true)
        isValid.slice(4).forEach(bool => expect(bool).to.be.true)
    })

    it('should test request factory too soon execution window validation error', async function() {
        const curBlock = await config.web3.eth.getBlockNumber()
        
        const requestLib = await RequestLib.deployed()
        expect(requestLib.address).to.exist

        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 11 // more than the blocks between now and the window start
        const windowStart = curBlock + 10
        const windowSize = 255
        const reservedWindowSize = 16
        const temporalUnit = 1
        const callValue = 123456789
        const callGas = 1000000

         /// Validate the data with the RequestLib
         const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                accounts[2]
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            config.web3.utils.toWei('10') //endowment
        )

        expect(isValid[3])
        .to.be.false 

        isValid.slice(0, 3).forEach(bool => expect(bool).to.be.true)
        isValid.slice(4).forEach(bool => expect(bool).to.be.true)
    })

    it('should test request factory has too high call gas validation error', async function() {
        const curBlock = await config.web3.eth.getBlockNumber()
        
        const requestLib = await RequestLib.deployed()
        expect(requestLib.address).to.exist

        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 10
        const windowStart = curBlock + 20
        const windowSize = 255
        const reservedWindowSize = 16
        const temporalUnit = 1
        const callValue = 123456789
        const callGas = 8.8e8 // cannot be over gas limit

         /// Validate the data with the RequestLib
         const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                accounts[2]
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            config.web3.utils.toWei('10') //endowment
        )

        expect(isValid[4])
        .to.be.false 

        isValid.slice(0, 4).forEach(bool => expect(bool).to.be.true)
        isValid.slice(5).forEach(bool => expect(bool).to.be.true)
    })

    it('should test null to address validation error', async function() {
        const curBlock = await config.web3.eth.getBlockNumber()
        
        const requestLib = await RequestLib.deployed()
        expect(requestLib.address).to.exist

        const claimWindowSize = 255
        const donation = 12345
        const payment = 54321
        const freezePeriod = 10
        const windowStart = curBlock + 20
        const windowSize = 255
        const reservedWindowSize = 16
        const temporalUnit = 1
        const callValue = 123456789
        const callGas = 1000000

         /// Validate the data with the RequestLib
         const isValid = await requestLib.validate(
            [
                accounts[0],
                accounts[0],
                accounts[1],
                NULL_ADDR // TO ADDRESS
            ], [
                donation,
                payment,
                claimWindowSize,
                freezePeriod,
                reservedWindowSize,
                temporalUnit,
                windowSize,
                windowStart,
                callGas,
                callValue
            ],
            'this-is-call-data',
            config.web3.utils.toWei('10') //endowment
        )

        expect(isValid[5])
        .to.be.false 

        isValid.slice(0, 5).forEach(bool => expect(bool).to.be.true)
    })
})