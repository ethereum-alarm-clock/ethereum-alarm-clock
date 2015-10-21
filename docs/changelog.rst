Changelog
=========

0.4.0
-----

- Convert Alarm service to use library contracts for all functionality.
- CallerPool contract API is now integrated into the Alarm API


0.3.0
-----

- Convert Alarm service to use `Grove`_ for tracking scheduled call ordering.
- Enable logging most notable Alarm service events.
- Two additional convenience functions for invoking ``scheduleCall`` with
  **gracePeriod** and **nonce** as optional parameters.


0.2.0
-----

- Fix for `Issue 42`_.  Make the free-for-all bond bonus restrict itself to the
  correct set of callers.
- Re-enable the right tree rotation in favor of removing three ``getLastX``
  function.  This is related to the pi-million gas limit which is restricting
  the code size of the contract.


0.1.0
-----

- Initial release.


.. _Issue 42: https://github.com/pipermerriam/ethereum-alarm-clock/issues/42
.. _Grove: https://github.com/pipermerriam/ethereum-grove
