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

baseScheduler, 0xa3258348abe4fee76b1c5b5fad1b7bedee6ad24c

blockScheduler, 0x9ac3c5d91c408b5cd8fe23fe915ba471d67333bb

claimLib, 0xc2387b54c165a65d485628809840132e22d10174

executionLib, 0xbd97838f0cfe6f01f1b36331fc8e98899ae6a2ad

groveLib, 0xccc00b710d97a1a8af7bce46b521b8ade587e1c8

iterTools, 0x12361ff30caa51a0e479407181a9a41f8a69fe52

mathLib, 0x3507f7b3c6520f6cb381e5417726a745edfadd35

paymentLib, 0x415a67edc449cc272192a3e276ac24d6044358ed

requestFactory, 0x99f93210b3f376ec627393b83569c7bd96923741

requestLib, 0xe43e82c1151bcdd1f807b1c0d1353742b30cd9aa

requestMetaLib, 0x3f86cd019cc128d63570e6f2e940c0c270a9f339

requestScheduleLib, 0xe97b8b9c6b4a2c3d4f2c7d16120d67873413ab47

requestTracker, 0x2864515319de2072938e87cb8411d8c266514b90

safeMath, 0x5940da705d6936d45ed30ccab1dcb6c871fac035

schedulerLib, 0x903c136841ce5732ea480d09f5292209be031041

timestampScheduler, 0xa033ad35a7d6f588cf256bfa640de60d2b54d6ff

transactionRecorder, 0xcbf9846994046572b7ee35fdb12cb5dbfc34ffc2
```

```
Rinkeby

baseScheduler, 0xfa1a5152d70aa9cd6cf87c3e82685c5fe49b635b

blockScheduler, 0x9e055469e33c8692e28500381afb9d0225a461c9

claimLib, 0x64dfc07f4fcd7f894ef87919a992c87f79f93720

executionLib, 0x2dde0aa6a648a19694f66a99c057a635cf64c93c

groveLib, 0x11f5a4afc5d11411b796c947e60f87896e04e2e3

iterTools, 0x1479a9dd5bca41e2f6a2f57459579beca929c432

mathLib, 0x14b7cfbd3f06b15cf91721721bc1e098c38c2213

paymentLib, 0x1acf6215213acd2e1bb733a9bb29f28c36b2d448

requestFactory, 0xe34fd3d0180ca9274e8a880533e66694083e23cb

requestLib, 0x810e90f7ba04367ff3833eddea450f66f972d245

requestMetaLib, 0x07a61a6f55d50f19c5a02788ccd4727919803805

requestScheduleLib, 0x91079d873c34074a85c252a975150ce3434233fe

requestTracker, 0x7fd72eba9298ccc17af2fe0942a7aa43bec8e04e

safeMath, 0x0e52c048ee0fcafbb1aacb69acae3f5623deaa82

schedulerLib, 0xc5d05850a753b7ee68d1465a41e36edc3b0e91fc

timestampScheduler, 0x213265a2647977ce7062836c7f78fa018bd88cc3

transactionRecorder, 0xfd12eb79c93419d1530b09f57caf768498c3243a
```

```
Kovan

baseScheduler, 0x600dd54c2df71bfb601fa1ff1d471412d6f9c45e

blockScheduler, 0xca006fbd3766885322ff1906e678dab9a528e1dc

claimLib, 0xce20333ef81e4f30bc9cebde03ee383dcae03d67

executionLib, 0x5d4148936771c2880e64b368fc06f5128128ba4f

groveLib, 0x8a9a3e77a6093c774e11e943edec85e01d0fe636

iterTools, 0x04a642bfd92a0a9f3dd7654fc5b930038bbec199

mathLib, 0x83f786fc99e738845d3ce679794d63317978b58b

paymentLib, 0xef47467a9c3acbcd610be2a45e2771f51eb39b11

requestFactory, 0x98bfd4ad0f493cc2a3e13d0b0a530a91ee2693ff

requestLib, 0x27405aa33023200df652c3ebd08617ff6e2699a5

requestMetaLib, 0xfaebe12d4d9726704bb8dc0c4f53b30b74ca0acc

requestScheduleLib, 0x98e097a61a0e261b706175b0e3397cb606c3face

requestTracker, 0x59fe33bfa4d82ffbf1cc76f22eff55ea5685c177

safeMath, 0x65aebbb6ede22c421ab2c795d83a77f3fe77567c

schedulerLib, 0xfe14564feb06d19a658b6cb2438efca16247969d

timestampScheduler, 0xa8b4c1fde4436c7c837566ff81c39bf36e1c0873

transactionRecorder, 0x07cf8fbf6c5715c101d98cdb698fd9eed77ff526
```