const path = require("path")
const nconf = require("nconf")
const Web3 = require("web3")
const defaults = require("./defaults.json")

const configPath = path.join(__dirname, '../config')
nconf.env().argv()
nconf.file({ file: path.join(configPath, `${nconf.get('NODE_ENV') || "dev"}.json`) })
nconf.defaults(defaults)

const provider = new Web3.providers.HttpProvider(nconf.get("ethereum:provider"))
const web3 = new Web3(provider)

module.exports = nconf
module.exports.web3 = web3
