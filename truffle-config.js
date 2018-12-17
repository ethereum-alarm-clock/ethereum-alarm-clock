const HDWalletProvider = require("truffle-hdwallet-provider");

// Test Address - 0xD593A23b099e85AE97CAB1b5a645959211B03277
// Main Address - 0x21ec253c9186065f05fb3f541085a185f96a16ee
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
    mainnet: {
      gas: 4700000,
      gasPrice: 3000000000, // 3 gwei
      provider: () => new HDWalletProvider(mnemonic, "https://mainnet.infura.io"),
      network_id: "1",
      // overwrite: false,
    },
    kovan: {
      gas: 4700000,
      gasPrice: 2800000000, // 2.8 gwei
      provider: () => new HDWalletProvider(mnemonic, "https://kovan.infura.io"),
      network_id: "42"
    },
    rinkeby: {
      gas: 4700000,
      gasPrice: 20000000000, // 20 gwei
      provider: () => new HDWalletProvider(mnemonic, "https://rinkeby.infura.io"),
      network_id: "4"
    },
    ropsten: {
      gas: 4700000,
      gasPrice: 10000000000, // 10 gwei
      provider: () => new HDWalletProvider(mnemonic, "https://ropsten.infura.io"),
      network_id: "3"
    },
  }
};
