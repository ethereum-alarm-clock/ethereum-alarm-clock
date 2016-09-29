import functools
import random

import gevent


def locked_txn_request(fn):
    """
    This decorator ensures that no two greenlets are able to work on the same
    request at the same time.
    """
    @functools.wraps(fn)
    def inner(config, txn_request):
        lock_key = 'txn-request:{0}'.format(txn_request.address)

        config.logger.debug("Acquiring lock for: %s", lock_key)
        with config.lock(lock_key):
            config.logger.debug("Acquired lock for: %s", lock_key)
            return fn(config, txn_request)
        config.logger.debug("Released lock for: %s", lock_key)

    return inner


@locked_txn_request
def handle_transaction_request(config, txn_request):
    config.logger.debug("Entering `handle_transaction_request`")

    # Early exit conditions
    # - cancelled
    # - before claim window
    # - in freeze window
    if txn_request.isCancelled:
        config.logger.debug("Ignoring Cancelled Request @ %s", txn_request.address)
        return
    elif txn_request.beforeClaimWindow:
        config.logger.debug(
            "Ignoring Pending Request @ %s.  Currently %s.  Not claimable till %s",
            txn_request.address,
            txn_request.now,
            txn_request.claimWindowStart,
        )
        return
    elif txn_request.inClaimWindow:
        config.logger.debug(
            "Spawning `claim_txn_request` for Request @ %s",
            txn_request.address,
        )
        gevent.spawn(claim_txn_request, config, txn_request)
    elif txn_request.inFreezePeriod:
        config.logger.debug("Ignoring Frozen Request @ %s", txn_request.address)
        return
    elif txn_request.inExecutionWindow:
        config.logger.debug(
            "Spawning `execute_txn_request` for Request @ %s",
            txn_request.address,
        )
        gevent.spawn(execute_txn_request, config, txn_request)
    elif txn_request.afterExecutionWindow:
        config.logger.debug(
            "Spawning `cleanup_txn_request` for Request @ %s",
            txn_request.address,
        )
        gevent.spawn(cleanup_txn_request, config, txn_request)

    config.logger.debug("Exiting `handle_transaction_request`")


@locked_txn_request
def claim_txn_request(config, txn_request):
    config.logger.debug("Entering `claim_txn_request`")

    web3 = config.web3
    wait = config.wait

    if txn_request.isCancelled:
        config.logger.debug(
            "Claim Abort for Request @ %s.  Reason: Cancelled",
            txn_request.address,
        )
        return
    elif not txn_request.inClaimWindow:
        config.logger.debug(
            "Claim Abort for Request @ %s.  Reason: Not in claim window",
            txn_request.address,
        )
        return
    elif txn_request.isClaimed:
        config.logger.debug(
            "Claim Abort for Request @ %s.  Reason: already claimed by: %s",
            txn_request.address,
            txn_request.claimedBy,
        )
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
        config.logger.debug(
            "Waiting to claim request @ %s.  Claim gas cost greater than "
            "payment. Claim Gas: %s | Current Payment: %s",
            txn_request.address,
            gas_cost_to_claim,
            payment_if_claimed,
        )
        return

    claim_dice_roll = random.random() * 100
    if claim_dice_roll >= txn_request.claimPaymentModifier:
        config.logger.debug(
            "Waiting to claim request @ %s.  Rolled %s.  Needed at least %s",
            txn_request.address,
            claim_dice_roll,
            txn_request.claimPaymentModifier,
        )

    config.logger.info(
        "Attempting to claim request @ %s.  Payment: %s | PaymentModifier: %s | "
        "Gas Cost %s | Projected Profit: %s",
        txn_request.address,
        payment_if_claimed,
        txn_request.claimPaymentModifier,
        gas_cost_to_claim,
        payment_if_claimed - gas_cost_to_claim,
    )
    claim_txn_hash = txn_request.transact({'value': claim_deposit}).claim()
    config.logger.info(
        "Sent claim transaction for request @ %s.  Txn Hash: %s",
        txn_request.address,
        claim_txn_hash,
    )
    try:
        wait.for_receipt(claim_txn_hash)
    except gevent.Timeout:
        config.logger.error(
            "Timed out waiting for claim transaction receipt for request @ %s. "
            "Txn Hash: %s",
            txn_request.address,
            claim_txn_hash,
        )
        return

    if not txn_request.isClaimed:
        config.logger.error(
            "Request @ %s unexpectedly unclaimed.",
            txn_request.address,
        )
    elif not txn_request.isClaimedBy(web3.eth.defaultAccount):
        config.logger.error(
            "Request @ %s got claimed by %s",
            txn_request.address,
            txn_request.claimedBy,
        )
    else:
        config.logger.info(
            "Successfully claimed request @ %s",
            txn_request.address,
        )


ABORTED_REASON_MAP = {
    0: "WasCancelled",
    1: "AlreadyCalled",
    2: "BeforeCallWindow",
    3: "AfterCallWindow",
    4: "ReservedForClaimer",
    5: "StackTooDeep",
    6: "InsufficientGas",
}


@locked_txn_request
def execute_txn_request(config, txn_request):
    web3 = config.web3
    wait = config.wait
    request_lib = config.request_lib

    if txn_request.wasCalled:
        config.logger.debug(
            "Aborting execution for Request @ %s. Reason: Already called.",
            txn_request.address,
        )
        return
    elif txn_request.isCancelled:
        config.logger.debug(
            "Aborting execution for Request @ %s. Reason: Cancelled.",
            txn_request.address,
        )
        return
    elif not txn_request.inExecutionWindow:
        config.logger.debug(
            "Aborting execution for Request @ %s. Reason: Outside of execution "
            "window.",
            txn_request.address,
        )
        return
    elif txn_request.inReservedWindow and not txn_request.isClaimedBy(web3.eth.defaultAccount):
        config.logger.debug(
            "Aborting execution for Request @ %s. Reason: In reserved window "
            "and claimed by: %s",
            txn_request.address,
            txn_request.claimedBy,
        )
        return

    # Since we are directly executing the request we don't need to include the
    # stack depth checking gas here.
    execute_gas = txn_request.callGas + request_lib.call().EXECUTION_GAS_OVERHEAD()
    gas_limit = web3.eth.getBlock('latest')['gasLimit']

    if execute_gas > gas_limit:
        config.logger.error(
            "Aborting execution for Request @ %s. Reason: Execution gas above "
            "network gas limit.  Computed Execution Gas: %s | Network gas limit: "
            "%s",
            txn_request.address,
            execute_gas,
            gas_limit,
        )

    config.logger.info(
        "Attempting execution of Request @ %s.  Now: %s | windowStart: %s | "
        "expectedPayment: %s | claimedBy: %s | inReservedWindow: %s",
        txn_request.address,
        txn_request.now,
        txn_request.windowStart,
        txn_request.payment * txn_request.paymentModifier // 100,
        txn_request.claimedBy,
        "Yes" if txn_request.inReservedWindow else "No",
    )

    execute_txn_hash = txn_request.transact({'gas': execute_gas}).execute()

    try:
        execute_txn_receipt = wait.for_receipt(execute_txn_hash)
    except gevent.Timeout:
        config.logger.error(
            "Timed out waiting for execution transaction receipt for request @ "
            "%s.  Txn Hash: %s",
            txn_request.address,
            execute_txn_hash,
        )

    if txn_request.wasCalled:
        config.logger.info(
            "Request @ %s has been executed.",
            txn_request.address,
        )
    else:
        config.logger.error(
            "Execution transaction did not successfully execute Request  @ %s. "
            "Execute Txn Hash: %s",
            txn_request.address,
            execute_txn_hash,
        )

    # TODO: this should be it's own log entry watcher.
    executed_filter = txn_request.pastEvents('Executed', {
        'fromBlock': txn_request.executionWindowStartBlock,
        'toBlock': txn_request.executionWindowEndBlock,
    })
    execute_logs = executed_filter.get(only_changes=False)

    if execute_logs:
        for log_entry in execute_logs:
            if log_entry['transactionHash'] == execute_txn_hash:
                config.logger.info(
                    "Successful Execution of Request @ %s.  Payment: %s | "
                    "Donation: %s | DonationBenefactor: %s | GasReimbursed: "
                    "%s | ActualGas: %s",
                    txn_request.address,
                    log_entry['args']['payment'],
                    log_entry['args']['donation'],
                    txn_request.donationBenefactor,
                    log_entry['args']['measuredGasConsumption'],
                    execute_txn_receipt['gasUsed'],
                )
            else:
                execute_txn = web3.eth.getTransaction(
                    log_entry['transactionHash'],
                )
                config.logger.error(
                    "Failed Execution of Request @ %s.  Actually executed "
                    "by: %s",
                    txn_request.address,
                    execute_txn['from'],
                )

    # TODO: this should be it's own log entry watcher.
    aborted_filter = txn_request.pastEvents('Aborted', {
        'fromBlock': txn_request.executionWindowStartBlock,
        'toBlock': txn_request.executionWindowEndBlock,
    })
    aborted_logs = aborted_filter.get(only_changes=False)
    if aborted_logs:
        for log_entry in aborted_logs:
            if log_entry['transactionHash'] == execute_txn_hash:
                config.logger.error(
                    "Execution transaction Aborted for Request @ %s.  Reason: "
                    "%s",
                    txn_request.address,
                    ABORTED_REASON_MAP.get(
                        log_entry['args']['reason'],
                        'Unknown Errror',
                    ),
                )
            else:
                aborted_txn = web3.eth.getTransaction(
                    log_entry['transactionHash'],
                )
                if aborted_txn['from'] in web3.eth.accounts:
                    config.logger.error(
                        "Found Unexpected Abort log for Request @ %s. From: %s "
                        "| Reason: %s",
                        txn_request.address,
                        aborted_txn['from'],
                        ABORTED_REASON_MAP.get(
                            log_entry['args']['reason'],
                            'Unknown Errror',
                        ),
                    )
                else:
                    config.logger.info(
                        "Found Abort log for Request @ %s. From: %s "
                        "| Reason: %s",
                        txn_request.address,
                        aborted_txn['from'],
                        ABORTED_REASON_MAP.get(
                            log_entry['args']['reason'],
                            'Unknown Errror',
                        ),
                    )


@locked_txn_request
def cleanup_txn_request(config, txn_request):
    # TODO
    assert False
