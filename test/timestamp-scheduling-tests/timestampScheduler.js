require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const RequestFactory = artifacts.require("./RequestFactory.sol")
const TimestampScheduler = artifacts.require("./TimestampScheduler.sol")
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

const ethUtil = require("ethereumjs-util")

// Brings in config.web3 (v1.0.0)
const config = require("../../config")
const { RequestData, computeEndowment } = require("../dataHelpers.js")

contract("Timestamp scheduling", (accounts) => {
  const MINUTE = 60 // seconds

  const gasPrice = 20000
  const requiredDeposit = config.web3.utils.toWei("34", "kwei")
  const testData32 = ethUtil.bufferToHex(Buffer.from("32".padEnd(32, "AF01")))

  let requestFactory
  let timestampScheduler
  let transactionRecorder

  // / Deploy a fresh instance of contracts for each test.
  beforeEach(async () => {
    const transactionRequestCore = await TransactionRequestCore.deployed()
    expect(transactionRequestCore.address).to.exist

    // Request factory
    requestFactory = await RequestFactory.new(transactionRequestCore.address)
    expect(requestFactory.address).to.exist

    // Timestamp scheduler
    timestampScheduler = await TimestampScheduler.new(
      requestFactory.address,
      "0xecc9c5fff8937578141592e7E62C2D2E364311b8"
    )
    expect(timestampScheduler.address).to.exist

    // Transaction recorder
    transactionRecorder = await TransactionRecorder.new()
    expect(transactionRecorder.address).to.exist
  })

  it("should do timestamp scheduling using `schedule", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock
    const windowStart = timestamp + (10 * MINUTE)
    const fee = 98765
    const bounty = 80008

    const scheduleTx = await timestampScheduler.schedule(
      transactionRecorder.address,
      testData32, // callData
      [
        1212121, // callGas
        123454321, // callValue
        55 * MINUTE, // windowSize
        windowStart,
        gasPrice,
        fee,
        bounty,
        requiredDeposit,
      ],
      { from: accounts[0], value: config.web3.utils.toWei("10") }
    )

    expect(scheduleTx.receipt).to.exist

    expect(scheduleTx.receipt.gasUsed).to.be.below(3000000)

    // Dig the logs out for proof
    const logNewRequest = scheduleTx.logs.find(e => e.event === "NewRequest")

    expect(logNewRequest.args.request).to.exist

    const txRequest = await TransactionRequestCore.at(logNewRequest.args.request)
    const requestData = await RequestData.from(txRequest)

    // Test that the endowment was sent to txRequest
    // const balOfTxRequest = await config.web3.eth.getBalance(txRequest.address)
    // expect(parseInt(balOfTxRequest))
    // .to.equal(requestData.calcEndowment())

    // Sanity check
    const expectedEndowment = computeEndowment(bounty, fee, 1212121, 123454321, gasPrice)
    expect(requestData.calcEndowment()).to.equal(expectedEndowment)

    expect(requestData.txData.toAddress).to.equal(transactionRecorder.address)

    expect(await txRequest.callData()).to.equal(testData32)

    expect(requestData.schedule.windowSize).to.equal(55 * MINUTE)

    expect(requestData.txData.callGas).to.equal(1212121)

    expect(requestData.paymentData.fee).to.equal(fee)

    expect(requestData.paymentData.bounty).to.equal(bounty)

    expect(requestData.schedule.windowStart).to.equal(windowStart)

    expect(requestData.txData.gasPrice).to.equal(gasPrice)

    expect(requestData.claimData.requiredDeposit).to.equal(parseInt(requiredDeposit, 10))
  })

  it("should revert an invalid transaction", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock

    const windowStart = timestamp + (10 * MINUTE)

    await timestampScheduler
      .schedule(
        accounts[4],
        testData32, // callData
        [
          4e20, // callGas is too high
          123123, // callValue
          55 * MINUTE, // windowSize
          windowStart,
          gasPrice,
          0, // fee
          0, // bounty
          12, // requiredDeposit
        ],
        { from: accounts[0] }
      )
      .should.be.rejectedWith("VM Exception while processing transaction: revert")
  })
})
