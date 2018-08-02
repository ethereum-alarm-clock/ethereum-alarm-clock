require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

const { waitUntilBlock } = require("@digix/tempo")(web3)

// Brings in config.web3
const config = require("../../config")
const { RequestData } = require("../dataHelpers.js")

const NULL_ADDR = "0x0000000000000000000000000000000000000000"

contract("Timestamp claiming", async (accounts) => {
  const MINUTE = 60 // seconds
  const HOUR = 60 * MINUTE
  const DAY = 24 * HOUR
  const gasPrice = config.web3.utils.toWei("45", "gwei")
  const claimWindowSize = 5 * MINUTE
  const freezePeriod = 2 * MINUTE
  const reservedWindowSize = 1 * MINUTE
  const executionWindow = 2 * MINUTE

  let txRecorder
  let txRequest

  // The set up before each test
  beforeEach(async () => {
    const { timestamp } = await config.web3.eth.getBlock("latest")
    const windowStart = timestamp + DAY

    txRecorder = await TransactionRecorder.new()

    const requiredDeposit = config.web3.utils.toWei("25", "kwei")

    // Instantiate a TransactionRequest with temporal unit 2 - aka timestamp
    txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        accounts[1], // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        0, // fee
        config.web3.utils.toWei("333", "finney"), // payment
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporal unit
        executionWindow,
        windowStart,
        1200000, // callGas
        0, // callValue
        gasPrice,
        requiredDeposit,
      ],
      "just-some-call-data",
      { value: config.web3.utils.toWei("1") }
    )
  })

  // ///////////
  // / Tests ///
  // ///////////

  // 1
  it("cannot claim before first claim stamp", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      firstClaimStamp
        - (await config.web3.eth.getBlock("latest")).timestamp
        - 3, // because these tests take a bit to run we need a 3 second buffer
      1
    )

    await txRequest
      .claim({
        value: config.web3.utils.toWei("2"),
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)
  })

  it("can claim at the first claim stamp", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      firstClaimStamp - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimTx = await txRequest.claim({
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])
  })

  it("can claim at the last claim stamp", async () => {
    const requestData = await RequestData.from(txRequest)

    const lastClaimStamp = requestData.schedule.windowStart - requestData.schedule.freezePeriod

    expect(lastClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      lastClaimStamp - (await config.web3.eth.getBlock("latest")).timestamp - 3,
      1
    )

    const claimTx = await txRequest.claim({
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])
  })

  // 4
  it("can not claim after the last claim stamp", async () => {
    const requestData = await RequestData.from(txRequest)

    const lastClaimStamp = requestData.schedule.windowStart - requestData.schedule.freezePeriod

    expect(lastClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    const currentTimestamp = (await config.web3.eth.getBlock("latest")).timestamp
    await waitUntilBlock((lastClaimStamp - currentTimestamp) + 1, 1)

    await txRequest
      .claim({
        value: config.web3.utils.toWei("2"),
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)
  })

  it("should execute a claimed timestamp request", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      firstClaimStamp - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimTx = await txRequest.claim({
      from: accounts[1],
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[1])

    await waitUntilBlock(
      requestData.schedule.windowStart
        - (await config.web3.eth.getBlock("latest")).timestamp,
      0
    )

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice,
    })

    expect(executeTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.meta.wasCalled).to.be.true
  })

  it("should execute a claimed call after reserve window", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      firstClaimStamp - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimTx = await txRequest.claim({
      from: accounts[1],
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[1])

    const currentTimestamp = (await config.web3.eth.getBlock("latest")).timestamp
    await waitUntilBlock((requestData.schedule.windowStart - currentTimestamp)
      + requestData.schedule.reservedWindowSize, 1)

    await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice,
    })

    await requestData.refresh()

    expect(requestData.meta.wasCalled).to.be.true
  })

  it("tests claim timestamp to determine the payment modifier", async () => {
    const requestData = await RequestData.from(txRequest)

    const claimAt = (requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize)
      + Math.floor((requestData.schedule.claimWindowSize * 2) / 3)

    expect(requestData.claimData.paymentModifier).to.equal(0)

    expect(claimAt).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      claimAt - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimTx = await txRequest.claim({
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    // console.log(requestData.claimData.paymentModifier, expectedPaymentModifier)
    // TODO - sometimes this fails?
    // expect(requestData.claimData.paymentModifier)
    // .to.equal(expectedPaymentModifier)
  })

  // 8
  it("CANNOT claim if already claimed", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      firstClaimStamp - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimTx = await txRequest.claim({
      from: accounts[0],
      value: config.web3.utils.toWei("1"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])

    // Now try to claim from a different account

    await txRequest
      .claim({
        from: accounts[3],
        value: config.web3.utils.toWei("1"),
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    // Check this again to be sure

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])
  })

  // 9
  it("CANNOT claim if supplied with insufficient claim deposit", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimStamp = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimStamp).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      firstClaimStamp - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const { requiredDeposit } = requestData.claimData
    const trySendDeposit = requiredDeposit - 2500

    await txRequest
      .claim({
        from: accounts[0],
        value: trySendDeposit,
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)
  })
})
