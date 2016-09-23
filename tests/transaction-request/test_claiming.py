import pytest

from web3.utils.encoding import (
    decode_hex,
)


def test_cannot_claim_before_first_claim_block(chain, web3, RequestData, get_claim_data):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_block > web3.eth.blockNumber

    chain.wait.for_block(first_claim_block - 1)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    with pytest.raises(AssertionError):
        get_claim_data(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_can_claim_at_first_claim_block(chain, web3, RequestData, get_claim_data):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_block > web3.eth.blockNumber

    chain.wait.for_block(first_claim_block)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    claim_data = get_claim_data(claim_txn_hash)
    assert claim_data

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.coinbase


def test_can_claim_at_last_claim_block(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    last_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 1

    # sanity
    assert last_claim_block > web3.eth.blockNumber

    chain.wait.for_block(last_claim_block)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.coinbase


def test_cannot_claim_after_last_claim_block(chain, web3, RequestData, get_claim_data):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    last_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod

    # sanity
    assert last_claim_block > web3.eth.blockNumber

    chain.wait.for_block(last_claim_block)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    with pytest.raises(AssertionError):
        get_claim_data(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_deposit_held_by_contract_on_claim(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 10

    # sanity
    assert claim_at > web3.eth.blockNumber

    chain.wait.for_block(claim_at)

    deposit_amount = 2 * request_data.paymentData.payment

    before_contract_balance = web3.eth.getBalance(txn_request.address)
    before_account_balance = web3.eth.getBalance(web3.eth.accounts[1])

    claim_txn_hash = txn_request.transact({
        'value': deposit_amount,
        'from': web3.eth.accounts[1],
    }).claim()
    claim_txn_receipt = chain.wait.for_receipt(claim_txn_hash)

    after_contract_balance = web3.eth.getBalance(txn_request.address)
    after_account_balance = web3.eth.getBalance(web3.eth.accounts[1])

    assert after_contract_balance - before_contract_balance == deposit_amount
    assert before_account_balance - after_account_balance == deposit_amount + web3.eth.gasPrice * claim_txn_receipt['gasUsed']

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]


def test_deposit_returned_if_claim_rejected(chain, web3, RequestData, get_claim_data):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    try_claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize - 3

    # sanity
    assert try_claim_at > web3.eth.blockNumber

    chain.wait.for_block(try_claim_at)

    deposit_amount = 2 * request_data.paymentData.payment

    before_contract_balance = web3.eth.getBalance(txn_request.address)
    before_account_balance = web3.eth.getBalance(web3.eth.accounts[1])

    claim_txn_hash = txn_request.transact({
        'value': deposit_amount,
        'from': web3.eth.accounts[1],
    }).claim()
    claim_txn = web3.eth.getTransaction(claim_txn_hash)
    claim_txn_receipt = chain.wait.for_receipt(claim_txn_hash)

    after_contract_balance = web3.eth.getBalance(txn_request.address)
    after_account_balance = web3.eth.getBalance(web3.eth.accounts[1])

    assert after_contract_balance == before_contract_balance
    assert after_account_balance == before_account_balance - claim_txn['gasPrice'] * claim_txn_receipt['gasUsed']

    with pytest.raises(AssertionError):
        get_claim_data(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_deposit_returned_even_if_returning_it_throws(chain, web3, RequestData, get_claim_data, proxy):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    try_claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize - 3

    # sanity
    assert try_claim_at > web3.eth.blockNumber

    chain.wait.for_block(try_claim_at)

    deposit_amount = 2 * request_data.paymentData.payment

    before_contract_balance = web3.eth.getBalance(txn_request.address)
    before_account_balance = web3.eth.getBalance(proxy.address)

    assert before_account_balance == 0

    claim_call_data = decode_hex(txn_request._encode_transaction_data('claim'))

    claim_txn_hash = proxy.transact({
        'value': deposit_amount,
    }).__proxy(txn_request.address, claim_call_data, )
    chain.wait.for_receipt(claim_txn_hash)

    after_contract_balance = web3.eth.getBalance(txn_request.address)
    after_account_balance = web3.eth.getBalance(proxy.address)

    assert after_contract_balance == before_contract_balance
    assert after_account_balance == deposit_amount

    request_data.refresh()
    assert request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_executing_own_claimed_call(chain, web3, RequestData, get_execute_data, get_claim_data):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_block > web3.eth.blockNumber

    chain.wait.for_block(first_claim_block)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
        'from': web3.eth.accounts[1],
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    assert get_claim_data(claim_txn_hash)

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({
        'from': web3.eth.accounts[1],
    }).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()
    assert request_data.meta.wasCalled is True

    assert get_execute_data(execute_txn_hash)


def test_executing_other_claimed_call_after_reserved_window(chain,
                                                            web3,
                                                            RequestData,
                                                            get_claim_data,
                                                            get_execute_data):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_block > web3.eth.blockNumber

    chain.wait.for_block(first_claim_block)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
        'from': web3.eth.accounts[1],
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    assert get_claim_data(claim_txn_hash)

    chain.wait.for_block(request_data.schedule.windowStart + request_data.schedule.reservedWindowSize)

    execute_txn_hash = txn_request.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()
    assert request_data.meta.wasCalled is True

    assert get_execute_data(execute_txn_hash)


def test_claim_block_determines_payment_amount():
    assert False
