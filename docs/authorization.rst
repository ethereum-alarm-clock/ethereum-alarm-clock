Authorization
=============

Scheduled calls can be considered either **authorized** or **unauthorized**.

An **authorized** call is one for which either ``scheduledBy == targetAddress``
or for which the ``scheduledBy`` address has been granted explicit
authorization by ``targetAddress`` to schedule calls.

An **unauthorized** call is one for which ``scheduledBy != targetAddress`` and
the ``scheduledBy`` address has not been granted authorization to schedule
calls.


Differentiating calls
---------------------

When the Alarm service executes calls, they will come from one of two addresses
depending on whether the call is considered **authorized** or **unauthorized**.
These addresses will sometimes be referred to as relays, as they relay the
actually function call for the Alarm service, allowing the callee to
differentiate between **authorized** and **unauthorized** calls.

.. note::

    A call's authorization state is determined at the time of execution.

The address that **authorized** calls will orignate from can be gotten from
the ``authorizedAddress`` function.

* **Soldity Function Signature:** ``authorizedAddress() returns (address)``
* **ABI Signature:** ``0x5539d400``

The address that **unauthorized** calls will orignate from can be gotten from
the ``unauthorizedAddress`` function.

* **Soldity Function Signature:** ``unauthorizedAddress() returns (address)``
* **ABI Signature:** ``0x94d2b21b``


Checking authorization status
-----------------------------

A contract can query the Alarm service for the two addresses and then compare
them to the ``msg.sender`` value.

To do this, our contract needs to be at least partially aware of the Alarm ABI function signatures which can be done easily with an abstract contract.

Consider the idea of a contract which holds onto funds until a specified future
block at which point it suicides sending all of the funds to the trustee.

.. code-block::

    contract AlarmAPI {
        function authorizedAddress() returns (address);
        function unauthorizedAddress() returns (address);
    }
    
    contract TrustFund {
        address trustee = 0x...;
        address _alarm = 0x...;

        function releaseFunds() public {
            AlarmAPI alarm = AlarmAPI(_alarm);
            if (msg.sender == alarm.authorizedAddress()) {
                suicide(trustee);
            }
        }
    }

In the above example, the ``TrustFund.releaseFunds`` function checks whether
the incoming call is from the **authorized** alarm address before suiciding and
releasing the funds.

.. note::

    It should be noted that the above example would require authorization to
    have been setup by the ``TrustFund`` contract via some mechanism like a
    contract constructor.


Managing Authorization
----------------------

It is the sole responsibility of the contract to manage address authorizations.


Granting Authorization
^^^^^^^^^^^^^^^^^^^^^^

Authorization is granted with the ``addAuthorization`` function.

* **Soldity Function Signature:** ``addAuthorization(address schedulerAddress)``
* **ABI Signature:** ``0x35b28153``

This function adds the ``schedulerAddress`` address to the authorized addresses
for ``msg.sender``.

Here is how a solidity contract could grant access to it's creator.

.. code-block::

    contract Example {
        address alarm = 0x....;

        function Example() {
            alarm.call(bytes4(sha3("addAuthorization(address)")), msg.sender);
        }
    }

Upon creation, the ``Example`` contract adds it's creator as an authorized
scheduler with the alarm service.

Checking Access
^^^^^^^^^^^^^^^

You can check whether an address has authorization to schedule calls for a
given address with the ``checkAuthorization`` function.

* **Soldity Function Signature:** ``checkAuthorization(address schedulerAddress, address contractAddress) returns (bool)``
* **ABI Signature:** ``0x685c234a``


Removing Authorization
^^^^^^^^^^^^^^^^^^^^^^

A contract can remove authorization using the ``removeAuthorization`` function.

* **Soldity Function Signature:** ``removeAuthorization(address schedulerAddress)``
* **ABI Signature:** ``0x94f3f81d``

.. code-block::

    contract MemberRoster {
        address alarm = 0x....;

        mapping (address => bool) members;

        function removeMember(address memberAddress) {
            members[memberAddress] = false;
            
            alarm.call(bytes4(sha3("removeAuthorization(address)")), memberAddress);
        }
    }

In the example above we are looking at part of a contract that manages the
membership for an organization of some sort.  Upon removing a member from the
organization, the ``MemberRoster`` contract also removes their authorization to
schedule calls.
