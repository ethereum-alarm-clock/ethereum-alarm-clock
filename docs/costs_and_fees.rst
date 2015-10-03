Call pricing and fees
=====================

The Alarm service operates under a **scheduler pays** model, which means that
the scheduler of a call is responsible for paying for the full gas cost and
fees associated with executing the call.

This payment is automatic and happens during the course of the execution of the scheduled call.

Minimum Balance
---------------

In order to guarantee reimbursment of gas costs and payment to the account
which executes the scheduled call, the scheduler of the call must have an
account balance sufficient to pay for the call at the time of execution.
Since, it is unknown how much gas the call will consume the Alarm service
requires a minimum balance equal to the maximum possible transaction cost plus
fees.

Call Fees and Caller Payment
----------------------------

The account which executes the scheduled call is reimbursed 100% of the gas
cost + payment for their service.  The creator of the Alarm service is also
paid the same payment.

The payment value is computed with the formula ``1% of GasUsed * BaseGasPrice *
GasPriceScalar`` where:

* **GasUsed:** is the total gas consumption for the call execution.  This
  includes all of the gas used by the Alarm service to do things like looking
  up call data, checking for sufficient account balance to pay for the call,
  paying the caller, etc.
* **BaseGasPrice** is the gas price that was used by the scheduler when they
  scheduled the function call.
* **GasPriceScalar** is a multiplier that ranges from 0 - 2 which is based on
  the difference between the gas priced used for call execution and the gas
  price used during call scheduling.  This number incentivises the call
  executor to use as low a gas price as possible.

The GasPriceScalar multiplier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This multiplier is computed with the following formula.

* *IF* ``gasPrice > baseGasPrice``

``baseGasPrice / gasPrice``

* *IF* ``gasPrice <= baseGasPrice``

``baseGasPrice / (2 * baseGasPrice - gasPrice)``

Where:

* **baseGasPrice** is the ``tx.gasprice`` used when the call was scheduled.
* **gasPrice** is the ``tx.gasprice`` used to execute the call.

At the time of call execution, the ``baseGasPrice`` has already been set, so
the only value that is variable is the ``gasPrice`` which is set by the account
executing the transaction.  Since the scheduler is the one who ends up paying
for the actual gas cost, this multiplier is designed to incentivize the caller
using the lowest gas price that can be expected to be reliably picked up and
promptly executed by miners.

Here are the values this formula produces for a ``baseGasPrice`` of 20 and a
``gasPrice`` ranging from 10 - 40 which uses 5000 gas;

+----------+------------+--------+
| gasPrice | multiplier | payout |
+==========+============+========+
|    15    |    1.20    |   120  |
+----------+------------+--------+   
|    16    |    1.17    |   117  |
+----------+------------+--------+
|    17    |    1.13    |   113  |
+----------+------------+--------+
|    18    |    1.09    |   109  |
+----------+------------+--------+
|    19    |    1.05    |   105  |
+----------+------------+--------+
|    20    |    1.00    |   100  |
+----------+------------+--------+
|    21    |    0.95    |   95   |
+----------+------------+--------+
|    22    |    0.91    |   91   |
+----------+------------+--------+
|    23    |    0.87    |   87   |
+----------+------------+--------+
|    24    |    0.83    |   83   |
+----------+------------+--------+
|    25    |    0.80    |   80   |
+----------+------------+--------+
|    26    |    0.77    |   77   |
+----------+------------+--------+
|    27    |    0.74    |   74   |
+----------+------------+--------+
|    28    |    0.71    |   71   |
+----------+------------+--------+
|    29    |    0.69    |   69   |
+----------+------------+--------+
|    30    |    0.67    |   67   |
+----------+------------+--------+
|    31    |    0.65    |   65   |
+----------+------------+--------+
|    32    |    0.63    |   63   |
+----------+------------+--------+
|    33    |    0.61    |   61   |
+----------+------------+--------+
|    34    |    0.59    |   59   |
+----------+------------+--------+
|    35    |    0.57    |   57   |
+----------+------------+--------+
|    36    |    0.56    |   56   |
+----------+------------+--------+
|    37    |    0.54    |   54   |
+----------+------------+--------+
|    38    |    0.53    |   53   |
+----------+------------+--------+
|    39    |    0.51    |   51   |
+----------+------------+--------+
|    40    |    0.50    |   50   |
+----------+------------+--------+

You can see from this table that as the ``gasPrice`` for the executing
transaction increases, the total payout for executing the call decreases.  This
provides a strong incentive for the entity executing the transaction to use a
reasonably low value.

Alternatively, if the ``gasPrice`` is set too low (potentially attempting to
maximize payout) and the call is not picked up by miners in a reasonable amount
of time, then the entity executing the call will not get paid at all.  This
provides a strong incentive to provide a value high enough to ensure the
transaction will be executed.

Overhead
--------

The gas overhead that you can expect to pay for your function call is
approximately 146287.
