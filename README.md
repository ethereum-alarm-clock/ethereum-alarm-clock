# Ethereum Alarm Clock

[![Join the chat at https://gitter.im/ethereum-alarm-clock/ethereum-alarm-clock](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ethereum-alarm-clock/ethereum-alarm-clock?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
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

If you would like to run the test please set up your environment to use node v8.0.0, truffle v4.1.5 and the latest
ganache-cli.

```
nvm use 8.0.0
npm i
npm i -g truffle@4.1.5 
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

Please see the [`eac.js-cli`](https://github.com/ethereum-alarm-clock/eac.js-cli) repository for the commandline client.

## Deployment

The EAC contracts are deployed on both the Ropsten and Rinkeby testnets at the addresses below.

```
Ropsten

baseScheduler, 0x051E75717ad5580Fe136394813dE7D8C1357fe38

blockScheduler, 0xf91902fCd3eAAC65f589F6d40dAB0ed90168826E

claimLib, 0xf2a76BE09C67b1D04E80f3BaCBf969701965323c

executionLib, 0x73586F18D802Be9144a375F99BE6D66D13377D7e

groveLib, 0xCa72FE8A56E6B6829b0CBFDB4A30F9C2712f353F

iterTools, 0x7C02e16aa14FF0A471CA24875b0D0724DC48d21f

mathLib, 0x4d09aCb1551907235E3b28fEC1cED02c51274212

paymentLib, 0x77B69F499720B605fB7ae08f7a0AdE057cf9E9f6

requestFactory, 0x86D1F8ea688769e115246c3B0592e7Bf1184f012

requestLib, 0xcBd07A8F17934F76537F4D8c4a65a27009903Fe6

requestMetaLib, 0x0D853623aDE2b8DB28263929b0Bdc4048236657A

requestScheduleLib, 0xfc7F6890e8a45A659Bd9e32Ee81EA1Dfb600AEC1

requestTracker, 0x2D1091A8FC1b90Bd54603d44c3CBD81a80461893

safeMath, 0xBBC77FDa54876362c841BA31aa9f23a3D32F8B87

schedulerLib, 0x5f241fCE2c1C074429cCB95C85F9bB60A2ba134f

timestampScheduler, 0x6EaFdcc0045e3B020593EC5b92c3A0AAA2Bd49D9

transactionRecorder, 0xD5CC9B85c1A07A91DD4A243C5829cB329284d8Fb
```

```
Kovan

baseScheduler, 0x73A7E7C72D5cc6806599b74741f47e6F3E6f2322

blockScheduler, 0xe03E6Abfb48eE76E4034c7bcf4B928D909162516

claimLib, 0x9C1A56c2d0d5EbbBcf44bf5937080607cA7402E7

executionLib, 0x7AE28E63dD05cE989Fb68299E280da8b7aF5d723

groveLib, 0x4155040e728eA4d3e25b19b06499484ed82DC8d5

iterTools, 0x6a3b2EB1447906b7804DC91Ffd76F0BD34FAa484

mathLib, 0x3b814e30b489BA23a7E8889D41372f77aEF2D5bc

paymentLib, 0x81eef1E8e56fF96270c8B6C21Da34aED46dFd7f0

requestFactory, 0x209270d49A3673e8D6163849Fa0539800cfEeB9c

requestLib, 0x7c143715d35F5Fd903dC089d393a348a8D9148FF

requestMetaLib, 0x060Ad875cD1E6cCdc7D8D13af51766Fd9eD79f25

requestScheduleLib, 0xDc0FC4AD179Ab092cB69Db628f8731B5b5bcd1Ad

requestTracker, 0x39e9B6156C15dEc500383157c7f479de9B73E14a

safeMath, 0xFA12a64389Fa8bF5628954795f671dF4AA27E494

schedulerLib, 0xbFC43062CF27Ae3299255a0b2d2e352bbDB05ab4

timestampScheduler, 0x1DEB360969d6A2589BfEACfb9a875547E5e2a87E

transactionRecorder, 0x5F09f1AD09B0b9a1BdA460779967aB7d71839f5B
```

## Thanks and support
[<img src="https://s3.amazonaws.com/chronologic.network/ChronoLogic_logo.svg" width="128px">](https://github.com/chronologic)
