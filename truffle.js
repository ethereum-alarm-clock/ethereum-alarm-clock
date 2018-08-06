const HDWalletProvider = require("truffle-hdwallet-provider");

// 0 - 0xD593A23b099e85AE97CAB1b5a645959211B03277
const mnemonic = "";

module.exports = {
  networks: {
    development: {
      gas: 4700000,
      gasPrice: 10000000000, // 10 gwei
      host: "localhost",
      port: 8545,
      network_id: "*" // Match any network id
    },
    kovan: {
      gas: 4700000,
      gasPrice: 10000000000, // 10 gwei
      host: "localhost",
      port: 8545,
      network_id: "42"
    },
    ropsten: {
      gas: 4700000,
      gasPrice: 10000000000, // 10 gwei
      provider: () => new HDWalletProvider(mnemonic, "https://ropsten.infura.io"),
      network_id: "3"
    },
    rinkeby: {
      gas: 4700000,
      gasPrice: 20000000000, // 20 gwei
      provider: () => new HDWalletProvider(mnemonic, "https://rinkeby.infura.io"),
      network_id: "4"
    }
  }
};
