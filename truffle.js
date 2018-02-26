module.exports = {
    networks: {
        development: {
            gas: 4700000,
            gasPrice: 10000000000, // 10 gwei
            host: "localhost",
            port: 8545,
            network_id: "*" // Match any network id
        }
    }
};
