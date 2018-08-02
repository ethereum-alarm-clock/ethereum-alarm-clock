require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

const SimpleToken = artifacts.require("./SimpleToken.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

const { waitUntilBlock } = require("@digix/tempo")(web3)

const ethUtil = require("ethereumjs-util")
const config = require("../../config")
const { RequestData, wasAborted } = require("../dataHelpers.js")
const simpleTokenAbi = require("./SimpleToken.json").abi

contract("TransactionRequestCore proxy function", (accounts) => {
  const claimWindowSize = 25 // blocks
  const freezePeriod = 5 // blocks
  const reservedWindowSize = 10 // blocks
  const executionWindow = 10 // blocks
  const gasPrice = config.web3.utils.toWei("66", "gwei")
  const requiredDeposit = config.web3.utils.toWei("66", "kwei")

  const testData32 = ethUtil.bufferToHex(Buffer.from("A1B2".padEnd(32, "FF")))

  it("only allows calling proxy after execution window and by the scheduling account", async () => {
    const curBlockNum = await config.web3.eth.getBlockNumber()
    const windowStart = curBlockNum + 38 + 10 + 5

    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        accounts[1], // fee recipient
        accounts[3], // toAddress
      ],
      [
        12345, // fee
        332332, // bounty
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
      { value: config.web3.utils.toWei("500", "finney") }
    )

    const requestData = await RequestData.from(txRequest)

    const duringExecutionWindow = (
      requestData.schedule.windowStart + requestData.schedule.windowSize
    ) - 2

    await waitUntilBlock(0, duringExecutionWindow)

    // This fails because it is not after the exeucution window
    await txRequest
      .proxy(accounts[7], testData32)
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    const afterExecutionWindow = (
      requestData.schedule.windowStart + requestData.schedule.windowSize
    ) + 1

    await waitUntilBlock(0, afterExecutionWindow)

    // This throws because it is not the scheduling account
    await txRequest
      .proxy(accounts[7], testData32, { from: accounts[4] })
      .should.be.rejectedWith("VM Exception while processing transaction: revert")

    // This is allowed since it is from scheduling accounts
    const tx = await txRequest.proxy(accounts[7], testData32)
    expect(tx.receipt.status).to.be.oneOf(['0x1', '0x01', 1])
  })

  it("does some fancy stuff with proxy", async () => {
    // Boring set up stuff
    const curBlockNum = await config.web3.eth.getBlockNumber()
    const windowStart = curBlockNum + 38 + 10 + 5

    const tokenContract = await SimpleToken.new(123454321)
    const buyTokensSig = config.web3.utils.sha3("buyTokens()").slice(0, 10)

    const txRequest = await TransactionRequestCore.new()
    await txRequest.initialize(
      [
        accounts[0], // createdBy
        accounts[0], // owner
        accounts[1], // fee recipient
        tokenContract.address, // toAddress
      ],
      [
        12345, // fee
        332332, // bounty
        claimWindowSize,
        freezePeriod,
        reservedWindowSize,
        1, // temporalUnit = 1, aka blocks
        executionWindow,
        windowStart,
        3000000, // callGas
        12345, // callValue
        gasPrice,
      ],
      buyTokensSig,
      { value: config.web3.utils.toWei("500", "finney") }
    )

    const requestData = await RequestData.from(txRequest)
    const executeAt = requestData.schedule.windowStart + 1

    await waitUntilBlock(0, executeAt)

    const executeTx = await txRequest.execute({
      from: accounts[4],
      gas: 3200000,
      gasPrice,
    })
    expect(executeTx.receipt).to.exist
    expect(wasAborted(executeTx)).to.be.false

    const balance = (await tokenContract.balanceOf(txRequest.address)).toNumber()
    expect(balance).to.equal(12345 * 30) // callValue * rate

    const afterExecutionWindow = (
      requestData.schedule.windowStart + requestData.schedule.windowSize
    ) + 2

    await waitUntilBlock(0, afterExecutionWindow)

    const t = new config.web3.eth.Contract(simpleTokenAbi)
    const encodedData = t.methods.transfer(accounts[8], 30000).encodeABI()
    // / This data was generated locally using the method above^^
    /* eslint-disable max-len */
    // const encoded_data = '0xa9059cbb000000000000000000000000737b4d5a9f46839501719b5d388b7c487b55957a0000000000000000000000000000000000000000000000000000000000007530'

    // / NOTE the method below vv SHOULD work but generates the wrong data string for some reason
    // const transferSig = config.web3.utils.sha3('transfer(address,uint256').slice(0,10)
    // const arg1 = config.web3.utils.padLeft(accounts[8], 64).slice(2)
    // const arg2 = config.web3.utils.padLeft(30000, 64).slice(2)
    // const encodedTransferData = transferSig.concat(arg1).concat(arg2)

    // console.log(encodedTransferData)
    // console.log(e)
    await txRequest.proxy(tokenContract.address, encodedData)

    expect((await tokenContract.balanceOf(accounts[8])).toNumber()).to.equal(30000)
  })
})
