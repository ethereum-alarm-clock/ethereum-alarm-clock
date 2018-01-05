require('chai')
    .use(require('chai-as-promised'))
    .should()   

const expect = require('chai').expect

/// Contracts
const TransactionRequest  = artifacts.require('./TransactionRequest.sol')
const TransactionRecorder = artifacts.require('./TransactionRecorder.sol')

/// Bring in config.web3 (v1.0.0)
const config = require('../../config')
const ethUtil = require('ethereumjs-util')
const { parseRequestData, parseAbortData, wasAborted } = require('../dataHelpers.js')
const { wait, waitUntilBlock } = require('@digix/tempo')(web3);

contract('Block execution', async function(accounts) {
    const Owner = accounts[0]
    const Benefactor = accounts[1]

    let txRequest
    let txRecorder

    const gasPrice = config.web3.utils.toWei('45', 'gwei')
    const requiredDeposit = config.web3.utils.toWei('33', 'kwei')  

    const executionWindow = 10
    const testData32 = ethUtil.bufferToHex(
        Buffer.from('A1B2'.padEnd(32, 'FF'))
    )

    beforeEach(async function () {
        const curBlock = await config.web3.eth.getBlockNumber()
        const windowStart = curBlock + 38

        txRecorder = await TransactionRecorder.new()
        expect(txRecorder.address)
        .to.exist

        txRequest = await TransactionRequest.new(
            [
                Owner,              //createdBy
                Owner,              //owner
                Benefactor,         //donationBenefactor
                txRecorder.address //toAddress
            ], [
                12345,                  //donation
                224455,                  //payment
                25,                 //claim window size
                5,                  //freeze period
                10,                 //reserved window size
                1,                  // temporal unit
                executionWindow,    //window size
                windowStart,        //windowStart
                200000,             //callGas
                0,                  //callValue
                gasPrice,
                requiredDeposit    
            ],
            testData32,              //callData
            {value: config.web3.utils.toWei('1')}
        )

        /// The first claim block is the current block + the number of blocks
        ///  until the window starts, minus the freeze period minus claim window size.
        const firstClaimBlock  = windowStart - 5 - 25
        await waitUntilBlock(0, firstClaimBlock);
        
        await txRequest.claim({
            value: config.web3.utils.toWei('1')
        })
    })

    /////////////
    /// Tests ///
    /////////////

    /// 1
    it('should reject the execution if its before the execution window', async function() {
        const requestData = await parseRequestData(txRequest)

        expect(await txRecorder.wasCalled())
        .to.be.false

        expect(requestData.meta.wasCalled)
        .to.be.false

        const now = await config.web3.eth.getBlockNumber()

        expect(now)
        .to.be.below(requestData.schedule.windowStart)

        const executeTx = await txRequest.execute({gas: 3000000})

        const requestDataTwo = await parseRequestData(txRequest)

        expect(await txRecorder.wasCalled())
        .to.be.false 

        expect(requestDataTwo.meta.wasCalled)
        .to.be.false 

        expect(wasAborted(executeTx))
        .to.be.true

        expect(parseAbortData(executeTx).find(reason => reason === 'BeforeCallWindow'))
        .to.exist
    })

    /// 2
    it('should reject the execution if its after the execution window', async function() {
        const requestData = await parseRequestData(txRequest)

        expect(await txRecorder.wasCalled())
        .to.be.false 

        expect(requestData.meta.wasCalled)
        .to.be.false 

        const endExecutionWindow = requestData.schedule.windowStart + requestData.schedule.windowSize
        await waitUntilBlock(0, endExecutionWindow + 1)

        expect(await config.web3.eth.getBlockNumber())
        .to.be.above(endExecutionWindow)

        const executeTx = await txRequest.execute({gas: 3000000})

        const requestDataTwo = await parseRequestData(txRequest)

        expect(await txRecorder.wasCalled())
        .to.be.false 

        expect(requestDataTwo.meta.wasCalled)
        .to.be.false 

        expect(wasAborted(executeTx))
        .to.be.true 

        expect(parseAbortData(executeTx).find(reason => reason === 'AfterCallWindow'))
        .to.exist
    })

    /// 3
    it('should allow the execution at the start of the execution window', async function() {
        const requestData = await parseRequestData(txRequest)

        expect(await txRecorder.wasCalled())
        .to.be.false 

        expect(requestData.meta.wasCalled)
        .to.be.false 

        const startExecutionWindow = requestData.schedule.windowStart
        await waitUntilBlock(0, startExecutionWindow)

        const balBeforeExecute = await config.web3.eth.getBalance(accounts[0])

        const executeTx = await txRequest.execute(
            {
                from: accounts[0],
                gas: 3000000,
                gasPrice: gasPrice 
            }
        )
        expect(executeTx.receipt)
        .to.exist 

        const balAfterExecute = await config.web3.eth.getBalance(accounts[0])

        expect(parseInt(balAfterExecute))
        .to.be.at.least(parseInt(balBeforeExecute))

        const requestDataTwo = await parseRequestData(txRequest)

        expect(await txRecorder.wasCalled())
        .to.be.true 

        expect(requestDataTwo.meta.wasCalled)
        .to.be.true 
    })

    /// 4
    it('should allow the execution at the end of the execution window', async function() {
        const requestData = await parseRequestData(txRequest) 

        expect(await txRecorder.wasCalled())
        .to.be.false 

        expect(requestData.meta.wasCalled)
        .to.be.false 

        const endExecutionWindow = requestData.schedule.windowStart + requestData.schedule.windowSize 
        await waitUntilBlock(0, endExecutionWindow - 1)
        /// Note: we go to one block before the endExecutionWindow
        /// because the next transaction will be mined in the next
        /// block, aka the exact block for `endExecutionWindow`

        const balBeforeExecute = await config.web3.eth.getBalance(accounts[3])

        const executeTx = await txRequest.execute(
            {
                from: accounts[3],
                gas: 3000000,
                gasPrice: gasPrice,
            }
        )
        expect(executeTx.receipt)
        .to.exist 

        const balAfterExecute = await config.web3.eth.getBalance(accounts[3])

        expect(parseInt(balAfterExecute))
        .to.be.at.least(parseInt(balBeforeExecute))

        const requestDataTwo = await parseRequestData(txRequest) 

        expect(await txRecorder.wasCalled())
        .to.be.true 

        expect(requestDataTwo.meta.wasCalled)
        .to.be.true
    })
})