let _        = require("lodash"),
    contract = require("truffle-contract"),
    nconf    = require("nconf"),
    path     = require("path"),
    Web3     = require("web3"),
    defaults = require("./defaults.json");

let configPath = path.join(__dirname, '../config');
nconf.env().argv();
nconf.file({file: path.join(configPath, (nconf.get('NODE_ENV') || "dev") + ".json")});
nconf.defaults(defaults);

let provider = new Web3.providers.HttpProvider(nconf.get("ethereum:provider"));
let web3     = new Web3(provider);

let properties       = ["contract_name", "abi", "unlinked_binary"];
let contractDefaults = {
    from: web3.eth.accounts[0],
    gas: 4712388,
    gasPrice: 100000000000
};

let TransactionRequest = contract(_.pick(require("../build/contracts/TransactionRequest.json"), properties));
TransactionRequest.setProvider(provider);
TransactionRequest.defaults(contractDefaults);

module.exports      = nconf;
module.exports.web3 = web3;

module.exports.contracts = {
    TransactionRequest: TransactionRequest
};
