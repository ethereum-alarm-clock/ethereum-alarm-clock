require("chai")
  .use(require("chai-as-promised"))
  .should()

const expect = require("chai").expect

/// Contracts
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")
const TransactionRequest = artifacts.require("./TransactionRequest.sol")

/// Bring in config.web3 (v1.0.0)
const config = require("../../config")
const { RequestData, parseAbortData, wasAborted } = require("../dataHelpers.js")
const { wait, waitUntilBlock } = require("@digix/tempo")(web3)
const toBN = config.web3.utils.toBN

contract("Execution", async function(accounts) {
  const gasPrice = config.web3.utils.toWei("66", "gwei")
  const requiredDeposit = config.web3.utils.toWei("66", "kwei")

  let txRequest
  let txRecorder

  beforeEach(async () => {
    txRecorder = await TransactionRecorder.new()
    expect(txRecorder.address).to.exist

    /// TransactionRequest constants
    const claimWindowSize = 25 //blocks
    const freezePeriod = 5 //blocks
    const reservedWindowSize = 10 //blocks
    const executionWindow = 10 //blocks

    const curBlockNum = await config.web3.eth.getBlockNumber()
    const windowStart = curBlockNum + 38

    txRequest = await TransactionRequest.new(
      [
        accounts[0], //createdBy
        accounts[0], //owner
        accounts[1], // fee recipient
        txRecorder.address, //toAddress
      ],
      [
        0, // fee
        0, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        1, //temporalUnit = 1, aka blocks
        executionWindow,
        windowStart,
        2000000, //callGas
        0, //callValue
        gasPrice,
        requiredDeposit,
      ],
      "some-call-data-could-be-anything",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist
  })

  it("tests execution transaction sent as specified", async function() {
    const requestData = await RequestData.from(txRequest)

    await waitUntilBlock(0, requestData.schedule.windowStart)

    const executeTx = await txRequest.execute({
      gas: 3000000,
      gasPrice: gasPrice,
    })
    expect(executeTx.receipt).to.exist

    assert((await txRecorder.wasCalled()) === true)
    assert((await txRecorder.lastCaller()) === txRequest.address)
    assert((await txRecorder.lastCallValue()).toNumber() === 0)
    expect(await txRecorder.lastCallData()).to.exist
    assert(Math.abs((await txRecorder.lastCallGas()) - 2000000) < 10000)
  })

  /// 2
  it("cannot execute if transaction gasPrice != txnData.gasPrice", async () => {
    const requestData = await RequestData.from(txRequest)

    expect(requestData.schedule.windowStart).to.be.above(
      await config.web3.eth.getBlockNumber()
    )

    await waitUntilBlock(0, requestData.schedule.windowStart)

    /// FAILS BECAUSE MISMATCH GASPRICE
    const failedExecuteTx = await txRequest.execute({
      from: accounts[5],
      gas: 3000000,
      gasPrice: config.web3.utils.toWei("88", "gwei"),
    })

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    expect(wasAborted(failedExecuteTx)).to.be.true

    expect(
      parseAbortData(failedExecuteTx).find(
        reason => reason === "MismatchGasPrice"
      )
    ).to.exist
  })

  /// 3
  it("CANNOT execute if available gas is less than txnData.callGas + GAS_OVERHEAD", async () => {
    const requestData = await RequestData.from(txRequest)

    expect(requestData.schedule.windowStart).to.be.above(
      await config.web3.eth.getBlockNumber()
    )

    await waitUntilBlock(0, requestData.schedule.windowStart)

    /// The min required gas is txnData.callGas + GAS_OVERHEAD (180000)
    const gas = requestData.txData.callGas + 180000 - 5000
    // console.log(gas)
    // console.log(gas + 5000)
    /// TODO: Investigate this further ^^^^

    /// FAILS BECAUSE NOT SUPPLIED ENOUGH GAS
    const failedExecuteTx = await txRequest.execute({
      from: accounts[5],
      gas: gas,
      gasPrice: gasPrice,
    })

    expect(await txRecorder.wasCalled()).to.be.false

    expect(requestData.meta.wasCalled).to.be.false

    expect(wasAborted(failedExecuteTx)).to.be.true

    expect(
      parseAbortData(failedExecuteTx).find(
        reason => reason === "InsufficientGas"
      )
    ).to.exist
  })
})
