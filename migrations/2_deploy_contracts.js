const fs = require('fs')

// / Contract artifacts (located in the build/ folder)
const BaseScheduler = artifacts.require("./BaseScheduler.sol"),
  BlockScheduler = artifacts.require("./BlockScheduler.sol"),
  ClaimLib = artifacts.require("./ClaimLib.sol"),
  ExecutionLib = artifacts.require("./ExecutionLib.sol"),
  GroveLib = artifacts.require("./GroveLib.sol"),
  IterTools = artifacts.require("./IterTools.sol"),
  MathLib = artifacts.require("./MathLib.sol"),
  PaymentLib = artifacts.require("./PaymentLib.sol"),
  RequestFactory = artifacts.require("./RequestFactory.sol"),
  RequestFactoryInterface = artifacts.require("./RequestFactoryInterface.sol"),
  RequestLib = artifacts.require("./RequestLib.sol"),
  RequestMetaLib = artifacts.require("./RequestMetaLib.sol"),
  RequestScheduleLib = artifacts.require("./RequestScheduleLib.sol"),
  RequestTracker = artifacts.require("./RequestTracker.sol"),
  RequestTrackerInterface = artifacts.require("./RequestTrackerInterface.sol"),
  SafeMath = artifacts.require("./SafeMath.sol"),
  SchedulerInterface = artifacts.require("./SchedulerInterface.sol"),
  SchedulerLib = artifacts.require("./SchedulerLib.sol"),
  TimestampScheduler = artifacts.require("./TimestampScheduler.sol"),
  TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol"),
  TransactionRequestInterface = artifacts.require("./TransactionRequestInterface.sol");

const TransactionRecorder = artifacts.require("./TransactionRecorder.sol");

module.exports = function (deployer) {
  console.log(`${"-".repeat(30)}
NOW DEPLOYING THE ETHEREUM ALARM CLOCK CONTRACTS...\n`)

  deployer.deploy(GroveLib, { gas: 2500000 }  )
    .then(() => deployer.deploy([
        [MathLib, {gas: 250000}],
        [IterTools, {gas: 250000}],
        [ExecutionLib, {gas: 250000}],
        [RequestMetaLib,{gas: 250000}],
        [SafeMath, {gas: 250000}]
    ]))
    .then(() => {
      deployer.link(SafeMath, ClaimLib)

      return deployer.deploy(ClaimLib, { gas: 250000 })
    })
    .then(() => {
      deployer.link(ExecutionLib, PaymentLib)
      deployer.link(MathLib, PaymentLib)
      deployer.link(SafeMath, PaymentLib)

      return deployer.deploy(PaymentLib, { gas: 250000 })
    })
    .then(() => {
      deployer.link(SafeMath, RequestScheduleLib)
      return deployer.deploy(RequestScheduleLib, { gas: 250000 })
    })
    .then(() => {
      deployer.link(ClaimLib, RequestLib)
      deployer.link(ExecutionLib, RequestLib)
      deployer.link(MathLib, RequestLib)
      deployer.link(PaymentLib, RequestLib)
      deployer.link(RequestMetaLib, RequestLib)
      deployer.link(RequestScheduleLib, RequestLib)
      deployer.link(SafeMath, RequestLib)

      return deployer.deploy(RequestLib, { gas: 3000000 })
    })
    .then(() => {
      deployer.link(MathLib, SchedulerLib)
      deployer.link(PaymentLib, SchedulerLib)
      deployer.link(RequestLib, SchedulerLib)
      deployer.link(SafeMath, SchedulerLib)

      return deployer.deploy(SchedulerLib, { gas: 500000 })
    })
    .then(() => {
      deployer.link(GroveLib, RequestTracker)
      deployer.link(MathLib, RequestTracker)

      return deployer.deploy(RequestTracker, { gas: 1000000 })
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

      return deployer.deploy(TransactionRequestCore, { gas: 3000000 })
    })
    .then(() => {
      deployer.link(ClaimLib, RequestFactory)
      deployer.link(MathLib, RequestFactory)
      deployer.link(RequestScheduleLib, RequestFactory)
      deployer.link(IterTools, RequestFactory)
      deployer.link(PaymentLib, RequestFactory)
      deployer.link(RequestLib, RequestFactory)
      deployer.link(RequestTracker, RequestFactory)
      deployer.link(SafeMath, RequestFactory)
      return deployer.deploy(RequestFactory, RequestTracker.address, TransactionRequestCore.address, { gas: 1500000 })
    })
    .then(() => {
      deployer.link(RequestScheduleLib, BaseScheduler)
      deployer.link(PaymentLib, BaseScheduler)
      deployer.link(SchedulerLib, BaseScheduler)
      deployer.link(RequestLib, BaseScheduler)
      deployer.link(MathLib, BaseScheduler)

      return deployer.deploy(BaseScheduler, { gas: 1500000 })
    })
    .then(() => {
      deployer.link(SchedulerLib, BlockScheduler)
      deployer.link(RequestScheduleLib, BlockScheduler)
      deployer.link(PaymentLib, BlockScheduler)
      deployer.link(RequestLib, BlockScheduler)
      deployer.link(MathLib, BlockScheduler)

      return deployer.deploy(BlockScheduler, RequestFactory.address, 0xecc9c5fff8937578141592e7E62C2D2E364311b8, { gas: 1500000 })
    })
    .then(() => {
      deployer.link(SchedulerLib, TimestampScheduler)
      deployer.link(RequestScheduleLib, TimestampScheduler)
      deployer.link(PaymentLib, TimestampScheduler)
      deployer.link(RequestLib, TimestampScheduler)
      deployer.link(MathLib, TimestampScheduler)

      return deployer.deploy(TimestampScheduler, RequestFactory.address, 0xecc9c5fff8937578141592e7E62C2D2E364311b8, { gas: 1500000 })
    })
    .then(() => {
        return deployer.deploy(TransactionRecorder, {gas: 750000})
    })
    .then(() => {
      const contracts = {
        baseScheduler: BaseScheduler.address,
        blockScheduler: BlockScheduler.address,
        claimLib: ClaimLib.address,
        executionLib: ExecutionLib.address,
        groveLib: GroveLib.address,
        iterTools: IterTools.address,
        mathLib: MathLib.address,
        paymentLib: PaymentLib.address,
        requestFactory: RequestFactory.address,
        requestLib: RequestLib.address,
        requestMetaLib: RequestMetaLib.address,
        requestScheduleLib: RequestScheduleLib.address,
        requestTracker: RequestTracker.address,
        safeMath: SafeMath.address,
        schedulerLib: SchedulerLib.address,
        timestampScheduler: TimestampScheduler.address,
        transactionRequestCore: TransactionRequestCore.address,
        transactionRecorder: TransactionRecorder.address
      }

    fs.writeFileSync('contracts.json', JSON.stringify(contracts))
    
    fs.unlinkSync('contracts.info')
    Object.keys(contracts).forEach((key) => {
        fs.appendFileSync('contracts.info', `${key}, ${contracts[key]}\n`)
    })

      //         console.log(`CONTRACTS SUCCESSFULLY DEPLOYED
      // ${"-".repeat(30)}
      // see deployed.info for addresses of all contracts
      //         `)
    })
}
