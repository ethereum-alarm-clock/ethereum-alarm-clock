import functools
import random

import gevent

from ..utils import task


def locked_txn_request(fn):
    """
    This decorator ensures that no two greenlets are able to work on the same
    request at the same time.
    """
    @functools.wraps(fn)
    def inner(config, txn_request):
        logger = config.get_logger(txn_request.address)

        logger.debug("Acquiring lock for: %s", txn_request.address)
        with config.lock(txn_request.address):
            logger.debug("Acquired lock for: %s", txn_request.address)
            return_value = fn(config, txn_request)
        logger.debug("Released lock for: %s", txn_request.address)
        return return_value

    return inner


@task
@locked_txn_request
def handle_transaction_request(config, txn_request):
    logger = config.get_logger(txn_request.address)

    # Early exit conditions
    # - cancelled
    # - before claim window
    # - in freeze window
    if txn_request.isCancelled:
        logger.debug("Ignoring Cancelled Request")
        return
    elif txn_request.beforeClaimWindow:
        logger.debug(
            "Ignoring Pending Request.  Now: %s | Claimable At: %s",
            txn_request.now,
            txn_request.claimWindowStart,
        )
        return
    elif txn_request.inClaimWindow:
        logger.debug(
            "Spawning `claim_txn_request`",
            txn_request.address,
        )
        gevent.spawn(claim_txn_request, config, txn_request)
    elif txn_request.inFreezePeriod:
        logger.debug(
            "Ignoring Frozen Request.  Now: %s | Window Start: %s",
            txn_request.now,
            txn_request.windowStart,
        )
        return
    elif txn_request.inExecutionWindow:
        logger.debug("Spawning `execute_txn_request`")
        gevent.spawn(execute_txn_request, config, txn_request)
    elif txn_request.afterExecutionWindow:
        logger.debug("Spawning `cleanup_txn_request`")
        gevent.spawn(cleanup_txn_request, config, txn_request)


@task
@locked_txn_request
def claim_txn_request(config, txn_request):
    logger = config.get_logger(txn_request.address)

    web3 = config.web3
    wait = config.wait

    if txn_request.isCancelled:
        logger.debug("Not Claiming Cancelled Request")
        return
    elif not txn_request.inClaimWindow:
        logger.debug(
            "Not in claim window.  Now: %s | Claim Window Start: %s",
            txn_request.now,
            txn_request.claimWindowStart,
        )
        return
    elif txn_request.isClaimed:
        logger.debug("Already claimed by: %s", txn_request.claimedBy)
        return

    payment_if_claimed = (
        txn_request.payment *
        txn_request.paymentModifier *
        txn_request.claimPaymentModifier
    ) // 100 // 100
    claim_deposit = 2 * txn_request.payment
    gas_to_claim = txn_request.estimateGas({'value': claim_deposit}).claim()
    gas_cost_to_claim = web3.eth.gasPrice * gas_to_claim

    if gas_cost_to_claim > payment_if_claimed:
        logger.debug(
            "Claim gas cost greater than payment. Claim Gas Cost: %s | Current "
            "Payment: %s",
            gas_cost_to_claim,
            payment_if_claimed,
        )
        return

    claim_dice_roll = random.random() * 100
    if claim_dice_roll >= txn_request.claimPaymentModifier:
        logger.debug(
            "Waiting longer to claim.  Rolled %s.  Needed at least %s",
            claim_dice_roll,
            txn_request.claimPaymentModifier,
        )

    logger.info(
        "Attempting to claim.  Payment: %s | PaymentModifier: %s | "
        "Gas Cost %s | Projected Profit: %s",
        payment_if_claimed,
        txn_request.claimPaymentModifier,
        gas_cost_to_claim,
        payment_if_claimed - gas_cost_to_claim,
    )
    claim_txn_hash = txn_request.transact({'value': claim_deposit}).claim()
    logger.info("Sent claim transaction.  Txn Hash: %s", claim_txn_hash)
    try:
        wait.for_receipt(claim_txn_hash, poll_interval=5)
    except gevent.Timeout:
        logger.error(
            "Timed out waiting for claim transaction receipt. Txn Hash: %s",
            claim_txn_hash,
        )
        return

    if not txn_request.isClaimed:
        logger.error(
            "Request unexpectedly not unclaimed.  Was claimed via txn: %s",
            claim_txn_hash,
        )
    elif not txn_request.isClaimedBy(web3.eth.defaultAccount):
        logger.error("Got beaten to claim by %s", txn_request.claimedBy)
    else:
        logger.info("Successfully claimed")


@task
@locked_txn_request
def execute_txn_request(config, txn_request):
    web3 = config.web3
    wait = config.wait
    request_lib = config.request_lib
    logger = config.get_logger(txn_request.address)

    if txn_request.wasCalled:
        logger.debug("Already called.")
        return
    elif txn_request.isCancelled:
        logger.debug("Cancelled.")
        return
    elif not txn_request.inExecutionWindow:
        logger.debug("Outside of execution window")
        return
    elif txn_request.inReservedWindow and not txn_request.isClaimedBy(web3.eth.defaultAccount):
        logger.debug(
            "In reserved window and claimed by: %s",
            txn_request.claimedBy,
        )
        return

    # Since we are directly executing the request we don't need to include the
    # stack depth checking gas here.
    execute_gas = txn_request.callGas + request_lib.call().EXECUTION_GAS_OVERHEAD()
    gas_limit = web3.eth.getBlock('latest')['gasLimit']

    if execute_gas > gas_limit:
        logger.error(
            "Execution gas above network gas limit.  Computed Execution Gas: %s "
            "| Network gas limit: %s",
            execute_gas,
            gas_limit,
        )
        return

    logger.info(
        "Attempting execution.  Now: %s | windowStart: %s | "
        "expectedPayment: %s | claimedBy: %s | inReservedWindow: %s",
        txn_request.now,
        txn_request.windowStart,
        txn_request.payment * txn_request.paymentModifier // 100,
        txn_request.claimedBy,
        "Yes" if txn_request.inReservedWindow else "No",
    )

    execute_txn_hash = txn_request.transact({'gas': execute_gas}).execute()

    try:
        logger.info("Waiting for transaction to be mined...")
        wait.for_receipt(execute_txn_hash, poll_interval=5)
        logger.info("Execution transaction mined.")
    except gevent.Timeout:
        logger.error(
            "Timed out waiting for execution transaction receipt. Txn Hash: %s",
            execute_txn_hash,
        )

    if txn_request.wasCalled:
        logger.info("Request is now Executed")
    else:
        logger.error("Request was not Executed")


@task
@locked_txn_request
def cleanup_txn_request(config, txn_request):
    web3 = config.web3
    wait = config.wait
    logger = config.get_logger(txn_request.address)

    # TODO: handle executing the payment/donation/ownerether methods too.
    if not txn_request.afterExecutionWindow:
        logger.debug("Not after window")
        return
    elif txn_request.isCancelled:
        logger.debug("Cancelled")
        return
    elif txn_request.wasCalled:
        logger.debug("Already executed")
        return

    if web3.eth.getBalance(txn_request.address) == 0:
        logger.debug("No ether left in contract")
        return

    if txn_request.owner != web3.eth.defaultAccount:
        gas_to_cancel = txn_request.estimateGas().cancel()
        gas_cost_to_cancel = gas_to_cancel * web3.eth.gasPrice

        if gas_cost_to_cancel > web3.eth.getBalance(txn_request.address):
            logger.debug("Not enough ether to cover cost of cancelling")
            return

    logger.info("Attempting cancellation.")

    cancel_txn_hash = txn_request.transact().cancel()

    try:
        logger.info("Waiting for transaction to be mined...")
        wait.for_receipt(cancel_txn_hash, poll_interval=5)
        logger.info("Cancellation transaction mined.")
    except gevent.Timeout:
        logger.error(
            "Timed out waiting for cancellation transaction receipt. Txn Hash: %s",
            cancel_txn_hash,
        )

    if txn_request.isCancelled:
        logger.info("Request is now cancelled")
    else:
        logger.error("Request was not cancelled")
