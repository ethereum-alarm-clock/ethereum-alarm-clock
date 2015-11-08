Call pricing and fees
=====================

The Alarm service operates under a **scheduler pays** model, which means that
the scheduler of a call is responsible for paying for the full gas cost and
fees associated with executing the call.

These funds must be presented upfront at the time of scheduling and are held by
the call contract until execution.

Call Payment and Fees
---------------------

When a call is scheduled, the scheduler can either provide values for the
payment and fee, or leave them off in favor of using the default values.

The account which executes the scheduled call is reimbursed 100% of the gas
cost + payment for their service as well as sending the fee to the creator of
the service.

The GasPriceScalar multiplier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Both the payment and the fee are multiplied by the **GasPriceScalar**.

**GasPriceScalar** is a multiplier that ranges from 0 - 2 which is based on
the difference between the gas priced used for call execution and the gas
price used during call scheduling.  This number incentivises the call
executor to use as low a gas price as possible.

This multiplier is computed with the following formula.

* *IF* ``gasPrice > anchorGasPrice``

``anchorGasPrice / gasPrice``

* *IF* ``gasPrice <= anchorGasPrice``

``anchorGasPrice / (2 * anchorGasPrice - gasPrice)``

Where:

* **anchorGasPrice** is the ``tx.gasprice`` used when the call was scheduled.
* **gasPrice** is the ``tx.gasprice`` used to execute the call.

At the time of call execution, the ``anchorGasPrice`` has already been set, so
the only value that is variable is the ``gasPrice`` which is set by the account
executing the transaction.  Since the scheduler is the one who ends up paying
for the actual gas cost, this multiplier is designed to incentivize the caller
using the lowest gas price that can be expected to be reliably picked up and
promptly executed by miners.

Here are the values this formula produces for a ``baseGasPrice`` of 20 and a
``gasPrice`` ranging from 10 - 40;

+----------+------------+
| gasPrice | multiplier |
+==========+============+
|    15    |    1.20    |
+----------+------------+   
|    16    |    1.17    |
+----------+------------+
|    17    |    1.13    |
+----------+------------+
|    18    |    1.09    |
+----------+------------+
|    19    |    1.05    |
+----------+------------+
|    20    |    1.00    |
+----------+------------+
|    21    |    0.95    |
+----------+------------+
|    22    |    0.91    |
+----------+------------+
|    23    |    0.87    |
+----------+------------+
|    24    |    0.83    |
+----------+------------+
|    25    |    0.80    |
+----------+------------+
|    26    |    0.77    |
+----------+------------+
|    27    |    0.74    |
+----------+------------+
|    28    |    0.71    |
+----------+------------+
|    29    |    0.69    |
+----------+------------+
|    30    |    0.67    |
+----------+------------+
|    31    |    0.65    |
+----------+------------+
|    32    |    0.63    |
+----------+------------+
|    33    |    0.61    |
+----------+------------+
|    34    |    0.59    |
+----------+------------+
|    35    |    0.57    |
+----------+------------+
|    36    |    0.56    |
+----------+------------+
|    37    |    0.54    |
+----------+------------+
|    38    |    0.53    |
+----------+------------+
|    39    |    0.51    |
+----------+------------+
|    40    |    0.50    |
+----------+------------+

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

The gas overhead that you can expect to pay for your function is about 100,000
gas.
