CLI Interface
=============

.. contents:: :local:

The alarm service ships with a command line interface that can be used to
interact with the service in various ways.


Requirements
------------

The ``ethereum-alarm-clock-client`` python package requires some system
dependencies to install.  Please see the `pyethereum documentation`_ for more
information on how to install these.

This package is only tested against Python 3.5.  It may work on other versions
but they are explicitely not supported.

This package is only tested on unix based platforms (OSX and Linux).  It may
work on other platforms but they are explicitely not supported.


Installation
------------

The ``ethereum-alarm-clock-client`` package can be installed using ``pip`` like this.

.. code-block:: bash

    $ pip install ethereum-alarm-clock-client

Or directly from source like this.

.. code-block:: bash

    $ python setup.py install

If you are planning on modifying the code or developing a new feature you
should instead install like this.

.. code-block:: bash

    $ python setup.py develop


The ``eth_alarm`` executable
----------------------------

Once you've installed the package you should have the ``eth_alarm`` executable
available on your command line.


.. code-block:: bash

    $ eth_alarm
    Usage: eth_alarm [OPTIONS] COMMAND [ARGS]...

    Options:
      -t, --tracker-address TEXT      The address of the RequestTracker contract
                                      that should be used.
      -f, --factory-address TEXT      The address of the RequestFactory contract
                                      that should be used.
      --payment-lib-address TEXT      The address of the PaymentLib contract that
                                      should be used.
      -r, --request-lib-address TEXT  The address of the RequestLib contract that
                                      should be used.
      -l, --log-level INTEGER         Integer logging level - 10:DEBUG 20:INFO
                                      30:WARNING 40:ERROR
      -p, --provider TEXT             Web3.py provider type to use to connect to
                                      the chain.  Supported values are 'rpc',
                                      'ipc', or any dot-separated python path to a
                                      web3 provider class
      --ipc-path TEXT                 Path to the IPC socket that the IPCProvider
                                      will connect to.
      --rpc-host TEXT                 Hostname or IP address of the RPC server
      --rpc-port INTEGER              The port to use when connecting to the RPC
                                      server
      -a, --compiled-assets-path PATH
                                      Path to JSON file which contains the
                                      compiled contract assets
      --back-scan-seconds INTEGER     Number of seconds to scan into the past for
                                      timestamp based calls
      --forward-scan-seconds INTEGER  Number of seconds to scan into the future
                                      for timestamp based calls
      --back-scan-blocks INTEGER      Number of blocks to scan into the past for
                                      block based calls
      --forward-scan-blocks INTEGER   Number of blocks to scan into the future for
                                      block based calls
      --help                          Show this message and exit.

    Commands:
      client:monitor  Scan the blockchain for events from the alarm...
      client:run
      repl            Drop into a debugger shell with most of what...
      request:create  Schedule a transaction to be executed at a...






Rollbar Integration
^^^^^^^^^^^^^^^^^^^

Monitoring these sorts of things can be difficult.  I am a big fan of the
`rollbar`_ service which provides what I feel is a very solid monitoring and
log management solution.

To enable rollbar logging with the ``eth_alarm`` client you'll need to do the
following.

1. Install the python rollbar package.
   * ``$ pip install rollbar``
2. Run ``eth_alarm`` with the following environment variables set.
   * ``ROLLBAR_SECRET`` set to the *server side* token that rollbar provides.
   * ``ROLLBAR_ENVIRONMENT`` set to a string such as `'production'` or `'ec2-instance-abcdefg'``.


Running a server
----------------

The scheduler runs nicely on the *small* AWS EC2 instance size.  The following
steps should get an EC2 instance provisioned with the scheduler running.

1. Setup an EC2 Instance
^^^^^^^^^^^^^^^^^^^^^^^^

* Setup an EC2 instance running Ubuntu.  The smallest instance size works fine.
* Add an extra volume to store your blockchain data.  20GB should be sufficient
  for a short while (after April 2017) if storing the entire history,
  block-for-block, is not required.  Otherwise, a much larger size should be
  used.
* Optionally mark this volume to persist past termination of the instance so
  that you can reuse your blockchain data.
* Make sure that the security policy leaves `30303` open to connections from
  the outside world.


2. Provision the Server
^^^^^^^^^^^^^^^^^^^^^^^

* ``sudo apt-get update --fix-missing``
* ``sudo apt-get install -y supervisor``
* ``sudo apt-get install -y python3-dev python build-essential libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev python-virtualenv libffi-dev autoconf``

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


4. Install Geth or Parity
^^^^^^^^^^^^^^^^^^^^^^^^^

Install the go-ethereum client.

* ``sudo apt-get install -y software-properties-common``
* ``sudo add-apt-repository -y ppa:ethereum/ethereum``
* ``sudo apt-get update``
* ``sudo apt-get install -y ethereum``


or install the parity client.

* ``bash <(curl https://get.parity.io -Lk)``


5. Install the Alarm Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the Alarm client.

* ``mkdir -p ~/alarm-0.8.0``
* ``cd ~/alarm-0.8.0``
* ``virtualenv -p /usr/bin/python3.5 env && source env/bin/activate``
* ``pip install setuptools --upgrade``
* ``pip install ethereum-alarm-clock-client==8.0.0b1``


6. Configure Supervisord
^^^^^^^^^^^^^^^^^^^^^^^^

Supervisord will be used to manage both ``geth`` and ``eth_alarm``.

If you are using Go-Ethereum, put the following in ``/etc/supervisord/conf.d/geth.conf``

.. code-block:: shell

    [program:geth]
    command=geth --datadir /data/ethereum --unlock 0 --password /home/ubuntu/scheduler_password --fast
    user=ubuntu
    stdout_logfile=/var/log/supervisor/geth-stdout.log
    stderr_logfile=/var/log/supervisor/geth-stderr.log
    autorestart=true
    autostart=false

and the following in ``/etc/supervisord/conf.d/scheduler-v8.conf``

.. code-block:: shell

    [program:scheduler-v8]
    user=ubuntu
    command=/home/ubuntu/alarm-0.8.0/env/bin/eth_alarm --ipc-path /data/ethereum/geth.ipc client:run
    directory=/home/ubuntu/alarm-0.8.0/
    environment=PATH="/home/ubuntu/alarm-0.8.0/env/bin"
    stdout_logfile=/var/log/supervisor/scheduler-v8-stdout.log
    stderr_logfile=/var/log/supervisor/scheduler-v8-stderr.log
    autorestart=true
    autostart=false

If you are using Parity, put the following in ``/etc/supervisord/conf.d/parity.conf``

.. code-block:: shell

    [program:parity]
    command=parity --db-path /data/ethereum --unlock <your-account-address> --password /home/ubuntu/scheduler_password
    user=ubuntu
    stdout_logfile=/var/log/supervisor/parity-stdout.log
    stderr_logfile=/var/log/supervisor/parity-stderr.log
    autorestart=true
    autostart=false

and the following in ``/etc/supervisord/conf.d/scheduler-v8.conf``

.. code-block:: shell

    [program:scheduler-v8]
    user=ubuntu
    command=/home/ubuntu/alarm-0.8.0/env/bin/eth_alarm --ipc-path /home/ubuntu/.parity/jsonrpc.ipc client:run
    directory=/home/ubuntu/alarm-0.8.0/
    environment=PATH="/home/ubuntu/alarm-0.8.0/env/bin"
    stdout_logfile=/var/log/supervisor/scheduler-v8-stdout.log
    stderr_logfile=/var/log/supervisor/scheduler-v8-stderr.log
    autorestart=true
    autostart=false


7. Generate an account
^^^^^^^^^^^^^^^^^^^^^^

For Go-Ethereum

* ``$ geth --datadir /data/ethereum account new``

For parity

* ``$ parity account new``

Place the password for that account in ``/home/ubuntu/scheduler_password``.

You will also need to send this account a few ether.  A few times the maximum
transaction cost should be sufficient as this account should always trend
upwards as it executes requests and receives payment for them.

Don't forget to back up the key file! Go-Ethereum should have put it in

* ``/data/ethereum/keystore/``

and Parity in

* ``/home/ubuntu/.local/share/io.parity.ethereum/keys/``

8. Turn it on
^^^^^^^^^^^^^

Reload supervisord so that it finds the two new config files.

* ``sudo supervisord reload``

You'll want to wait for Go-Ethereum or Parity to fully sync with the network
before you start the ``scheduler-v8`` process.

9. Monitoring
^^^^^^^^^^^^^

You can monitor these processes with ``tail``

* ``tail -f /var/log/supervisor/geth*.log``
* ``tail -f /var/log/supervisor/parity*.log``
* ``tail -f /var/log/supervisor/scheduler-v8*.log``


10. System Clock
^^^^^^^^^^^^^^^^

You might want to add the following line to your crontab.  This keeps your
system clock up to date.  I've had issues with my servers *drifting*.


.. code-block:: shell

    0 0 * * * /usr/sbin/ntpdate ntp.ubuntu.com



.. _pip: https://pip.pypa.io/en/stable/
.. _rollbar: https://rollbar.com/
.. _AWS Documentation: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html
.. _pyethereum documentation: https://github.com/ethereum/pyethereum/wiki/Developer-Notes
