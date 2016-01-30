Reliability
===========

One of the ways to assess the reliability of the Alarm service is to check the
Reliability Canary.  This is a contract which continually reschedules a call to
itself every 480 blocks (approximately 2 hours).  If any of these function
calls is ever missed the canary *dies*.

http://canary.ethereum-alarm-clock.com/

A dead canary means that at some point one of the calls that the canary
scheduled was not executed.
