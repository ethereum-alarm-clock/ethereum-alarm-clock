const _      = require("lodash"),
    contract = require("truffle-contract"),
    nconf    = require("nconf"),
    path     = require("path"),
    Web3     = require("web3"),
    defaults = require("./defaults.json");

const configPath = path.join(__dirname, '../config');
nconf.env().argv();
nconf.file({file: path.join(configPath, (nconf.get('NODE_ENV') || "dev") + ".json")});
nconf.defaults(defaults);

const provider = new Web3.providers.HttpProvider(nconf.get("ethereum:provider"));
const web3     = new Web3(provider);

// let properties       = ["contract_name", "abi", "unlinked_binary"];
// let contractDefaults = {
//     from: web3.eth.accounts[0],
//     gas: 4712388,
//     gasPrice: 100000000000
// };

// let MathLib = contract(_.pick(require("../build/contracts/MathLib.json"), properties));
// MathLib.setProvider(provider);
// MathLib.defaults(contractDefaults);

// let GroveLib = contract(_.pick(require("../build/contracts/GroveLib.json"), properties));
// GroveLib.setProvider(provider);
// GroveLib.defaults(contractDefaults);

// let IterTools = contract(_.pick(require("../build/contracts/IterTools.json"), properties));
// IterTools.setProvider(provider);
// IterTools.defaults(contractDefaults);

// let ExecutionLib = contract(_.pick(require("../build/contracts/ExecutionLib.json"), properties));
// ExecutionLib.setProvider(provider);
// ExecutionLib.defaults(contractDefaults);

// let RequestMetaLib = contract(_.pick(require("../build/contracts/RequestMetaLib.json"), properties));
// RequestMetaLib.setProvider(provider);
// RequestMetaLib.defaults(contractDefaults);

// let ClaimLib = contract(_.pick(require("../build/contracts/ClaimLib.json"), properties));
// ClaimLib.setProvider(provider);
// ClaimLib.defaults(contractDefaults);

// let PaymentLib = contract(_.pick(require("../build/contracts/PaymentLib.json"), properties));
// PaymentLib.setProvider(provider);
// PaymentLib.defaults(contractDefaults);

// let RequestScheduleLib = contract(_.pick(require("../build/contracts/RequestScheduleLib.json"), properties));
// RequestScheduleLib.setProvider(provider);
// RequestScheduleLib.defaults(contractDefaults);

// let RequestLib = contract(_.pick(require("../build/contracts/RequestLib.json"), properties));
// RequestLib.setProvider(provider);
// RequestLib.defaults(contractDefaults);

// let SchedulerLib = contract(_.pick(require("../build/contracts/SchedulerLib.json"), properties));
// SchedulerLib.setProvider(provider);
// SchedulerLib.defaults(contractDefaults);

// let BaseScheduler = contract(_.pick(require("../build/contracts/BaseScheduler.json"), properties));
// BaseScheduler.setProvider(provider);
// BaseScheduler.defaults(contractDefaults);

// let BlockScheduler = contract(_.pick(require("../build/contracts/BlockScheduler.json"), properties));
// BlockScheduler.setProvider(provider);
// BlockScheduler.defaults(contractDefaults);

// let TimestampScheduler = contract(_.pick(require("../build/contracts/TimestampScheduler.json"), properties));
// TimestampScheduler.setProvider(provider);
// TimestampScheduler.defaults(contractDefaults);

// let RequestTracker = contract(_.pick(require("../build/contracts/RequestTracker.json"), properties));
// RequestTracker.setProvider(provider);
// RequestTracker.defaults(contractDefaults);

// let TransactionRequest = contract(_.pick(require("../build/contracts/TransactionRequest.json"), properties));
// TransactionRequest.setProvider(provider);
// TransactionRequest.defaults(contractDefaults);

// let RequestFactory = contract(_.pick(require("../build/contracts/RequestFactory.json"), properties));
// RequestFactory.setProvider(provider);
// RequestFactory.defaults(contractDefaults);

module.exports      = nconf;
module.exports.web3 = web3;

// module.exports.contracts = {
// MathLib: MathLib,
// GroveLib: GroveLib,
// IterTools: IterTools,
// ExecutionLib: ExecutionLib,
// RequestMetaLib: RequestMetaLib,
// ClaimLib: ClaimLib,
// PaymentLib: PaymentLib,
// RequestScheduleLib: RequestScheduleLib,
// RequestLib: RequestLib,
// SchedulerLib: SchedulerLib,
// BaseScheduler: BaseScheduler,
// BlockScheduler: BlockScheduler,
// TimestampScheduler: TimestampScheduler,
// RequestTracker: RequestTracker,
// TransactionRequest: TransactionRequest,
// RequestFactory: RequestFactory
// };