require("chai")
  .use(require("chai-as-promised"))
  .should()

const { expect } = require("chai")

// Contracts
const RequestTracker = artifacts.require("./RequestTracker.sol")

// Brings in config.web3 (v1.0.0)
const NULL_ADDR = "0x0000000000000000000000000000000000000000"

contract("Request tracker", async (accounts) => {
  it("should test request tracker", async () => {
    const mockSchedulerAddr = accounts[0]

    const requestTracker = await RequestTracker.new()
    expect(requestTracker.address).to.exist

    const values = [
      ["0x0000000000000000000000000000000000000001", 2],
      ["0x0000000000000000000000000000000000000002", 1],
      ["0x0000000000000000000000000000000000000003", 4],
      ["0x0000000000000000000000000000000000000004", 10],
      ["0x0000000000000000000000000000000000000005", 10],
      ["0x0000000000000000000000000000000000000006", 3],
      ["0x0000000000000000000000000000000000000007", 2],
      ["0x0000000000000000000000000000000000000008", 8],
      ["0x0000000000000000000000000000000000000009", 3],
      ["0x0000000000000000000000000000000000000010", 4],
      ["0x0000000000000000000000000000000000000011", 0],
      ["0x0000000000000000000000000000000000000012", 2],
    ]

    const expectedOrder = [
      "0x0000000000000000000000000000000000000011",
      "0x0000000000000000000000000000000000000002",
      "0x0000000000000000000000000000000000000001",
      "0x0000000000000000000000000000000000000007",
      "0x0000000000000000000000000000000000000012",
      "0x0000000000000000000000000000000000000006",
      "0x0000000000000000000000000000000000000009",
      "0x0000000000000000000000000000000000000003",
      "0x0000000000000000000000000000000000000010",
      "0x0000000000000000000000000000000000000008",
      "0x0000000000000000000000000000000000000004",
      "0x0000000000000000000000000000000000000005",
    ]

    values.forEach(async (items) => {
      // console.log(items[0], items[1])
      const tx = await requestTracker.addRequest(items[0], items[1])
      expect(tx.receipt).to.exist
    })

    const res = await requestTracker.query(mockSchedulerAddr, ">=", 0)
    expect(res).to.equal(expectedOrder[0])
    const res2 = await requestTracker.query(mockSchedulerAddr, "<=", 20)
    expect(res2).to.equal(expectedOrder[expectedOrder.length - 1])

    expectedOrder.forEach(async (addr, index) => {
      const isKnown = await requestTracker.isKnownRequest(
        mockSchedulerAddr,
        addr
      )
      expect(isKnown).to.equal(true)

      if (index > 0) {
        const prevRequest = await requestTracker.getPreviousRequest(
          mockSchedulerAddr,
          addr
        )
        expect(prevRequest).to.equal(expectedOrder[index - 1])
      } else {
        const prevRequest = await requestTracker.getPreviousRequest(
          mockSchedulerAddr,
          addr
        )
        expect(prevRequest).to.equal(NULL_ADDR)
      }

      if (index < expectedOrder.length - 1) {
        const nextRequest = await requestTracker.getNextRequest(
          mockSchedulerAddr,
          addr
        )
        expect(nextRequest).to.equal(expectedOrder[index + 1])
      } else {
        const nextRequest = await requestTracker.getNextRequest(
          mockSchedulerAddr,
          addr
        )
        expect(nextRequest).to.equal(NULL_ADDR)
      }
    })
  })

  it("should test adding and removing", async () => {
    const mockSchedulerAddr = accounts[0]

    const requestTracker = await RequestTracker.new()
    expect(requestTracker.address).to.exist

    const isKnown = await requestTracker.isKnownRequest(
      mockSchedulerAddr,
      "0x0000000000000000000000000000000000000001"
    )
    expect(isKnown).to.equal(false)

    // Add a request
    await requestTracker.addRequest(
      "0x0000000000000000000000000000000000000001",
      12345
    )
    const isKnown2 = await requestTracker.isKnownRequest(
      mockSchedulerAddr,
      "0x0000000000000000000000000000000000000001"
    )
    expect(isKnown2).to.equal(true)

    // Remove a request
    await requestTracker.removeRequest("0x0000000000000000000000000000000000000001")
    const isKnown3 = await requestTracker.isKnownRequest(
      mockSchedulerAddr,
      "0x0000000000000000000000000000000000000001"
    )
    expect(isKnown3).to.equal(false)
  })
})
