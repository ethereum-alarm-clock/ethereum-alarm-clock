require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

const { waitUntilBlock } = require("@digix/tempo")(web3)

// Bring in config.web3 (v1.0.0)
const config = require("../../config")
const {
  RequestData,
  parseRequestData,
  parseAbortData,
  wasAborted,
} = require("../dataHelpers.js")

const MINUTE = 60 // seconds
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

contract("Timestamp execution", async (accounts) => {
  let txRecorder
  let txRequest

  const gasPrice = config.web3.utils.toWei("37", "gwei")
  const requiredDeposit = config.web3.utils.toWei("60", "kwei")

  // / Constant variables we need in each test
  const claimWindowSize = 5 * MINUTE
  const freezePeriod = 2 * MINUTE
  const reservedWindowSize = 1 * MINUTE
  const executionWindow = 2 * MINUTE

  beforeEach(async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock
    const windowStart = timestamp + (DAY * 10)

    // / Deploy a fresh transactionRecorder
    txRecorder = await TransactionRecorder.new()
    expect(
      txRecorder.address,
      "transactionRecorder should be fresh for each test"
    ).to.exist

    // / Make a transactionRequest
    txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        accounts[1], // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        12345, // fee
        224455, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, // callGas
        0, // callValue
        gasPrice,
        requiredDeposit,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )

    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    const secondsToWait = firstClaimStamp
      - (await config.web3.eth.getBlock("latest")).timestamp

    await waitUntilBlock(
      secondsToWait,
      1
    )

    const claimTx = await txRequest.claim({
      from: accounts[1],
      value: config.web3.utils.toWei("1"),
    })

    expect(claimTx.receipt).to.exist
  })

  // ///////////
  // / Tests ///
  // ///////////

  // / 1
  it("should reject execution if its before the execution window", async () => {
    const requestData = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    expect((await config.web3.eth.getBlock("latest")).timestamp).to.be.below(requestData.schedule.windowStart)

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
    })

    const requestDataRefresh = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestDataRefresh.meta.wasCalled).to.be.false

    expect(wasAborted(executeTx)).to.be.true

    expect(parseAbortData(executeTx).find(reason => reason === "BeforeCallWindow")).to.exist
  })

  // / 2
  it("should reject execution if its after the execution window", async () => {
    const requestData = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    const endExecutionWindow = requestData.schedule.windowStart + requestData.schedule.windowSize
    const secsToWait = endExecutionWindow - (await config.web3.eth.getBlock("latest")).timestamp

    await waitUntilBlock(secsToWait + 1, 1)

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
    })

    const requestDataRefresh = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestDataRefresh.meta.wasCalled).to.be.false

    expect(wasAborted(executeTx)).to.be.true

    expect(parseAbortData(executeTx).find(reason => reason === "AfterCallWindow")).to.exist
  })

  // / 3
  it("should allow execution at the start of the execution window", async () => {
    const requestData = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    const startExecutionWindow = requestData.schedule.windowStart
    const secsToWait = startExecutionWindow
      - (await config.web3.eth.getBlock("latest")).timestamp
    // console.log(secsToWait)
    await waitUntilBlock(secsToWait, 1)

    const balBeforeExecute = await config.web3.eth.getBalance(accounts[1])

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    const balAfterExecute = await config.web3.eth.getBalance(accounts[1])

    expect(parseInt(balAfterExecute, 10)).to.be.at.least(parseInt(balBeforeExecute, 10))

    const requestDataRefresh = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.true

    expect(requestDataRefresh.meta.wasCalled).to.be.true
  })

  // / 4
  it("should allow execution at the end of the execution window", async () => {
    const requestData = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    const endExecutionWindow = requestData.schedule.windowStart + requestData.schedule.windowSize
    const secsToWait = endExecutionWindow - (await config.web3.eth.getBlock("latest")).timestamp
    await waitUntilBlock(secsToWait - 1, 1)

    const balBeforeExecute = await config.web3.eth.getBalance(accounts[5])

    const executeTx = await txRequest.execute({
      from: accounts[5],
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    const balAfterExecute = await config.web3.eth.getBalance(accounts[5])

    expect(parseInt(balAfterExecute, 10)).to.be.at.least(parseInt(balBeforeExecute, 10))

    const requestDataRefresh = await parseRequestData(txRequest)

    expect(await txRecorder.wasCalled()).to.be.true

    expect(requestDataRefresh.meta.wasCalled).to.be.true
  })
})
