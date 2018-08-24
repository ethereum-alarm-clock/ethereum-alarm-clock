/* eslint-disable no-console */
const fs = require('fs')

// / Contract artifacts (located in the build/ folder)
const BaseScheduler = artifacts.require("./BaseScheduler.sol")
const BlockScheduler = artifacts.require("./BlockScheduler.sol")
const ClaimLib = artifacts.require("./ClaimLib.sol")
const ExecutionLib = artifacts.require("./ExecutionLib.sol")
const IterTools = artifacts.require("./IterTools.sol")
const MathLib = artifacts.require("./MathLib.sol")
const PaymentLib = artifacts.require("./PaymentLib.sol")
const RequestFactory = artifacts.require("./RequestFactory.sol")
const RequestLib = artifacts.require("./RequestLib.sol")
const RequestMetaLib = artifacts.require("./RequestMetaLib.sol")
const RequestScheduleLib = artifacts.require("./RequestScheduleLib.sol")
const SafeMath = artifacts.require("./SafeMath.sol")
const TimestampScheduler = artifacts.require("./TimestampScheduler.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")
const TransactionRecorder = artifacts.require("./TransactionRecorder.sol")

const MultiSigAddress = '0x47863b9E8C590323768E4352A78Ca759BBd37E8B';

const overwrite = false;

module.exports = (deployer, network) => {
  console.log(`${"-".repeat(30)}
NOW DEPLOYING THE ETHEREUM ALARM CLOCK CONTRACTS...\n`)

  let balanceBefore;
  web3.eth.getBalance("0x21ec253c9186065f05fb3f541085a185f96a16ee", (err, res) => {
    balanceBefore = res;
  })

  deployer.deploy(MathLib, { gas: 250000, overwrite })
    .then(() => deployer.deploy(IterTools, { gas: 250000, overwrite }))
    .then(() => deployer.deploy(ExecutionLib, { gas: 250000, overwrite }))
    .then(() => deployer.deploy(RequestMetaLib, { gas: 250000, overwrite }))
    .then(() => deployer.deploy(SafeMath, { gas: 250000, overwrite }))
    .then(() => {
      deployer.link(SafeMath, ClaimLib)

      return deployer.deploy(ClaimLib, { gas: 250000, overwrite })
    })
    .then(() => {
      deployer.link(SafeMath, PaymentLib)

      return deployer.deploy(PaymentLib, { gas: 250000, overwrite })
    })
    .then(() => {
      deployer.link(SafeMath, RequestScheduleLib)

      return deployer.deploy(RequestScheduleLib, { gas: 250000, overwrite })
    })
    .then(() => {
      deployer.link(ClaimLib, RequestLib)
      deployer.link(ExecutionLib, RequestLib)
      deployer.link(MathLib, RequestLib)
      deployer.link(PaymentLib, RequestLib)
      deployer.link(RequestMetaLib, RequestLib)
      deployer.link(RequestScheduleLib, RequestLib)
      deployer.link(SafeMath, RequestLib)

      return deployer.deploy(RequestLib, { gas: 3000000, overwrite })
    })
    .then(() => {
      deployer.link(ClaimLib, TransactionRequestCore)
      deployer.link(ExecutionLib, TransactionRequestCore)
      deployer.link(MathLib, TransactionRequestCore)
      deployer.link(PaymentLib, TransactionRequestCore)
      deployer.link(RequestMetaLib, TransactionRequestCore)
      deployer.link(RequestLib, TransactionRequestCore)
      deployer.link(RequestScheduleLib, TransactionRequestCore)
      deployer.link(SafeMath, TransactionRequestCore)

      return deployer.deploy(TransactionRequestCore, { gas: 3000000, overwrite })
    })
    .then(() => {
      deployer.link(ClaimLib, RequestFactory)
      deployer.link(MathLib, RequestFactory)
      deployer.link(RequestScheduleLib, RequestFactory)
      deployer.link(IterTools, RequestFactory)
      deployer.link(PaymentLib, RequestFactory)
      deployer.link(RequestLib, RequestFactory)
      deployer.link(SafeMath, RequestFactory)
      return deployer.deploy(
        RequestFactory,
        TransactionRequestCore.address,
        { gas: 1900000, overwrite }
      )
    })
    // .then(requestFactory => requestFactory.transferOwnership(MultiSigAddress))
    .then(() => {
      deployer.link(RequestScheduleLib, BaseScheduler)
      deployer.link(PaymentLib, BaseScheduler)
      deployer.link(RequestLib, BaseScheduler)
      deployer.link(MathLib, BaseScheduler)

      return deployer.deploy(BaseScheduler, { gas: 1500000 })
    })
    .then(() => {
      deployer.link(RequestScheduleLib, BlockScheduler)
      deployer.link(PaymentLib, BlockScheduler)
      deployer.link(RequestLib, BlockScheduler)
      deployer.link(MathLib, BlockScheduler)

      return deployer.deploy(
        BlockScheduler,
        RequestFactory.address,
        MultiSigAddress,
        { gas: 1500000 }
      )
    })
    .then(() => {
      deployer.link(RequestScheduleLib, TimestampScheduler)
      deployer.link(PaymentLib, TimestampScheduler)
      deployer.link(RequestLib, TimestampScheduler)
      deployer.link(MathLib, TimestampScheduler)

      return deployer.deploy(
        TimestampScheduler,
        RequestFactory.address,
        MultiSigAddress,
        { gas: 1500000 }
      )
    })
    .then(() => deployer.deploy(TransactionRecorder, { gas: 750000 }))
    .then(() => {
      const contracts = {
        baseScheduler: BaseScheduler.address,
        blockScheduler: BlockScheduler.address,
        claimLib: ClaimLib.address,
        executionLib: ExecutionLib.address,
        iterTools: IterTools.address,
        mathLib: MathLib.address,
        paymentLib: PaymentLib.address,
        requestFactory: RequestFactory.address,
        requestLib: RequestLib.address,
        requestMetaLib: RequestMetaLib.address,
        requestScheduleLib: RequestScheduleLib.address,
        safeMath: SafeMath.address,
        timestampScheduler: TimestampScheduler.address,
        transactionRequestCore: TransactionRequestCore.address,
        transactionRecorder: TransactionRecorder.address
      }
      if (network && network !== "development") {
        const contractsFile = `${network}.json`
        const contractsInfoFile = `${network}.info`
        fs.writeFileSync(contractsFile, JSON.stringify(contracts))

        if (fs.existsSync(contractsInfoFile)) { fs.unlinkSync(contractsInfoFile) }

        Object.keys(contracts).forEach((key) => {
          fs.appendFileSync(contractsInfoFile, `${key}, ${contracts[key]}\n`)
        })

        let balanceAfter;
        web3.eth.getBalance("0x21ec253c9186065f05fb3f541085a185f96a16ee", (e, r) => {
          balanceAfter = r;
          fs.writeFileSync('balances', `
  balanceBefore: ${balanceBefore}
  balanceAfter: ${balanceAfter}
  `);
        });
      }
    })
    .then(() => RequestFactory.at(RequestFactory.address))
    .then(requestFactory => requestFactory.owner())
    .then(owner => console.log(owner))
}
