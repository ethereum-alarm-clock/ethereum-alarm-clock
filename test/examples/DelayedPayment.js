require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

const { waitUntilBlock } = require("@digix/tempo")(web3)

const config = require("../../config")

const BlockScheduler = artifacts.require("./BlockScheduler.sol")
const RequestFactory = artifacts.require("./RequestFactory.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")
const TransactionRequestInterface = artifacts.require("./TransactionRequestInterface")
const DelayedPayment = artifacts.require("./DelayedPayment.sol")

const getBalance = async address => parseInt(await config.web3.eth.getBalance(address), 10)

const execute = async (payment, miner, numberOfBlocks) => {
  const scheduledTransactionAddress = await payment.payment()

  const currentBlock = await config.web3.eth.getBlockNumber()
  await waitUntilBlock(0, currentBlock + numberOfBlocks)

  const scheduledTransaction = TransactionRequestInterface.at(scheduledTransactionAddress)
  await scheduledTransaction.execute({ from: miner, gas: 3000000, gasPrice: 20000000000 })
}

contract("Delayed payment", (accounts) => {
  it("should schedule and execute delayed payment transaction", async () => {
    const transactionRequestCore = await TransactionRequestCore.deployed()

    const requestFactory = await RequestFactory.new(transactionRequestCore.address)
    const blockScheduler = await BlockScheduler.new(
      requestFactory.address,
      "0xecc9c5fff8937578141592e7E62C2D2E364311b8"
    )

    const numberOfBlocks = 50
    const paymentValue = 10 ** 17 // 0.1 ETH
    const recipient = accounts[1]
    const miner = accounts[2]

    const payment = await DelayedPayment.new(
      blockScheduler.address,
      numberOfBlocks,
      recipient,
      paymentValue,
      { value: paymentValue * 2 }
    )

    const recipientBalance = await getBalance(recipient)
    await execute(payment, miner, numberOfBlocks)

    await payment.collectRemaining()

    const recipientBalanceAfter = await getBalance(recipient)
    expect(recipientBalanceAfter).to.equals(recipientBalance + paymentValue)

    const scheduledPaymentBalance = await getBalance(await payment.payment())
    expect(scheduledPaymentBalance).to.equals(0, "scheduledPaymentBalance should be 0")

    const paymentContractBalance = await getBalance(payment.address)
    expect(paymentContractBalance).to.equals(0, "paymentContractBalance should be 0")
  })
})
