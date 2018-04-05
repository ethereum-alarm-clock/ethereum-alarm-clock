require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")
const BigNumber = require('bignumber.js')
const { calculateTimestampBucket, calculateBlockBucket } = require("../dataHelpers")

// Contracts
const RequestFactory = artifacts.require("./RequestFactory.sol")
const TransactionRequestCore = artifacts.require("./TransactionRequestCore.sol")

// Note - these tests were checked very well and should never be wrong.
// If they start failing - look in the contracts.
contract("Request factory", async () => {
  describe("getBucket()", async () => {
    let transactionRequestCore
    let requestFactory

    before(async () => {
      transactionRequestCore = await TransactionRequestCore.deployed()
      requestFactory = await RequestFactory.new(transactionRequestCore.address)
    })

    it("should calculate bucket for timestamp", async () => {
      const now = 1522825648
      const bucket = await requestFactory.getBucket(now, 2)
      const expected = calculateTimestampBucket(now)

      expect(bucket.equals(expected)).to.be.true
    })

    it("should calculate bucket for max timestamp", async () => {
      const intMax = new BigNumber(2).pow(255).minus(1)
      const now = new BigNumber(2).pow(256).minus(1)
      const bucket = await requestFactory.getBucket(now, 2)

      const expected = intMax.plus(1).times(-2).plus(calculateTimestampBucket(now)) // overflows

      expect(bucket.equals(expected)).to.be.true
    })

    it("should calculate bucket for block", async () => {
      const now = 6709534
      const bucket = await requestFactory.getBucket(now, 1)
      const expected = calculateBlockBucket(now)

      expect(bucket.equals(expected)).to.be.true
    })
  })
})
