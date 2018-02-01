require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")

const config = require("../../config")

contract("Test TransactionRecorder", (accounts) => {
  it("should send a transaction as specified", async () => {
    const txRecorder = await TransactionRecorder.new()

    let wasCalled = await txRecorder.wasCalled()
    let lastCaller = await txRecorder.lastCaller()
    let lastCallValue = await txRecorder.lastCallValue()
    let lastCallGas = await txRecorder.lastCallGas()
    let lastCallData = await txRecorder.lastCallData()

    expect(wasCalled).to.be.false
    lastCaller.should.equal("0x0000000000000000000000000000000000000000")
    lastCallValue.toNumber().should.equal(0)
    lastCallGas.toNumber().should.equal(0)
    lastCallData.should.equal("0x")

    const testCallData = config.web3.utils.toHex("this-is-call-data")

    await txRecorder.sendTransaction({
      value: 121212,
      gas: 3000000,
      data: "this-is-call-data",
    })

    wasCalled = await txRecorder.wasCalled()
    lastCaller = await txRecorder.lastCaller()
    lastCallValue = await txRecorder.lastCallValue()
    lastCallGas = await txRecorder.lastCallGas()
    lastCallData = await txRecorder.lastCallData()

    expect(wasCalled).to.be.true
    lastCaller.should.equal(accounts[0])

    expect(wasCalled, "Should have been called.").to.be.true
    expect(
      lastCaller === accounts[0],
      "Should have registered the correct address."
    ).to.be.true
    expect(lastCallValue.toNumber() === 121212, "Sent the correct value.")

    const callGasDelta = lastCallGas.toNumber() - 3000000
    expect(lastCallGas.toNumber() > 0, "Should have used some gas.").to.be.true
    expect(callGasDelta < 10000, "But not too much gas...").to.be.true

    // Here we take out the `0x` of the test call data in hex representation
    //  and also remove the first 4 hex characters from the call data.
    expect(
      testCallData.slice(2) === lastCallData.slice(6),
      "The call data should be the same."
    ).to.be.true
  })
})
