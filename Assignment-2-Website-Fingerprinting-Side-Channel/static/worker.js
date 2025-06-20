/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64
/* Find the L3 size by running `getconf -a | grep CACHE` */
const LLCSIZE = 8388608
/* Collect traces for 10 seconds; you can vary this */
const TIME = 10000
/* Collect traces every 10ms; you can vary this */
const P = 10

function sweep(P) {
  // Allocate a buffer of size LLCSIZE
  const buffer = new ArrayBuffer(LLCSIZE)
  const view = new Uint8Array(buffer)

  // Calculate number of cache lines
  const numCacheLines = LLCSIZE / LINESIZE

  // Array to store counts for each time period
  const K = TIME / P // Number of time periods
  const traces = []

  for (let period = 0; period < K; period++) {
    const startTime = performance.now()
    let count = 0

    // Keep reading cache lines for P milliseconds
    while (performance.now() - startTime < P) {
      // Read each cache line in the buffer
      for (let i = 0; i < LLCSIZE; i += LINESIZE) {
        // Force memory access by reading the first byte of each cache line
        view[i]
        //count++
      }
      count++;
    }

    traces.push(count)
  }

  return traces
}

self.addEventListener("message", function (e) {
  if (e.data === "start") {
    // Call the sweep function and return the result
    const result = sweep(P)
    self.postMessage(result)
  }
})
