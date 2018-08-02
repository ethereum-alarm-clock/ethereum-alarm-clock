require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

const { waitUntilBlock } = require("@digix/tempo")(web3)

// Bring in config.web3 (v1.0.0)
const config = require("../../config")
const {
  RequestData,
  parseRequestData,
} = require("../dataHelpers.js")

contract("Cancelling", async (accounts) => {
  const Owner = accounts[0]

  const gasPrice = config.web3.utils.toWei("66", "gwei")
  const requiredDeposit = config.web3.utils.toWei("66", "kwei")

  let txRequest

  // / TransactionRequest constants
  const claimWindowSize = 25 // blocks
  const freezePeriod = 5 // blocks
  const reservedWindowSize = 10 // blocks
  const executionWindow = 10 // blocks
  let windowStart

  beforeEach(async () => {
    const curBlockNum = await config.web3.eth.getBlockNumber()
    windowStart = curBlockNum + 38 + 10 + 5

    txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        Owner, // createdBy
        Owner, // owner
        accounts[1], // fee recipient
        accounts[3], // toAddress
      ],
      [
        0, // fee
        1, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        1, // temporalUnit = 1, aka blocks
        executionWindow,
        windowStart,
        43324, // callGas
        12345, // callValue
        gasPrice,
        requiredDeposit,
      ],
      "some-call-data-could-be-anything",
      { value: config.web3.utils.toWei("1") }
    )
  })

  // ///////////
  // / Tests ///
  // ///////////

  // 1
  it("tests CAN cancel before the claim window", async () => {
    const requestData = await RequestData.from(txRequest)

    const cancelAt = requestData.schedule.windowStart - requestData.schedule.freezePeriod - 3

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, cancelAt)

    const cancelTx = await txRequest.cancel({ from: Owner })
    expect(cancelTx.receipt).to.exist

    const requestDataRefresh = await parseRequestData(txRequest)

    expect(requestDataRefresh.meta.isCancelled).to.be.true
  })

  // 2
  it("tests non-owner CANNOT cancel before the claim window", async () => {
    const requestData = await RequestData.from(txRequest)

    const cancelAt = requestData.schedule.windowStart
      - requestData.schedule.freezePeriod
      - requestData.schedule.claimWindowSize
      - 3

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, cancelAt)

    await txRequest
      .cancel({ from: accounts[4] })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.false

    // For completion sakes, let's test if the `Owner` can cancel.
    const cancelTx = await txRequest.cancel({
      Owner,
    })
    expect(cancelTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.true
  })

  // 3
  it("tests CAN cancel during claim window when unclaimed", async () => {
    const requestData = await RequestData.from(txRequest)

    const cancelAt = requestData.schedule.windowStart - requestData.schedule.freezePeriod - 20

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    await waitUntilBlock(0, cancelAt)

    const cancelTx = await txRequest.cancel({ from: Owner })
    expect(cancelTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.true
  })

  // 4
  it("tests CANNOT be cancelled if claimed and before the freeze window", async () => {
    const requestData = await RequestData.from(txRequest)

    const cancelAt = requestData.schedule.windowStart - requestData.schedule.freezePeriod - 20
    const claimAt = cancelAt - 5

    await waitUntilBlock(0, claimAt)

    const claimTx = await txRequest.claim({
      from: accounts[1],
      value: config.web3.utils.toWei((2 * requestData.paymentData.bounty).toString()),
    })

    expect(claimTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.claimData.claimedBy).to.equal(accounts[1])

    await waitUntilBlock(0, cancelAt)

    await txRequest
      .cancel()
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.false
  })

  // 5
  it("tests CANNOT cancel during the freeze window", async () => {
    const requestData = await RequestData.from(txRequest)

    const cancelAt = requestData.schedule.windowStart - requestData.schedule.freezePeriod

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, cancelAt)

    await txRequest
      .cancel()
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.false
  })

  // 6
  it("tests CANNOT cancel during the execution window", async () => {
    const requestData = await parseRequestData(txRequest)

    const cancelAt = requestData.schedule.windowStart

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, cancelAt)

    await txRequest
      .cancel()
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    expect((await parseRequestData(txRequest)).meta.isCancelled).to.be.false
  })

  // 7
  it("tests CANNOT cancel if was called", async () => {
    const requestData = await RequestData.from(txRequest)

    const executeAt = requestData.schedule.windowStart
    const cancelFirst = requestData.schedule.windowStart + 10
    const cancelSecond = requestData.schedule.windowStart + requestData.schedule.windowSize + 5

    expect(executeAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, executeAt)

    const executeTx = await txRequest.execute({
      gas: 3000000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.meta.wasCalled).to.be.true

    expect(requestData.meta.isCancelled).to.be.false

    // Tries (and fails) to cancel after execution during execution window
    await waitUntilBlock(0, cancelFirst)

    await txRequest
      .cancel()
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.false

    // Tries (and fails) to cancel after execution and after execution window
    await waitUntilBlock(0, cancelSecond)

    await txRequest
      .cancel()
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.false
  })

  // 8
  it("tests CANNOT cancel if already cancelled", async () => {
    const requestData = await RequestData.from(txRequest)

    const cancelFirst = requestData.schedule.windowStart - requestData.schedule.freezePeriod - 20
    const cancelSecond = requestData.schedule.windowStart - requestData.schedule.freezePeriod - 10

    expect(cancelFirst).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    await waitUntilBlock(0, cancelFirst)

    const cancelTx = await txRequest.cancel({
      from: Owner,
    })
    expect(cancelTx.receipt).to.exist

    await requestData.refresh()

    expect(requestData.meta.isCancelled).to.be.true

    // Now try to cancel again 9 blocks in the future

    await waitUntilBlock(0, cancelSecond)

    await txRequest
      .cancel({
        from: Owner,
      })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")
  })

  it("tests cancellable if call is missed", async () => {
    const requestData = await parseRequestData(txRequest)

    const cancelAt = requestData.schedule.windowStart + requestData.schedule.windowSize + 10

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, cancelAt)

    const cancelTx = await txRequest.cancel()
    expect(cancelTx.receipt).to.exist

    expect((await parseRequestData(txRequest)).meta.isCancelled).to.be.true
  })

  it("tests accounting for pre-execution cancellation", async () => {
    const requestData = await parseRequestData(txRequest)

    const cancelAt = requestData.schedule.windowStart - requestData.schedule.freezePeriod - 3

    expect(cancelAt).to.be.above(await config.web3.eth.getBlockNumber())

    expect(requestData.meta.owner).to.equal(Owner)

    expect(requestData.meta.isCancelled).to.be.false

    await waitUntilBlock(0, cancelAt)

    // const balanceBeforeCancel = await config.web3.eth.getBalance(accounts[1])
    // const contractBalanceBefore = await config.web3.eth.getBalance(txRequest.address)

    const cancelTx = await txRequest.cancel({
      from: Owner, // TODO: this throws if set to another account
    })
    expect(cancelTx.receipt).to.exist

    // const balanceAfterCancel = await config.web3.eth.getBalance(accounts[1])
    // const contractBalanceAfter = await config.web3.eth.getBalance(txRequest.address)

    expect((await parseRequestData(txRequest)).meta.isCancelled).to.be.true

    // TODO: Get cancel data

    // console.log(balanceBeforeCancel)
    // console.log(balanceAfterCancel)
    // console.log(contractBalanceBefore)
    // console.log(contractBalanceAfter)
  })

  // /// TODO
  // it('tests accounting for missed execution cancellation by owner', async function() {
  //     const cancelAt = windowStart + executionWindow + 1

  //     /// Sanity checks
  //     assert(cancelAt > await config.web3.eth.getBlockNumber())

  //     const requestData = await transactionRequest.requestData()
  //     const logs = requestData.logs.find(e => e.event === 'RequestData')
  //     // requestData.meta.isCancelled === false
  //     assert(logs.args.bools[0] === false)
  //     // requestData.meta.owner === Owner
  //     assert(logs.args.addressArgs[2] === Owner)

  //     /// Get the balances before the cancellation calls
  //     const beforeCancelBal = await config.web3.eth.getBalance(Owner)
  //     const beforeContractBal = await config.web3.eth.getBalance(transactionRequest.address)

  //     /// Wait until the cancellation block and cancel the transaction
  //     await waitUntilBlock(0, cancelAt)
  //     const cancelTx = await transactionRequest.cancel({from: Owner})
  //     expect(cancelTx.receipt).to.exist

  //     /// Get the balances after the cancellation calls
  //     const afterCancelBal = await config.web3.eth.getBalance(Owner)
  //     const afterContractBal = await config.web3.eth.getBalance(transactionRequest.address)

  //     const updatedRequestData = await transactionRequest.requestData()
  //     const updatedLogs = updatedRequestData.logs.find(e => e.event === 'RequestData')
  //     // isCancelled === true
  //     assert(updatedLogs.args.bools[0] === true)

  //     // console.log(beforeCancelBal, afterCancelBal)
  //     // console.log(beforeContractBal, afterContractBal)

  // })

  // /// TODO
  // it('tests accounting for missed execution cancellation not by owner', async function() {
  //     const cancelAt = windowStart + executionWindow + 1

  //     /// Sanity checks
  //     assert(cancelAt > await config.web3.eth.getBlockNumber())

  //     const requestData = await transactionRequest.requestData()
  //     const logs = requestData.logs.find(e => e.event === 'RequestData')
  //     // requestData.meta.isCancelled === false
  //     assert(logs.args.bools[0] === false)
  //     // requestData.meta.owner === Owner
  //     assert(logs.args.addressArgs[2] === Owner)

  //     /// Get the balances before the cancellation calls
  //     const beforeCancelBal = await config.web3.eth.getBalance(Owner)
  //     const beforeContractBal = await config.web3.eth.getBalance(transactionRequest.address)

  //     /// Wait until the cancellation block and cancel the transaction
  //     await waitUntilBlock(0, cancelAt)
  //     const cancelTx = await transactionRequest.cancel({from: Owner})
  //     expect(cancelTx.receipt).to.exist

  //     /// Get the balances after the cancellation calls
  //     const afterCancelBal = await config.web3.eth.getBalance(Owner)
  //     const afterContractBal = await config.web3.eth.getBalance(transactionRequest.address)

  // })
})
