let BlockScheduler = artifacts.require("./BlockScheduler.sol");

module.exports = function(deployer) {
    deployer.deploy(BlockScheduler);
};
