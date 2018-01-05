# Ethereum Alarm Clock

[![Join the chat at https://gitter.im/pipermerriam/ethereum-alarm-clock](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pipermerriam/ethereum-alarm-clock?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/ethereum-alarm-clock/ethereum-alarm-clock.svg?branch=master)](https://travis-ci.org/chronologic/ethereum-alarm-clock)
[![Documentation Status](https://readthedocs.org/projects/ethereum-alarm-clock/badge/?version=latest)](http://ethereum-alarm-clock.readthedocs.io/en/latest/?badge=latest)


Source code for the [Ethereum Alarm Clock service](http://www.ethereum-alarm-clock.com/)

## What is the EAC (Ethereum Alarm Clock)

The Ethereum Alarm Clock is a smart contract protocol for scheduling Ethereum transactions to be executed in the future. It allows any address to set the parameters of a transaction and allow clients to call these transactions during the desired window. The EAC is agnostic to callers so can be used by both human users and other smart contracts. Since all of the scheduling logic is contained in smart contracts, transactions can be scheduled from solidity.

Additionally the EAC faciliates the execution of this pool of scheduled transactions through a client. The EAC client continuously runs and searches for transactions which are scheduled to be executed soon then claims and executes them. For the EAC to be successful it depends on users who run execution clients. There are a few ways incentives for running these execution clients are baked in to the protocol itself, notably the claiming mechanism and the reward payment. 

## Running the tests

_Tests have been ported to Javascript and can now be run using the Truffle Suite_

Originally the test suite was written in Python using the Populus framework, these still exist for reference under the populus-tests/ directory. However, we have ported over the suite to use the Truffle framework since this may be more familiar to developers who know the Ethereum tooling in Javascript. These tests can be found in the test/ directory.

If you would like to run the test please set up your environment to use node v8.0.0, truffle v4.0.1 and the latest ganache-cli.

```
nvm use 8.0.0
npm i
npm i -g truffle@4.0.1 
npm i -g ganache-cli
```

Start ganache-cli in a terminal screen by running `ganache-cli`.

In another terminal screen run `npm test` at the root of the directory. This will run the npm test script that splits up the tests into different runtimes. The tests are split because the EAC is a moderately sized project and running all the tests with one command has a tendency to break down the ganache tester chain.

Each time you run the tests it is advised to rebuild your build/ folder, as this may lead to bugs if not done. You can do this by running the command `rm -rf build/`.

## Documentation

Documentation can be found on [Read the Docs](https://ethereum-alarm-clock.readthedocs.io/en/latest/).

## Using the CLI

Please see the [`eac.js`](https://github.com/ethereum-alarm-clock/eac.js) repository for the commandline client.

## Deployment

The EAC contracts are deployed on both the Ropsten and Rinkeby testnets at the addresses below.

```
Ropsten

baseScheduler, 0x8b938aa0ff8a099ca67e13a5c24593e91c7500cf

blockScheduler, 0xe07904827235c15168d1f4d61b79553a985ff3f1

claimLib, 0xdf81a22d0717586cde667e35d19d5553cc68e250

executionLib, 0x7bee0a08cd24b159576a194e12eaec11c46f1222

groveLib, 0x6bb31ff1ed0a7586039d46e399e20b749e13116e

iterTools, 0xe72747e81befadba4d8e969cd7055e06a58e84ba

mathLib, 0x466f50a7528d7108c8507a6416895b10fba9f344

paymentLib, 0x561ebc8af36182914738cd8d3f19ddd09d1f9c9f

requestFactory, 0x8edb8836d67ccf18a601dac529ae9349d733aa33

requestLib, 0x7bb340558c70c9673c3654a975bc0ddbbca3e209

requestMetaLib, 0x70138db1fe900b7d0041bd0841923f9744ad8892

requestScheduleLib, 0xef2ecbd4586efcb34c847c9122638634f9cc69cf

requestTracker, 0x58e1ecd989c8ba8a093cac62a4e74dd9ff14e951

safeMath, 0x2d94fa4d4f2c988f9873bcd2386b29d21e266a19

schedulerLib, 0x1512efb7ff2f4377a412f5ca21b28f6263a63341

timestampScheduler, 0xa0739a169ba3c7d859f9fd6c2ba689f9fa9b86f7

transactionRecorder, 0x2f554e49b38ec15126e4f41df1192f3e28311d0a
```

```
Rinkeby

baseScheduler, 0x059763c4f1d761ae255ed593e3a267e793d4d71d

blockScheduler, 0xf60c376a4faa7116b7a452e5ab7318faf63c6153

claimLib, 0xfc5e333f5ded9aefd625d9be6f20916bc68832bd

executionLib, 0x06f0f303514029481f76f793267f41d2bd8f47e2

groveLib, 0xbb9f3d2fe58c9fdc3bf6d1b28415a479ed931ed7

iterTools, 0x4dd38f289dcfe812cb5ec9f1ede36edeb5528618

mathLib, 0xac0234a515299b4e0cd6a11aa209b6e304a2b295

paymentLib, 0x06aea9c2f88eb9db0ababd4328b73eb55cf6589a

requestFactory, 0x8b216a851b15f9d058fe48b671b8234a7060ce62

requestLib, 0x2a3ce27000c74522bc042012bc41dfae150d4852

requestMetaLib, 0xd5d261a2f468f1d982d91d8a1e86e8541935a0f3

requestScheduleLib, 0x096725e5c5eed10b4a43308a215beec8f6a7be68

requestTracker, 0xa4175f27b8baaede19cdefd03b86d292e06073b3

safeMath, 0x3a5ad9ddc15049122766c2eeba33f7fb322d4d41

schedulerLib, 0xb840466bee43bf87a00aadc35ed790b2beda28b7

timestampScheduler, 0x474232b7cd87b3ec8272b2692663a9340f3bfa3f

transactionRecorder, 0xfcd7b04d9e614dff981e830b6b98f4bff8c3636d

```