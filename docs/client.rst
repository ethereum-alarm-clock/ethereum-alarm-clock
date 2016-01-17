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

The scheduler requires an *unlocked* ethereum client with the JSON-RPC server
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
* When an upcoming call is found that is unclaimed, the scheduler will claim
  the call. (more on this later)
* When an upcoming scheduled call is found within the next 40 blocks it will
  print a notice that it is now tracking that call.
* When the target block is imminent (2 blocks) a notice that it is entering the
  *call loop* is logged.

Call Claiming
^^^^^^^^^^^^^

The scheduling client will claim scheduled calls.  The logic for claiming is
roughly the following.

* Let ``N`` be a number between 0 and 255 that represents the current location in
  the call's claim window.
* If the claim value at ``N`` is not at least enough to pay for the claiming
  transaction and ``N`` is less than 240 the call is ignored.
* If the call is profitable at ``N`` or ``N`` is greater than 240, a random
  number ``x`` is generated between 0 and 255.
* If ``x`` is less than ``N`` then the client will attempt to claim the call.
  Otherwise the call is ignored.


Call Execution
^^^^^^^^^^^^^^

Once the call enters the call window the client will check whether the call is claimed.  

* If the call is claimed and the current coinbase is the claiming address then the client will attempt to execute the call.
* If the call is claimed and the claiming address is not the current coinbase
  the client will wait until the call enters free-for-all mode.
* If the call is unclaimed then the client will attempt to execute it.

Once the client has sent a transaction attempting to execute the call it will
wait for the transaction receipt and no further attempts to execute the call
will be made.

Checks
^^^^^^

The client implements all of the following

* Don't claim cancelled calls
* Don't execute cancelled calls
* Don't execute calls that have already been executed.
* Don't execute calls that don't have enough ether to pay for the transaction.


Other Things You Should Know
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* The script only logs that the transaction was accepted which is not the same
  as successfully executing the call. see `issue 1`_


Running a server
----------------

The scheduler runs nicely on the smallest AWS EC2 instance size.  The following
steps should get an EC2 instance provisioned with the scheduler running.

1. Setup an EC2 Instance
^^^^^^^^^^^^^^^^^^^^^^^^

* Setup an EC2 instance running Ubuntu.  The smallest instance size works fine.
* Add an extra volume to store your blockchain data.  16GB should be sufficient
  for the near term future.
* Optionally mark this volume to persist past termination of the instance so
  that you can reuse your blockchain data.
* Make sure that the security policy leaves `30303` open to connections from
  the outside world.


2. Provision the Server
^^^^^^^^^^^^^^^^^^^^^^^

* ``sudo apt-get update --fix-missing``
* ``sudo apt-get install -y supervisor``
* ``sudo apt-get install -y python-dev python build-essential libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev python-virtualenv``

3. Mount the extra volume
^^^^^^^^^^^^^^^^^^^^^^^^^

The following comes from the `AWS Documentation`_ and will only work verbatim
if your additional volume is ``/dev/xvdb``.


* ``sudo mkfs -t ext4 /dev/xvdb``
* ``sudo mkdir -p /data``
* ``sudo mount /dev/xvdb /data``
* ``sudo mkdir -p /data/ethereum``
* ``sudo chown ubuntu /data/ethereum``

Modify `/etc/fstab` to look like the following.  This ensures the extra volume
will persist through restarts.

.. code-block:: shell

    #/etc/fstab
    LABEL=cloudimg-rootfs   /        ext4   defaults,discard        0 0
    /dev/xvdb       /data   ext4    defaults,nofail        0       2

Run ``sudo mount -a``  If you don't get any errors then you haven't borked your
``etc/fstab``

4. Install Geth
^^^^^^^^^^^^^^^

Install the go-ethereum client.

* ``sudo apt-get install -y software-properties-common``
* ``sudo add-apt-repository -y ppa:ethereum/ethereum``
* ``sudo apt-get update``
* ``sudo apt-get install -y ethereum``

5. Install the Alarm Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the Alarm client.

* ``mkdir -p ~/alarm-0.6.0``
* ``cd ~/alarm-0.6.0``
* ``virtualenv env && source env/bin/activate``
* ``pip install ethereum-alarm-clock-client``

6. Configure Supervisord
^^^^^^^^^^^^^^^^^^^^^^^^

Supervisord will be used to manage both ``geth`` and ``eth_alarm``.

Put the following in ``/etc/supervisord/conf.d/geth.conf``

.. code-block:: shell

    [program:geth]
    command=geth --datadir /data/ethereum --unlock 0 --password /home/ubuntu/geth_password --rpc --fast
    user=ubuntu
    stdout_logfile=/var/log/supervisor/geth-stdout.log
    stderr_logfile=/var/log/supervisor/geth-stderr.log


Put the following in ``/etc/supervisord/conf.d/scheduler-v6.conf``

.. code-block:: shell

    [program:scheduler-v6]
    user=ubuntu
    command=/home/ubuntu/alarm-0.6.0/env/bin/eth_alarm scheduler --client rpc --address 0xe109ecb193841af9da3110c80fdd365d1c23be2a
    directory=/home/ubuntu/alarm-0.6.0/
    environment=PATH="/home/ubuntu/alarm-0.6.0/env/bin"
    stdout_logfile=/var/log/supervisor/scheduler-v6-stdout.log
    stderr_logfile=/var/log/supervisor/scheduler-v6-stderr.log
    autorestart=true
    autostart=false


7. Generate geth account
^^^^^^^^^^^^^^^^^^^^^^^^

Use the following command to generate an account.  The ``--datadir`` argument
is important, otherwise the generated account won't be found by our geth
process being run by supervisord.

* ``$ geth --datadir /data/ethereum account new``

Place the password for that account in ``/home/ubuntu/geth_password``.

You will also need to send this account a few ether.  Twice the maximum
transaction cost should be sufficient.

8. Turn it on
^^^^^^^^^^^^^

Reload supervisord so that it finds the two new config files.

* ``sudo supervisord reload``

You'll want to wait for ``geth`` to fully sync with the network before you
start the ``scheduler-v6`` process.

9. Monitoring
^^^^^^^^^^^^^

You can monitor these two processes with ``tail``

* ``tail -f /var/log/supervisor/geth*.log``
* ``tail -f /var/log/supervisor/scheduler-v6*.log``



.. _Ethereum Alarm Clock Client: https://github.com/pipermerriam/ethereum-alarm-client
.. _pip: https://pip.pypa.io/en/stable/
.. _issue 1: https://github.com/pipermerriam/ethereum-alarm-client/issues/1
.. _AWS Documentation: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html
