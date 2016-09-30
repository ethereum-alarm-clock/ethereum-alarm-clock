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

    TODO: `help` output from the main command


Setting up an 





.. _pyethereum documentation: https://github.com/ethereum/pyethereum/wiki/Developer-Notes


Rollbar Integration
-------------------

TODO


Running a server
----------------

TODO: update this.

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
* ``sudo apt-get install -y python3-dev python build-essential libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev python-virtualenv``

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
