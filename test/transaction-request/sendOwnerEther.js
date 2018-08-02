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
const Proxy = artifacts.require("./Proxy.sol")

contract("TransactionRequestCore", async (accounts) => {
  const getBalance = async address => parseInt(await config.web3.eth.getBalance(address), 10)

  const wallet = accounts[1]

  let proxy
  let scheduledTransactionAddress
  let remainingScheduledTransactionBalance
  let walletBalanceAfterExecution

  before(async () => {
    const transactionRequestCore = await TransactionRequestCore.deployed()

    const requestFactory = await RequestFactory.new(transactionRequestCore.address)
    const blockScheduler = await BlockScheduler.new(
      requestFactory.address,
      "0xecc9c5fff8937578141592e7E62C2D2E364311b8"
    )

    const initialWalletBalance = await getBalance(wallet)
    const funds = 10 ** 18 // 1 ETH
    const delay = 50
    const payout = 10 ** 17 // 0.1 ETH
    const gasPrice = 10 ** 6

    proxy = await Proxy.new(
      blockScheduler.address,
      wallet,
      payout,
      gasPrice,
      delay,
      { value: funds }
    )

    const proxyBalance = await getBalance(proxy.address)
    expect(proxyBalance).to.equal(0)

    const currentBlock = await config.web3.eth.getBlockNumber()
    await waitUntilBlock(0, currentBlock + delay)

    scheduledTransactionAddress = await proxy.scheduledTransaction()
    const scheduledTransaction = TransactionRequestInterface.at(scheduledTransactionAddress)

    await scheduledTransaction.execute({ from: accounts[2], gas: 3000000, gasPrice })

    walletBalanceAfterExecution = await getBalance(wallet)
    expect(walletBalanceAfterExecution).to.equals(initialWalletBalance + payout)

    remainingScheduledTransactionBalance = await getBalance(scheduledTransactionAddress)
    expect(remainingScheduledTransactionBalance).to.be.greaterThan(0)
  })

  it("should fail to send remaining funds to the contract", async () => {
    // this is not going to succeed because of fallback
    // function in proxy contract which consumes more than 2300 gas
    await proxy.sendOwnerEther(proxy.address)

    const scheduledTransactionBalance = await getBalance(scheduledTransactionAddress)
    expect(scheduledTransactionBalance).to.equal(remainingScheduledTransactionBalance)
  })

  it("should fail to send remaining funds to the account when not owner", async () => {
    await proxy.sendOwnerEther(wallet, { from: accounts[2] })

    const scheduledTransactionBalance = await getBalance(scheduledTransactionAddress)
    expect(scheduledTransactionBalance).to.equal(remainingScheduledTransactionBalance)
  })

  it("should fail to send remaining funds to null account", async () => {
    await proxy.sendOwnerEther('')

    const scheduledTransactionBalance = await getBalance(scheduledTransactionAddress)
    expect(scheduledTransactionBalance).to.equal(remainingScheduledTransactionBalance)
  })

  it("should succeed to send remaining funds to the account", async () => {
    await proxy.sendOwnerEther(wallet)

    const scheduledTransactionBalance = await getBalance(scheduledTransactionAddress)
    expect(scheduledTransactionBalance).to.equal(0)

    const walletBalance = await getBalance(wallet)
    expect(walletBalance)
      .to.equal(walletBalanceAfterExecution + remainingScheduledTransactionBalance)
  })
})
