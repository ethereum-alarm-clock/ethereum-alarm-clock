# Ethereum Alarm Clock

[![Join the chat at https://gitter.im/ethereum-alarm-clock/ethereum-alarm-clock](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ethereum-alarm-clock/ethereum-alarm-clock?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/ethereum-alarm-clock/ethereum-alarm-clock.svg?branch=master)](https://travis-ci.org/chronologic/ethereum-alarm-clock)
[![Documentation Status](https://readthedocs.org/projects/ethereum-alarm-clock/badge/?version=latest)](http://ethereum-alarm-clock.readthedocs.io/en/latest/?badge=latest) [![Greenkeeper badge](https://badges.greenkeeper.io/ethereum-alarm-clock/ethereum-alarm-clock.svg)](https://greenkeeper.io/)


__Homepage:__ [Ethereum Alarm Clock](http://www.ethereum-alarm-clock.com/)

__Looking to download the DApp?__: [Latest Releases](https://github.com/chronologic/eth-alarm-clock-dapp/releases)

## What is the EAC (Ethereum Alarm Clock)

The Ethereum Alarm Clock is a smart contract protocol for scheduling Ethereum transactions 
to be executed in the future. It allows any address to set the parameters of a transaction and 
allow executors (known as _TimeNodes_) to call these transactions during the desired window. 
The EAC is agnostic to callers so can be used by both human users and other smart contracts. 
Since all of the scheduling logic is contained in smart contracts, transactions can be scheduled 
from solidity, and developers can rely on it as a core piece of their smart contract of decentralized application.

Additionally the EAC faciliates the execution of this pool of scheduled transactions through the TimeNode. 
The EAC TimeNode continuously runs and watches for transactions which are scheduled to be executed soon 
then claims and later executes them. For the EAC to be successful it depends on users to run TimeNodes. 
There are a few ways incentives for running these TimeNodes are baked in to the protocol itself via the claiming
mechanism and the bounty payout.

See [here](https://blog.chronologic.network/how-to-prove-day-ownership-to-be-a-timenode-3dc1333c74ef) for more information about how to run a TimeNode.

## Documentation

Documentation can be found on [Read the Docs](https://ethereum-alarm-clock.readthedocs.io/en/latest/).

We are in progress of migrating the documentation to the [Wiki](https://github.com/ethereum-alarm-clock/ethereum-alarm-clock/wiki).

## Deployment

Deployed version is [`1.0.0-rc.2`](https://github.com/ethereum-alarm-clock/ethereum-alarm-clock/releases/tag/v1.0.0-rc.2)

You can find the address for each network in the [networks](https://github.com/ethereum-alarm-clock/ethereum-alarm-clock/tree/master/networks/) folder. 

## Using the CLI

Please see the [`cli`](https://github.com/ethereum-alarm-clock/cli) repository for the commandline client.

## Running the tests

Please ensure you are using node version _at least_ 8.0.0 and have truffle and ganache-cli installed.

```
nvm use lts/carbon
npm i
npm i -g truffle@4.1.14 
npm i -g ganache-cli
```

Start ganache-cli in a terminal screen by running `ganache-cli`.

In another terminal screen run `npm test` at the root of the directory. This will run the npm test script that 
splits up the tests into different runtimes. The tests are split because the EAC is a moderately sized project and 
running all the tests with one command has a tendency to break down the ganache tester chain.

Each time you run the tests it is advised to rebuild your build/ folder, as this may lead to bugs if not done. You 
can do this by running the command `rm -rf build/`.

## Thanks and support
[<img src="https://s3.amazonaws.com/chronologic.network/ChronoLogic_logo.svg" width="128px">](https://github.com/chronologic)
