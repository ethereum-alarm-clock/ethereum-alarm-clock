const Migrations = artifacts.require("./Migrations.sol")

module.exports = function(deployer) {
    deployer.deploy(Migrations, {gas: 4700000})
    .then(() => {
        console.log('DEPLOYED MIGRATIONS')
    })
}
