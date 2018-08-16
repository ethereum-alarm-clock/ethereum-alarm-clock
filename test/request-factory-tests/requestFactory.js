require("chai")
  .use(require("chai-as-promised"))
  .should()

const { assert, expect } = require("chai")

// Contracts
const RequestFactory = artifacts.require("./RequestFactory.sol")
const RequestLib = artifacts.require("./RequestLib.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

// Brings in config.web3 (v1.0.0)
const ethUtil = require("ethereumjs-util")
const config = require("../../config")
const { parseRequestData, calculateBlockBucket } = require("../dataHelpers.js")

const NULL_ADDR = "0x0000000000000000000000000000000000000000"

// Note - these tests were checked very well and should never be wrong.
// If they start failing - look in the contracts.
contract("Request factory", async (accounts) => {
  let requestLib
  let transactionRequestCore
  let requestFactory

  const transactionRequest = {
    claimWindowSize: 255,
    fee: 12345,
    bounty: 54321,
    freezePeriod: 10,
    windowSize: 511,
    reservedWindowSize: 16,
    temporalUnit: 1,
    callValue: 123456789,
    callGas: 1000000,
    gasPrice: 1000000,
    requiredDeposit: 1000000,
    testCallData: "this-is-call-data",
    endowment: 10 ** 18
  }

  const getWindowStart = async () => (await config.web3.eth.getBlockNumber()) + 20

  const createValidationParams = async (properties = {}) => {
    const request = Object.assign(
      {},
      transactionRequest,
      { windowStart: await getWindowStart() },
      properties
    )

    return [
      request.fee,
      request.bounty,
      request.claimWindowSize,
      request.freezePeriod,
      request.reservedWindowSize,
      request.temporalUnit,
      request.windowSize,
      request.windowStart,
      request.callGas,
      request.callValue,
    ]
  }

  const validate = async ({
    endowment = transactionRequest.endowment,
    properties,
    to = accounts[2]
  } = {}) => {
    const paramsForValidation = await createValidationParams(properties)
    const isValid = await requestLib.validate(
      [accounts[0], accounts[0], accounts[1], to],
      paramsForValidation,
      endowment
    )

    return { paramsForValidation, isValid }
  }

  before(async () => {
    requestLib = await RequestLib.deployed()
    expect(requestLib.address).to.exist

    transactionRequestCore = await TransactionRequestCore.deployed()
    expect(transactionRequestCore.address).to.exist

    requestFactory = await RequestFactory.new(transactionRequestCore.address)
    expect(requestFactory.address).to.exist
  })

  it("should create a request with provided properties", async () => {
    const windowStart = await getWindowStart()
    const { paramsForValidation, isValid } = await validate({ properties: { windowStart } })

    isValid.forEach(bool => expect(bool).to.be.true)

    const params = paramsForValidation
    params.push(transactionRequest.gasPrice)
    params.push(transactionRequest.requiredDeposit)

    // Create a request with the same args we validated
    const createTx = await requestFactory.createRequest(
      [
        accounts[0],
        accounts[1], // fee recipient
        accounts[2], // to
      ],
      params,
      transactionRequest.testCallData
    )

    expect(createTx.receipt).to.exist

    const logRequestCreated = createTx.logs.find(e => e.event === "RequestCreated")

    expect(logRequestCreated.args.request).to.exist
    expect(logRequestCreated.args.params.length).to.equal(12)

    logRequestCreated.args.params.forEach((el, idx) => expect(el.toNumber()).to.equal(params[idx]))

    const bucket = calculateBlockBucket(windowStart)
    expect(logRequestCreated.args.bucket.toNumber()).to.equal(bucket.toNumber())

    // Now let's create a transactionRequest instance
    const txRequest = await TransactionRequestCore.at(logRequestCreated.args.request)
    const requestData = await parseRequestData(txRequest)

    expect(requestData.meta.owner).to.equal(accounts[0])

    expect(requestData.meta.createdBy).to.equal(accounts[0])

    expect(requestData.meta.isCancelled).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    expect(requestData.meta.wasSuccessful).to.be.false

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)

    expect(requestData.claimData.claimDeposit).to.equal(0)

    expect(requestData.claimData.paymentModifier).to.equal(0)

    expect(requestData.paymentData.fee).to.equal(transactionRequest.fee)

    expect(requestData.paymentData.feeRecipient).to.equal(accounts[1])

    expect(requestData.paymentData.feeOwed).to.equal(0)

    expect(requestData.paymentData.bounty).to.equal(transactionRequest.bounty)

    expect(requestData.paymentData.bountyBenefactor).to.equal(NULL_ADDR)

    expect(requestData.paymentData.bountyOwed).to.equal(0)

    expect(requestData.schedule.claimWindowSize).to.equal(transactionRequest.claimWindowSize)

    expect(requestData.schedule.freezePeriod).to.equal(transactionRequest.freezePeriod)

    expect(requestData.schedule.windowStart).to.equal(windowStart)

    expect(requestData.schedule.reservedWindowSize).to.equal(transactionRequest.reservedWindowSize)

    expect(requestData.schedule.temporalUnit).to.equal(1)

    expect(requestData.txData.toAddress).to.equal(accounts[2])

    const expectedCallData = ethUtil.bufferToHex(Buffer.from(transactionRequest.testCallData))
    const callData = await txRequest.callData()
    expect(callData).to.equal(expectedCallData)

    expect(requestData.txData.callValue).to.equal(transactionRequest.callValue)

    expect(requestData.txData.callGas).to.equal(transactionRequest.callGas)

    // Lastly, we just make sure that the transaction request
    // address is a known request for the factory.
    expect(await requestFactory.isKnownRequest(NULL_ADDR)).to.be.false // sanity check
    expect(await requestFactory.isKnownRequest(txRequest.address)).to.be.true
  })

  it("should test request factory insufficient endowment validation error", async () => {
    // Validate the data with the RequestLib
    const { isValid } = await validate({ endowment: 1 })

    expect(isValid[0]).to.be.false
    isValid.slice(1).forEach(bool => expect(bool).to.be.true)
  })

  it("should test request factory throws validation error on too large of a reserve window", async () => {
    const reservedWindowSize = transactionRequest.windowSize + 2
    const { isValid } = await validate({ properties: { reservedWindowSize } })

    expect(isValid[1]).to.be.false
    expect(isValid[0]).to.be.true
    isValid.slice(2).forEach(bool => expect(bool).to.be.true)
  })

  it("should test request factory throws invalid temporal unit validation error", async () => {
    const temporalUnit = 100
    const { isValid } = await validate({ properties: { temporalUnit } })

    expect(isValid[2]).to.be.false
    expect(isValid[3]).to.be.false
    isValid.slice(0, 2).forEach(bool => expect(bool).to.be.true)
    isValid.slice(4).forEach(bool => expect(bool).to.be.true)
  })

  it("should test request factory too soon execution window validation error", async () => {
    const windowStart = await getWindowStart()
    const freezePeriod = windowStart + 1
    const { isValid } = await validate({ properties: { windowStart, freezePeriod } })

    expect(isValid[3]).to.be.false
    isValid.slice(0, 3).forEach(bool => expect(bool).to.be.true)
    isValid.slice(4).forEach(bool => expect(bool).to.be.true)
  })

  it("should test request factory has too high call gas validation error", async () => {
    const callGas = 8.8e8 // cannot be over gas limit
    const { isValid } = await validate({ properties: { callGas } })

    expect(isValid[4]).to.be.false
    isValid.slice(0, 4).forEach(bool => expect(bool).to.be.true)
    isValid.slice(5).forEach(bool => expect(bool).to.be.true)
  })

  it("should test null to address validation error", async () => {
    const to = NULL_ADDR // cannot be over gas limit
    const { isValid } = await validate({ to })

    expect(isValid[5]).to.be.false
    isValid.slice(0, 5).forEach(bool => expect(bool).to.be.true)
  })

  it("should not allow to reinitialize the scheduled transaction", async () => {
    const { paramsForValidation } = await validate()

    const params = paramsForValidation
    params.push(transactionRequest.gasPrice)
    params.push(transactionRequest.requiredDeposit)

    // Create a request with the same args we validated
    const createTx = await requestFactory.createRequest(
      [
        accounts[0],
        accounts[1], // fee recipient
        accounts[2], // to
      ],
      params,
      transactionRequest.testCallData
    )

    const logRequestCreated = createTx.logs.find(e => e.event === "RequestCreated")
    const txRequest = await TransactionRequestCore.at(logRequestCreated.args.request)

    let requestData = await parseRequestData(txRequest)
    expect(requestData.txData.toAddress).to.equal(accounts[2])

    await txRequest.initialize(
      [
        accounts[0],
        accounts[0],
        accounts[1], // fee recipient
        accounts[3], // hijacking recipient
      ],
      params,
      transactionRequest.testCallData
    ).should.be.rejectedWith("VM Exception while processing transaction: revert")

    requestData = await parseRequestData(txRequest)
    expect(requestData.txData.toAddress).to.equal(accounts[2])
  })

  it("should not allow the deployment of new requests when paused", async () => {
    await requestFactory.pause();
    const isPaused = await requestFactory.paused();
    assert(isPaused, "RequestFactory should be paused now.");

    const windowStart = await getWindowStart()
    const { paramsForValidation, isValid } = await validate({ properties: { windowStart } })

    isValid.forEach(bool => expect(bool).to.be.true)

    const params = paramsForValidation
    params.push(transactionRequest.gasPrice)
    params.push(transactionRequest.requiredDeposit)

    // Create a request with the same args we validated
    let res;
    try {
      res = await requestFactory.createRequest(
        [
          accounts[0],
          accounts[1], // fee recipient
          accounts[2], // to
        ],
        params,
        transactionRequest.testCallData
      )
    } catch (e) {
      const wasReverted = e.toString().indexOf("VM Exception while processing transaction: revert");
      assert(wasReverted !== -1);
    }
    expect(res).to.be.undefined;
  })
})
