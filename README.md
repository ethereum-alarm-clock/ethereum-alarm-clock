# Ethereum Alarm Clock

[![Join the chat at https://gitter.im/pipermerriam/ethereum-alarm-clock](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pipermerriam/ethereum-alarm-clock?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/ethereum-alarm-clock/ethereum-alarm-clock.svg?branch=master)](https://travis-ci.org/chronologic/ethereum-alarm-clock)
[![Documentation Status](https://readthedocs.org/projects/ethereum-alarm-clock/badge/?version=latest)](http://ethereum-alarm-clock.readthedocs.io/en/latest/?badge=latest)


Source code for the [Ethereum Alarm Clock service](http://www.ethereum-alarm-clock.com/)

## What is the EAC (Ethereum Alarm Clock)

The Ethereum Alarm Clock is a smart contract protocol for scheduling Ethereum transactions 
to be executed in the future. It allows any address to set the parameters of a transaction and 
allow clients to call these transactions during the desired window. The EAC is agnostic to callers
so can be used by both human users and other smart contracts. Since all of the scheduling logic is 
contained in smart contracts, transactions can be scheduled from solidity.

Additionally the EAC faciliates the execution of this pool of scheduled transactions through a client. 
The EAC client continuously runs and searches for transactions which are scheduled to be executed soon 
then claims and executes them. For the EAC to be successful it depends on users who run execution clients. 
There are a few ways incentives for running these execution clients are baked in to the protocol itself, 
notably the claiming mechanism and the reward payment. 

## Running the tests

_Tests have been ported to Javascript and can now be run using the Truffle Suite_

Originally the test suite was written in Python using the Populus framework, these still exist for reference 
under the populus-tests/ directory. However, we have ported over the suite to use the Truffle framework since 
this may be more familiar to developers who know the Ethereum tooling in Javascript. These tests can be found in 
the [test/](test) directory.

If you would like to run the test please set up your environment to use node v8.0.0, truffle v4.0.1 and the latest
ganache-cli.

```
nvm use 8.0.0
npm i
npm i -g truffle@4.0.1 
npm i -g ganache-cli
```

Start ganache-cli in a terminal screen by running `ganache-cli`.

In another terminal screen run `npm test` at the root of the directory. This will run the npm test script that 
splits up the tests into different runtimes. The tests are split because the EAC is a moderately sized project and 
running all the tests with one command has a tendency to break down the ganache tester chain.

Each time you run the tests it is advised to rebuild your build/ folder, as this may lead to bugs if not done. You 
can do this by running the command `rm -rf build/`.

## Documentation

Documentation can be found on [Read the Docs](https://ethereum-alarm-clock.readthedocs.io/en/latest/).

## Using the CLI

Please see the [`eac.js`](https://github.com/ethereum-alarm-clock/eac.js) repository for the commandline client.

## Deployment

The EAC contracts are deployed on both the Ropsten and Rinkeby testnets at the addresses below.

```
Ropsten

baseScheduler, 0x051e75717ad5580fe136394813de7d8c1357fe38

blockScheduler, 0xf91902fcd3eaac65f589f6d40dab0ed90168826e

claimLib, 0xf2a76be09c67b1d04e80f3bacbf969701965323c

executionLib, 0x73586f18d802be9144a375f99be6d66d13377d7e

groveLib, 0xca72fe8a56e6b6829b0cbfdb4a30f9c2712f353f

iterTools, 0x7c02e16aa14ff0a471ca24875b0d0724dc48d21f

mathLib, 0x4d09acb1551907235e3b28fec1ced02c51274212

paymentLib, 0x77b69f499720b605fb7ae08f7a0ade057cf9e9f6

requestFactory, 0x86d1f8ea688769e115246c3b0592e7bf1184f012

requestLib, 0xcbd07a8f17934f76537f4d8c4a65a27009903fe6

requestMetaLib, 0x0d853623ade2b8db28263929b0bdc4048236657a

requestScheduleLib, 0xfc7f6890e8a45a659bd9e32ee81ea1dfb600aec1

requestTracker, 0x2d1091a8fc1b90bd54603d44c3cbd81a80461893

safeMath, 0xbbc77fda54876362c841ba31aa9f23a3d32f8b87

schedulerLib, 0x5f241fce2c1c074429ccb95c85f9bb60a2ba134f

timestampScheduler, 0x6eafdcc0045e3b020593ec5b92c3a0aaa2bd49d9

transactionRecorder, 0xd5cc9b85c1a07a91dd4a243c5829cb329284d8fb
```

```
Rinkeby

baseScheduler, 0x3c85c56230db82ca57893debf58b5cea3c829a58

blockScheduler, 0x9e2ca249caad16b982d34e6c013f2e4ff9ff44fd

claimLib, 0x6214779413a68857eef3a7e39af252cf32e84640

executionLib, 0xf57403ff40173f92729251dab6b28ae8b0d35a21

groveLib, 0xf628e5650720c66b8ee5a1de1abde2825fdc78e7

iterTools, 0xdd9af26afb2382aab7b37ec3e2d6b97d701eb5cf

mathLib, 0xda81053737a137d624db2b9cbf1722bef6a21d1a

paymentLib, 0x639da3a1ed49b310b8ca2533d863e315f8383bad

requestFactory, 0xb5f3538bf4b751d44a68937eee6fdfa678dc9ec1

requestLib, 0x5fcf1ad079810465afa7f82ff1a4040f86699d4c

requestMetaLib, 0x59e6f502615b5b1477f28083a04e8fbb668064e0

requestScheduleLib, 0xfdf449cf4f2058abd9743778d71173e7c394fb3a

requestTracker, 0xb852c89103eaf0b01b9f010000a7e16effcd14c3

safeMath, 0xdaa478994a8ffcf70566fefdf429aeb2811f3540

schedulerLib, 0x87ee8a926b4576152409df632fc9c047d7164e19

timestampScheduler, 0x5cbd0d763120f1e8ba293fcfc07b0278f8e384fc

transactionRecorder, 0x4c5b46da3c64f8ef546644fea7cf82d10bd321d2
```

## Thanks and support
[<img src="https://s3.amazonaws.com/chronologic.network/ChronoLogic_logo.svg" width="128px">](https://github.com/chronologic)
