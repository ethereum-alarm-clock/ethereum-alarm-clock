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

If you would like to run the test please set up your environment to use node v8 (lts/carbon), truffle v4.1.5 and the latest ganache-cli.

```
nvm use lts/carbon
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

We are in progress of migrating the documentation to the [Wiki](https://github.com/ethereum-alarm-clock/ethereum-alarm-clock/wiki).

## Using the CLI

Please see the [`cli`](https://github.com/ethereum-alarm-clock/cli) repository for the commandline client.

## Deployment

The EAC contracts are deployed on both the Kovan and Ropsten testnets at the addresses below.

Deployed version is [`0.9.3`](https://github.com/ethereum-alarm-clock/ethereum-alarm-clock/releases/tag/0.9.3)

```
Kovan

baseScheduler, 0x36223956a45f658cc7ac4f2c4150bcfad49e6a4b

blockScheduler, 0x1afc19a7e642761ba2b55d2a45b32c7ef08269d1

claimLib, 0xbfee9c0d041a7ce6357959b5de7a336dc72e6125

executionLib, 0xb23658842939e581b77245e0032ebac83dba9e57

groveLib, 0x4afe44930813599f3a111f335c844dc4a4e9a9c3

iterTools, 0x5e41e026615941b2bfdb696d1d1f910fa1d6f02d

mathLib, 0x147d8962f12dfbaada00c78db9c5f07df536500b

paymentLib, 0x64906a8b50da07ca19c0ec145b933fa0500c7378

requestFactory, 0x496e2b6089bde77293a994469b08e9f266d87adb

requestLib, 0xea74036bab068b83e34233d15b63c50e7edb0f7a

requestMetaLib, 0x013fbac1dfe24ad664419a8a1eb808bfd7e525d6

requestScheduleLib, 0xb6289ea1995af2d58f56410567477c61f2f301c3

requestTracker, 0xc3e310aa664ecc155bec79750400586e87738a75

safeMath, 0xee2eb5b9658403034f2cac4652c1d10d4fd3eb2d

schedulerLib, 0x27a5c2cf457b8457e82887fd793b6dc5d9c45abd

timestampScheduler, 0xc6370807f0164bdf10a66c08d0dab1028dbe80a3

transactionRequestCore, 0x4b500c814add8768cd85de4ac43a15995f5b3663

transactionRecorder, 0x80d8b7ddbd266b8f9113d9e4b017827c3029fcb9
```

```
Ropsten

baseScheduler, 0x94291c81a79215cb24457645f48b6e46530d10f7

blockScheduler, 0x4b2cbd698aac423b85dada9c7892b7d8678a1654

claimLib, 0xfc5f42ce6ef6396e538ca8ca22a384fb2d212aee

executionLib, 0xb743e1b53d0bac077210c112b2f164b86cd750cf

groveLib, 0xa427b12fdcbc457342982de74de997282bb798b4

iterTools, 0x82d3ec44de773b36abea3e6fcd5f0be8097bc464

mathLib, 0x6745cad06c2716d4fbf75203753410b1b0deeebf

paymentLib, 0x86bf89d7c9c8f4607127fb8e9398b0c33cdc83e1

requestFactory, 0xc9498985739bd7451f3fd3f5774708aa7bda0f5b

requestLib, 0x85ccad322b326bca0a61c80ffef60dfcc13b5bb3

requestMetaLib, 0x9708fc0aeceaaea0cd1c28e1d5fe4f69eec5213e

requestScheduleLib, 0x9e286151b85d8e5f684001b3499707d04425e3c9

requestTracker, 0xa6e27f575d1460c93cf38879820d711b7367cc6d

safeMath, 0x17c935a24c43cf8e48cd2b1fad4a2e3b342208ec

schedulerLib, 0x15b73e1784fcd8b54a381d99f78e414b4e191268

timestampScheduler, 0x9e93c8a1a2abc7f55a51bc088286e70644a22226

transactionRequestCore, 0xdc4fa890d1f0320fd51812a246e0d8b5fd9ad319

transactionRecorder, 0x28ed44268658496715b4229aab6d3edc1e819701
```

## Thanks and support
[<img src="https://s3.amazonaws.com/chronologic.network/ChronoLogic_logo.svg" width="128px">](https://github.com/chronologic)
