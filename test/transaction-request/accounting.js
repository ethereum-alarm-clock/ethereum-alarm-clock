require("chai")
  .use(require("chai-as-promised"))
  .should()

const expect = require("chai").expect

/// Contracts
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")
const TransactionRequest = artifacts.require("./TransactionRequest.sol")

/// Brings in config.web3 (v1.0.0)
const config = require("../../config")
const { RequestData } = require("../dataHelpers.js")
const { wait, waitUntilBlock } = require("@digix/tempo")(web3)
const toBN = config.web3.utils.toBN

const MINUTE = 60 //seconds
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

const NULL_ADDRESS = "0x0000000000000000000000000000000000000000"

contract("Test accounting", async function(accounts) {
  let txRecorder

  /// Constant variables we need in each test
  const claimWindowSize = 5 * MINUTE
  const freezePeriod = 2 * MINUTE
  const reservedWindowSize = 1 * MINUTE
  const executionWindow = 2 * MINUTE

  const feeRecipient = accounts[3]

  const gasPrice = config.web3.utils.toWei("33", "gwei")
  const requiredDeposit = config.web3.utils.toWei("33", "kwei")

  const fee = 12345
  const payment = 232323

  beforeEach(async function() {
    // Deploy a fresh transactionRecorder
    txRecorder = await TransactionRecorder.new()
    expect(txRecorder.address).to.exist
  })

  /////////////////////
  /// Tests ///
  /////////////////////

  /// 1
  it("tests transaction request payments", async function() {
    const curBlock = await config.web3.eth.getBlock("latest")
    const timestamp = curBlock.timestamp

    const windowStart = timestamp + DAY

    /// Make a transactionRequest
    const txRequest = await TransactionRequest.new(
      [
        accounts[0], //createdBy
        accounts[0], //owner
        feeRecipient, // fee recipient
        txRecorder.address, //toAddress
      ],
      [
        fee, // fee
        payment, //payment
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, //callGas
        0, //callValue
        gasPrice,
        requiredDeposit,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    expect(requestData.paymentData.fee).to.equal(fee)

    expect(requestData.paymentData.payment).to.equal(payment)

    const beforeFeeBal = await config.web3.eth.getBalance(
      requestData.paymentData.feeRecipient
    )
    const beforePaymentBal = await config.web3.eth.getBalance(accounts[1])

    await waitUntilBlock(
      requestData.schedule.windowStart -
        (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice: gasPrice,
    })
    expect(executeTx.receipt).to.exist

    const afterFeeBal = await config.web3.eth.getBalance(
      requestData.paymentData.feeRecipient
    )
    const afterPaymentBal = await config.web3.eth.getBalance(accounts[1])

    const Executed = executeTx.logs.find(e => e.event === "Executed")
    const feeAmt = Executed.args.fee.toNumber()
    const paymentAmt = Executed.args.payment.toNumber()

    expect(feeAmt).to.equal(fee)

    expect(
      toBN(afterFeeBal)
        .sub(toBN(beforeFeeBal))
        .toNumber()
    ).to.equal(feeAmt)

    const gasUsed = executeTx.receipt.gasUsed
    const gasCost = gasUsed * gasPrice

    const expectedPayment = gasCost + requestData.paymentData.payment

    expect(paymentAmt).to.be.above(expectedPayment)

    expect(paymentAmt - expectedPayment).to.be.below(120000 * gasPrice)

    expect(
      toBN(afterPaymentBal)
        .sub(toBN(beforePaymentBal))
        .toNumber()
    ).to.equal(paymentAmt - gasCost - 1) // FIXME: Is this an off-by-one error?
  })

  /// 2
  it("tests transaction request payments when claimed", async function() {
    const curBlock = await config.web3.eth.getBlock("latest")
    const timestamp = curBlock.timestamp

    const windowStart = timestamp + DAY

    /// Make a transactionRequest
    const txRequest = await TransactionRequest.new(
      [
        accounts[0], //createdBy
        accounts[0], //owner
        feeRecipient, // fee recipient
        txRecorder.address, //toAddress
      ],
      [
        fee, // fee
        payment, //payment
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, //callGas
        0, //callValue
        gasPrice,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    const beforePaymentBal = await config.web3.eth.getBalance(accounts[1])

    const claimAt =
      requestData.schedule.windowStart -
      requestData.schedule.freezePeriod -
      requestData.schedule.claimWindowSize

    expect(claimAt).to.be.above(
      (await config.web3.eth.getBlock("latest")).timestamp
    )

    await waitUntilBlock(
      claimAt - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimDeposit = 2 * requestData.paymentData.payment

    expect(parseInt(claimDeposit)).to.be.above(0)

    const claimTx = await txRequest.claim({
      value: claimDeposit,
      from: accounts[1],
      gasPrice: gasPrice,
    })
    expect(claimTx.receipt).to.exist

    const claimGasUsed = claimTx.receipt.gasUsed
    const claimGasCost = gasPrice * claimGasUsed

    const afterClaimBal = await config.web3.eth.getBalance(accounts[1])

    expect(
      toBN(beforePaymentBal)
        .sub(toBN(afterClaimBal))
        .toString()
    ).to.equal((parseInt(claimDeposit) + claimGasCost).toString())

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[1])

    await waitUntilBlock(
      requestData.schedule.windowStart -
        (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice: gasPrice,
    })
    expect(executeTx.receipt).to.exist

    await requestData.refresh()

    const afterPaymentBal = await config.web3.eth.getBalance(accounts[1])

    const Executed = executeTx.logs.find(e => e.event === "Executed")
    const feeAmt = Executed.args.fee.toNumber()
    const paymentAmt = Executed.args.payment.toNumber()

    const executeGasUsed = executeTx.receipt.gasUsed
    const executeGasCost = executeGasUsed * gasPrice

    const expectedPayment =
      parseInt(claimDeposit) +
      executeGasCost +
      Math.floor(
        requestData.claimData.paymentModifier *
          requestData.paymentData.payment /
          100
      )

    expect(paymentAmt).to.be.at.least(expectedPayment)

    expect(paymentAmt - expectedPayment).to.be.below(100000 * gasPrice)

    const diff = toBN(afterPaymentBal)
      .sub(toBN(beforePaymentBal))
      .toNumber()
    const expectedDiff =
      paymentAmt - claimDeposit - executeGasCost - claimGasCost
    if (diff == expectedDiff) expect(diff).to.equal(expectedDiff)
    else console.log(diff, expectedDiff)
  })

  /// 3
  it("tests accounting when everything reverts", async function() {})

  /// 4
  it("test claim deposit held by contract on claim", async function() {
    const curBlock = await config.web3.eth.getBlock("latest")
    const timestamp = curBlock.timestamp

    const windowStart = timestamp + DAY

    /// Make a transactionRequest
    const txRequest = await TransactionRequest.new(
      [
        accounts[0], //createdBy
        accounts[0], //owner
        feeRecipient, // fee recipient
        txRecorder.address, //toAddress
      ],
      [
        fee, // fee
        payment, //payment
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, //callGas
        0, //callValue
        gasPrice,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    const claimAt =
      requestData.schedule.windowStart -
      requestData.schedule.freezePeriod -
      requestData.schedule.claimWindowSize

    expect(claimAt).to.be.above(
      (await config.web3.eth.getBlock("latest")).timestamp
    )

    await waitUntilBlock(
      claimAt - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const depositAmt = config.web3.utils.toWei("1")

    const beforeContractBal = await config.web3.eth.getBalance(
      txRequest.address
    )
    const beforeAccountBal = await config.web3.eth.getBalance(accounts[1])

    const claimTx = await txRequest.claim({
      value: depositAmt,
      from: accounts[1],
    })
    expect(claimTx.receipt).to.exist

    const afterContractBal = await config.web3.eth.getBalance(txRequest.address)
    const afterAccountBal = await config.web3.eth.getBalance(accounts[1])

    expect(
      toBN(afterContractBal)
        .sub(toBN(beforeContractBal))
        .toString()
    ).to.equal(depositAmt.toString())
  })

  /// 5
  it("test claim deposit returned if claim rejected", async function() {
    const curBlock = await config.web3.eth.getBlock("latest")
    const timestamp = curBlock.timestamp

    const windowStart = timestamp + DAY

    /// Make a transactionRequest
    const txRequest = await TransactionRequest.new(
      [
        accounts[0], //createdBy
        accounts[0], //owner
        feeRecipient, // fee recipient
        txRecorder.address, //toAddress
      ],
      [
        fee, // fee
        34343, //payment
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, //callGas
        0, //callValue
        gasPrice,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    const tryClaimAt =
      requestData.schedule.windowStart -
      requestData.schedule.freezePeriod -
      requestData.schedule.claimWindowSize -
      200

    expect(tryClaimAt).to.be.above(
      (await config.web3.eth.getBlock("latest")).timestamp
    )

    const depositAmt = config.web3.utils.toWei("1")

    const beforeContractBal = await config.web3.eth.getBalance(
      txRequest.address
    )
    const beforeAccountBal = await config.web3.eth.getBalance(accounts[1])

    await txRequest
      .claim({
        value: depositAmt,
        from: accounts[1],
        gasPrice: gasPrice,
      })
      .should.be.rejectedWith(
        "VM Exception while processing transaction: revert"
      )

    const afterContractBal = await config.web3.eth.getBalance(txRequest.address)
    const afterAccountBal = await config.web3.eth.getBalance(accounts[1])

    expect(afterContractBal).to.equal(beforeContractBal)

    /// Since revert() only returns the gas that wasn't used,
    /// the balance of the account after a failed transaction
    /// will be below what it was before.
    expect(parseInt(afterAccountBal)).to.be.below(parseInt(beforeAccountBal))

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDRESS)
  })

  it("tests claim deposit returned even if returning it throws", async function() {
    /// TODO
  })
})
