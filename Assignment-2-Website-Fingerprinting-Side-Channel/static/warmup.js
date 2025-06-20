/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64

function readNlines(n) {
  // Allocate a buffer of size n * LINESIZE
  const bufferSize = n * LINESIZE
  const buffer = new ArrayBuffer(bufferSize)
  const view = new Uint8Array(buffer)

  const times = []

  // Read each cache line 10 times and measure time
  for (let iteration = 0; iteration < 10; iteration++) {
    const startTime = performance.now()

    // Read the buffer in steps of LINESIZE
    for (let i = 0; i < bufferSize; i += LINESIZE) {
      // Force memory access by reading the first byte of each cache line
      const value = view[i]
    }

    const endTime = performance.now()
    times.push(endTime - startTime)
  }

  // Return the median time
  times.sort((a, b) => a - b)
  return times[Math.floor(times.length / 2)]
}

self.addEventListener("message", function (e) {
  if (e.data === "start") {
    const results = {}

    // Call the readNlines function for n = 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000
    const nValues = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]

    for (const n of nValues) {
      results[n] = readNlines(n)
    }

    self.postMessage(results)
  }
})
