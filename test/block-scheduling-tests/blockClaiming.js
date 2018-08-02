require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")

const { waitUntilBlock } = require("@digix/tempo")(web3)

// Brings in config.web3 (v1.0.0)
const config = require("../../config")
const { RequestData } = require("../dataHelpers.js")

const NULL_ADDR = "0x0000000000000000000000000000000000000000"

contract("Block claiming", async (accounts) => {
  const Owner = accounts[0]
  const Benefactor = accounts[1]

  const gasPrice = config.web3.utils.toWei("45", "gwei")

  let txRequest
  let txRecorder

  // Before each test we deploy a new instance of Transaction Request so we have a fresh instance
  beforeEach(async () => {
    const curBlock = await config.web3.eth.getBlockNumber()

    txRecorder = await TransactionRecorder.new()
    expect(txRecorder.address).to.exist

    const requiredDeposit = config.web3.utils.toWei("20", "kwei") // 1 kwei = 10e3 wei, ie this is 20000 wei

    // Instantiate a TransactionRequest with temporal unit 1 - aka block
    txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        Owner, // created by
        Owner, // owner
        Benefactor, // fee recipient
        txRecorder.address, // to
      ],
      [
        0, // fee
        config.web3.utils.toWei("200", "finney"), // bounty
        25, // claim window size
        5, // freeze period
        10, // reserved window size
        1, // temporal unit - blocks is 1
        10, // window size
        curBlock + 38, // windowStart
        100000, // callGas
        0, // callValue
        gasPrice,
        requiredDeposit,
      ],
      "this-is-the-call-data",
      { value: config.web3.utils.toWei("1") }
    )
  })

  // ///////////
  // / Tests ///
  // ///////////

  // 1
  it("should not claim before first claim block", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimBlock = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, firstClaimBlock - 2)

    await txRequest
      .claim({
        value: 2 * requestData.paymentData.bounty,
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)
  })

  // 2
  it("should allow claiming at the first claim block", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimBlock = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, firstClaimBlock)

    const claimTx = await txRequest.claim({
      from: accounts[0],
      value: 2 * requestData.paymentData.bounty,
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])
  })

  // 3
  it("should allow claiming at the last claim block", async () => {
    const requestData = await RequestData.from(txRequest)

    const lastClaimBlock = requestData.schedule.windowStart - requestData.schedule.freezePeriod

    expect(lastClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    // Because this function consumes a block we must give ourselves the buffer of two blocks.
    await waitUntilBlock(0, lastClaimBlock - 2)

    const claimTx = await txRequest.claim({
      from: accounts[0],
      value: 2 * requestData.paymentData.bounty,
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])
  })

  // 4
  it("cannot claim after the last block", async () => {
    const requestData = await RequestData.from(txRequest)

    const lastClaimBlock = requestData.schedule.windowStart - requestData.schedule.freezePeriod

    expect(lastClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, lastClaimBlock)

    await txRequest
      .claim({
        from: accounts[0],
        value: 2 * requestData.paymentData.bounty,
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)
  })

  it("should execute a claimed block request", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimBlock = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, firstClaimBlock)

    const claimTx = await txRequest.claim({
      from: accounts[1],
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[1])

    await waitUntilBlock(0, requestData.schedule.windowStart)

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.meta.wasCalled).to.be.true
  })

  it("should execute a claimed call after block reserve window", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimBlock = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, firstClaimBlock)

    const claimTx = await txRequest.claim({
      value: config.web3.utils.toWei("2"),
      from: accounts[2],
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[2])

    await waitUntilBlock(
      0,
      requestData.schedule.windowStart + requestData.schedule.reservedWindowSize
    )

    const executeTx = await txRequest.execute({
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    await requestData.refresh()
    // console.log(requestData)
    // expect(requestData.meta.wasCalled)
    // .to.be.true
  })

  // 7
  it("should determine bounty amount with modifier", async () => {
    const requestData = await RequestData.from(txRequest)

    const claimAt = (requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize)
      + Math.floor((requestData.schedule.claimWindowSize * 2) / 3)

    const expectedPaymentModifier = Math.floor((100 * 2) / 3)

    expect(requestData.claimData.paymentModifier).to.equal(0)

    expect(claimAt).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, claimAt)

    const claimTx = await txRequest.claim({
      value: config.web3.utils.toWei("2"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.paymentModifier - 2).to.equal(expectedPaymentModifier)
  })

  // 8
  it("CANNOT claim if already claimed", async () => {
    const requestData = await RequestData.from(txRequest)

    const claimAt = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(claimAt).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, claimAt)

    const claimTx = await txRequest.claim({
      value: config.web3.utils.toWei("1"),
    })
    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])

    // Now try to claim from a different account

    await txRequest
      .claim({
        from: accounts[6],
        value: config.web3.utils.toWei("1"),
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    // Just check this again to be sure

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[0])
  })

  // 9
  it("CANNOT claim with insufficient claim deposit", async () => {
    const requestData = await RequestData.from(txRequest)

    const firstClaimBlock = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(firstClaimBlock).to.be.above(await config.web3.eth.getBlockNumber())

    await waitUntilBlock(0, firstClaimBlock)

    await txRequest
      .claim({
        from: accounts[0],
        // Since the requiredDeposit is 20 kwei, we will send the value of 15 kwei in
        // order to fail this test
        value: config.web3.utils.toWei("15", "kwei"),
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDR)
  })
})
