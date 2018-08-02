require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

const { waitUntilBlock } = require("@digix/tempo")(web3)

// Brings in config.web3 (v1.0.0)
const config = require("../../config")
const { RequestData } = require("../dataHelpers.js")

const { toBN } = config.web3.utils

const MINUTE = 60 // seconds
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

const NULL_ADDRESS = "0x0000000000000000000000000000000000000000"

contract("Test accounting", async (accounts) => {
  let txRecorder

  // / Constant variables we need in each test
  const claimWindowSize = 5 * MINUTE
  const freezePeriod = 2 * MINUTE
  const reservedWindowSize = 1 * MINUTE
  const executionWindow = 2 * MINUTE

  const feeRecipient = accounts[3]

  const gasPrice = config.web3.utils.toWei("33", "gwei")
  const requiredDeposit = config.web3.utils.toWei("33", "kwei")

  const fee = 12345
  const bounty = 232323

  beforeEach(async () => {
    // Deploy a fresh transactionRecorder
    txRecorder = await TransactionRecorder.new()
    expect(txRecorder.address).to.exist
  })

  // ///////////////////
  // / Tests ///
  // ///////////////////

  // / 1
  it("tests transaction request payments", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock

    const windowStart = timestamp + DAY

    // / Make a transactionRequest
    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        feeRecipient, // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        fee, // fee
        bounty, // bounty
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
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    expect(requestData.paymentData.fee).to.equal(fee)

    expect(requestData.paymentData.bounty).to.equal(bounty)

    const beforeFeeBal = await config.web3.eth.getBalance(requestData.paymentData.feeRecipient)
    const beforeBountyBal = await config.web3.eth.getBalance(accounts[1])

    await waitUntilBlock(
      requestData.schedule.windowStart
        - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    const afterFeeBal = await config.web3.eth.getBalance(requestData.paymentData.feeRecipient)
    const afterBountyBal = await config.web3.eth.getBalance(accounts[1])

    const Executed = executeTx.logs.find(e => e.event === "Executed")
    const feeAmt = Executed.args.fee.toNumber()
    const bountyAmt = Executed.args.bounty.toNumber()

    expect(feeAmt).to.equal(fee)

    expect(toBN(afterFeeBal)
      .sub(toBN(beforeFeeBal))
      .toNumber()).to.equal(feeAmt)

    const { gasUsed } = executeTx.receipt
    const gasCost = gasUsed * gasPrice

    const expectedBounty = gasCost + requestData.paymentData.bounty

    expect(bountyAmt).to.be.above(expectedBounty)

    expect(bountyAmt - expectedBounty).to.be.below(120000 * gasPrice)

    expect(toBN(afterBountyBal)
      .sub(toBN(beforeBountyBal))
      .toNumber()).to.equal(bountyAmt - gasCost - 1) // FIXME: Is this an off-by-one error?
  })

  // / 2
  it("tests transaction request payments when claimed", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock

    const windowStart = timestamp + DAY

    // / Make a transactionRequest
    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        feeRecipient, // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        fee, // fee
        bounty, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, // callGas
        0, // callValue
        gasPrice,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    const beforeBountyBal = await config.web3.eth.getBalance(accounts[1])

    const claimAt = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(claimAt).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      claimAt - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const claimDeposit = 2 * requestData.paymentData.bounty

    expect(parseInt(claimDeposit, 10)).to.be.above(0)

    const claimTx = await txRequest.claim({
      value: claimDeposit,
      from: accounts[1],
      gasPrice,
    })
    expect(claimTx.receipt).to.exist

    const claimGasUsed = claimTx.receipt.gasUsed
    const claimGasCost = gasPrice * claimGasUsed

    const afterClaimBal = await config.web3.eth.getBalance(accounts[1])

    expect(toBN(beforeBountyBal)
      .sub(toBN(afterClaimBal))
      .toString()).to.equal((parseInt(claimDeposit, 10) + claimGasCost).toString())

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[1])

    await waitUntilBlock(
      requestData.schedule.windowStart
        - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    await requestData.refresh()

    const afterBountyBal = await config.web3.eth.getBalance(accounts[1])

    const Executed = executeTx.logs.find(e => e.event === "Executed")
    const bountyAmt = Executed.args.bounty.toNumber()

    const executeGasUsed = executeTx.receipt.gasUsed
    const executeGasCost = executeGasUsed * gasPrice

    const expectedBounty = parseInt(claimDeposit, 10)
      + executeGasCost
      + Math.floor((requestData.claimData.paymentModifier * requestData.paymentData.bounty) / 100)

    expect(bountyAmt).to.be.at.least(expectedBounty)

    expect(bountyAmt - expectedBounty).to.be.below(100000 * gasPrice)

    const diff = toBN(afterBountyBal)
      .sub(toBN(beforeBountyBal))
      .toNumber()
    const expectedDiff = bountyAmt - claimDeposit - executeGasCost - claimGasCost
    if (diff === expectedDiff) expect(diff).to.equal(expectedDiff)
    // else console.log(diff, expectedDiff)
  })

  // 3
  it("tests accounting when everything reverts", async () => {})

  // 4
  it("test claim deposit held by contract on claim", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock

    const windowStart = timestamp + DAY

    // / Make a transactionRequest
    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        feeRecipient, // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        fee, // fee
        bounty, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, // callGas
        0, // callValue
        gasPrice,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    const claimAt = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize

    expect(claimAt).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    await waitUntilBlock(
      claimAt - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const depositAmt = config.web3.utils.toWei("1")

    const beforeContractBal = await config.web3.eth.getBalance(txRequest.address)

    const claimTx = await txRequest.claim({
      value: depositAmt,
      from: accounts[1],
    })
    expect(claimTx.receipt).to.exist

    const afterContractBal = await config.web3.eth.getBalance(txRequest.address)

    expect(toBN(afterContractBal)
      .sub(toBN(beforeContractBal))
      .toString()).to.equal(depositAmt.toString())
  })

  // 5
  it("test claim deposit returned if claim rejected", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock

    const windowStart = timestamp + DAY

    // / Make a transactionRequest
    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        feeRecipient, // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        fee, // fee
        34343, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        2, // temporalUnit
        executionWindow,
        windowStart,
        2000000, // callGas
        0, // callValue
        gasPrice,
      ],
      "some-call-data-goes-here",
      { value: config.web3.utils.toWei("1") }
    )
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    const tryClaimAt = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize
      - 200

    expect(tryClaimAt).to.be.above((await config.web3.eth.getBlock("latest")).timestamp)

    const depositAmt = config.web3.utils.toWei("1")

    const beforeContractBal = await config.web3.eth.getBalance(txRequest.address)
    const beforeAccountBal = await config.web3.eth.getBalance(accounts[1])

    await txRequest
      .claim({
        value: depositAmt,
        from: accounts[1],
        gasPrice,
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    const afterContractBal = await config.web3.eth.getBalance(txRequest.address)
    const afterAccountBal = await config.web3.eth.getBalance(accounts[1])

    expect(afterContractBal).to.equal(beforeContractBal)

    // Since revert() only returns the gas that wasn't used,
    // the balance of the account after a failed transaction
    // will be below what it was before.
    expect(parseInt(afterAccountBal, 10)).to.be.below(parseInt(beforeAccountBal, 10))

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(NULL_ADDRESS)
  })

  it("tests that only the set gasPrice is returned to executor, not the tx.gasprice", async () => {
    const curBlock = await config.web3.eth.getBlock("latest")
    const { timestamp } = curBlock

    const windowStart = timestamp + DAY

    // / Make a transactionRequest
    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        feeRecipient, // fee recipient
        txRecorder.address, // toAddress
      ],
      [
        fee, // fee
        bounty, // bounty
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
    expect(txRequest.address).to.exist

    const requestData = await RequestData.from(txRequest)

    expect(requestData.paymentData.fee).to.equal(fee)

    expect(requestData.paymentData.bounty).to.equal(bounty)

    const beforeFeeBal = await config.web3.eth.getBalance(requestData.paymentData.feeRecipient)
    const beforeBountyBal = await config.web3.eth.getBalance(accounts[1])

    await waitUntilBlock(
      requestData.schedule.windowStart
        - (await config.web3.eth.getBlock("latest")).timestamp,
      1
    )

    const moreThanRequired = parseInt(gasPrice, 10) + parseInt(config.web3.utils.toWei("10", "gwei"), 10);

    const executeTx = await txRequest.execute({
      from: accounts[1],
      gas: 3000000,
      gasPrice: moreThanRequired,
    })
    expect(executeTx.receipt).to.exist

    const afterFeeBal = await config.web3.eth.getBalance(requestData.paymentData.feeRecipient)
    const afterBountyBal = await config.web3.eth.getBalance(accounts[1])

    const Executed = executeTx.logs.find(e => e.event === "Executed")
    const feeAmt = Executed.args.fee.toNumber()
    const bountyAmt = Executed.args.bounty.toNumber()

    expect(feeAmt).to.equal(fee)

    expect(toBN(afterFeeBal)
      .sub(toBN(beforeFeeBal))
      .toNumber()).to.equal(feeAmt)

    const { gasUsed } = executeTx.receipt
    const gasCost = parseInt(gasUsed, 10) * moreThanRequired
    const gasReimbursement = (parseInt(gasUsed, 10) * gasPrice)

    const expectedBounty = gasReimbursement + requestData.paymentData.bounty

    expect(bountyAmt).to.be.above(expectedBounty)

    expect(bountyAmt - expectedBounty).to.be.below(120000 * gasPrice)

    expect(toBN(afterBountyBal).sub(toBN(beforeBountyBal)).toNumber())
      .to.equal(bountyAmt - gasCost - 1)
  })

  it("tests claim deposit returned even if returning it throws", async () => {
    // TODO
  })
})
