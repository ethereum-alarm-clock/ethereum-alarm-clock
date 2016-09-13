def test_middle_third_claim_results_in_no_change(unmigrated_chain, web3, denoms,
                                                 deploy_fbc):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        call_value=5 * denoms.ether,
    )
    chain.wait.for_block(fbc.call().targetBlock())

    assert web3.eth.getBalance(client_contract.address) == 0

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert web3.eth.getBalance(client_contract.address) == 5 * denoms.ether
