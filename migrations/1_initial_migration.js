/* eslint-disable no-console */
const Migrations = artifacts.require("./Migrations.sol")

module.exports = (deployer) => {
  deployer.deploy(Migrations, { gas: 350000 })
    .then(() => {
      console.log('DEPLOYED MIGRATIONS')
    })
}
