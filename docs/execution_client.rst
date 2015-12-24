Execution Client
================

.. warning:: This tool should be considered alpha software and comes with all of the caveats and disclaimers that one might expect with early stage software.  Use at your own risk.

The easiest way to start executing calls is to use the `Ethereum Alarm Clock Client`_.

Installation can be done with `pip`_

.. code-block:: shell

    $ pip install ethereum-alarm-clock-client

Once the package is installed, a new command line tool ``eth_alarm`` should be
available.

Running the Scheduler
---------------------

The execution scheduler is a process that monitors the alarm service for
upcoming scheduled function calls and executes them at their target block.

The scheduler requires an unlocked ethereum client with the JSON-RPC server
enabled to be running on localhost.

.. code-block:: shell

    $ eth_alarm scheduler
    BLOCKSAGE: INFO: 2015-12-23 15:31:26,920 > Starting block sage
    BLOCKSAGE: INFO: 2015-12-23 15:31:38,143 > Heartbeat: block #328 : block_time: 1.90237202068
    BLOCKSAGE: INFO: 2015-12-23 15:31:43,623 > Heartbeat: block #335 : block_time: 1.75782920308
    SCHEDULER: INFO: 2015-12-23 15:31:56,415 Tracking call: 0xa4a1b0d99e5271dd236a7f2abe30f81bba67dd90
    CALL-0XA4A1B0D99E5271DD236A7F2ABE30F81BBA67DD90: INFO: 2015-12-23 15:31:56,415 Sleeping until 377
    BLOCKSAGE: INFO: 2015-12-23 15:31:58,326 > Heartbeat: block #340 : block_time: 1.89721174014
    BLOCKSAGE: INFO: 2015-12-23 15:32:06,473 > Heartbeat: block #346 : block_time: 2.07706735856
    BLOCKSAGE: INFO: 2015-12-23 15:32:12,427 > Heartbeat: block #352 : block_time: 1.78518210439
    BLOCKSAGE: INFO: 2015-12-23 15:32:24,904 > Heartbeat: block #357 : block_time: 1.67715797869
    BLOCKSAGE: INFO: 2015-12-23 15:32:32,134 > Heartbeat: block #363 : block_time: 2.02664816647
    BLOCKSAGE: INFO: 2015-12-23 15:32:41,400 > Heartbeat: block #368 : block_time: 1.70622547582
    BLOCKSAGE: INFO: 2015-12-23 15:32:48,291 > Heartbeat: block #373 : block_time: 1.59583837187
    BLOCKSAGE: INFO: 2015-12-23 15:32:53,134 > Heartbeat: block #378 : block_time: 1.51536617309
    CALL-0XA4A1B0D99E5271DD236A7F2ABE30F81BBA67DD90: INFO: 2015-12-23 15:32:55,419 Entering call loop
    CALL-0XA4A1B0D99E5271DD236A7F2ABE30F81BBA67DD90: INFO: 2015-12-23 15:32:55,452 Attempting to execute call
    CALL-0XA4A1B0D99E5271DD236A7F2ABE30F81BBA67DD90: INFO: 2015-12-23 15:32:59,473 Transaction accepted.


* The process will log a *heartbeat* every 4 blocks (1 minute). 
* When an upcoming scheduled call is found within the next 40 blocks it will
  print a notice that it is now tracking that call.
* When the target block is imminent (2 blocks) a notice that it is entering the
  *call loop* is logged.


Other Things You Should Know
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* The script only logs that the transaction was accepted which is not the same
  as successfully executing the call. see `issue 1`_
* The script doesn't *claim* the calls. see `issue 2`_

.. _Ethereum Alarm Clock Client: https://github.com/pipermerriam/ethereum-alarm-client
.. _pip: https://pip.pypa.io/en/stable/
.. _issue 1: https://github.com/pipermerriam/ethereum-alarm-client/issues/1
.. _issue 2: https://github.com/pipermerriam/ethereum-alarm-client/issues/2
