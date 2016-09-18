import pytest


def test_cannot_claim_before_first_claim_block(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_block > web3.eth.blockNumber

    chain.wait.for_block(first_claim_block - 1)

    claim_txn_hash = txn_request.transact({'value': 2 * request_data.paymentData.payment}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_can_claim_at_first_claim_block(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_block > web3.eth.blockNumber

    chain.wait.for_block(first_claim_block)

    claim_txn_hash = txn_request.transact({'value': 2 * request_data.paymentData.payment}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.claimData.claimedBy == web3.eth.coinbase


def test_can_claim_at_last_claim_block(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    last_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 1

    # sanity
    assert last_claim_block > web3.eth.blockNumber

    chain.wait.for_block(last_claim_block)

    claim_txn_hash = txn_request.transact({'value': 2 * request_data.paymentData.payment}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.claimData.claimedBy == web3.eth.coinbase


def test_cannot_claim_after_last_claim_block(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    last_claim_block = request_data.schedule.windowStart - request_data.schedule.freezePeriod

    # sanity
    assert last_claim_block > web3.eth.blockNumber

    chain.wait.for_block(last_claim_block)

    claim_txn_hash = txn_request.transact({'value': 2 * request_data.paymentData.payment}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


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

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.claimData.claimedBy == web3.eth.accounts[1]


def test_deposit_returned_if_claim_rejected(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    try_claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize - 3

    # sanity
    assert try_claim_at > web3.eth.blockNumber

    chain.wait.for_block(try_claim_at)

    deposit_amount = 2 * request_data.paymentData.payment

    before_contract_balance = web3.eth.getBalance(txn_request.address)
    before_account_balance = web3.eth.getBalance(web3.eth.accounts[1])

    with pytest.raises(ValueError):
        txn_request.transact({
            'value': deposit_amount,
            'from': web3.eth.accounts[1],
        }).claim()

    after_contract_balance = web3.eth.getBalance(txn_request.address)
    after_account_balance = web3.eth.getBalance(web3.eth.accounts[1])

    assert after_contract_balance == before_contract_balance
    assert after_account_balance == before_account_balance

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_executing_own_claimed_call():
    assert False


def test_executing_other_claimed_call_after_reserved_window():
    assert False


def test_claim_block_determines_payment_amount():
    assert False
