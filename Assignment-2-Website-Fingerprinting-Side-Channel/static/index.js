function app() {
  return {
    /* This is the main app object containing all the application state and methods. */
    // The following properties are used to store the state of the application

    // results of cache latency measurements
    latencyResults: null,
    // local collection of trace data
    traceData: [],
    // Local collection of heapmap images
    heatmaps: [],

    // Current status message
    status: "",
    // Is any worker running?
    isCollecting: false,
    // Is the status message an error?
    statusIsError: false,
    // Show trace data in the UI?
    showingTraces: false,

    // Collect latency data using warmup.js worker
    async collectLatencyData() {
      this.isCollecting = true
      this.status = "Collecting latency data..."
      this.latencyResults = null
      this.statusIsError = false
      this.showingTraces = false

      try {
        // Create a worker
        let worker = new Worker("warmup.js")

        // Start the measurement and wait for result
        const results = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data)
          worker.postMessage("start")
        })

        // Update results
        this.latencyResults = results
        this.status = "Latency data collection complete!"

        // Terminate worker
        worker.terminate()
      } catch (error) {
        console.error("Error collecting latency data:", error)
        this.status = `Error: ${error.message}`
        this.statusIsError = true
      } finally {
        this.isCollecting = false
      }
    },

    // Collect trace data using worker.js and send to backend
    async collectTraceData() {
      this.isCollecting = true
      this.status = "Collecting trace data..."
      this.statusIsError = false
      this.showingTraces = true

      try {
        // Create a worker to run the sweep function
        let worker = new Worker("worker.js")

        // Start the measurement and wait for result
        const traceData = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data)
          worker.postMessage("start")
        })

        // Terminate worker
        worker.terminate()

        // Send the trace data to the backend for temporary storage and heatmap generation
        const response = await fetch("/collect_trace", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            trace_data: traceData,
            timestamp: Date.now(),
          }),
        })

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`)
        }

        const result = await response.json()

        // Add the heatmap to local collection
        if (result.heatmap_url) {
          this.heatmaps.push({
            url: result.heatmap_url,
            timestamp: result.timestamp,
            stats: result.stats,
          })
        }

        // Store trace data locally
        this.traceData.push({
          data: traceData,
          timestamp: Date.now(),
        })

        this.status = `Trace data collection complete! Generated heatmap ${this.heatmaps.length}`
      } catch (error) {
        console.error("Error collecting trace data:", error)
        this.status = `Error: ${error.message}`
        this.statusIsError = true
      } finally {
        this.isCollecting = false
      }
    },

    // Download the trace data as JSON (array of arrays format for ML)
    async downloadTraces() {
      try {
        this.status = "Fetching latest data from backend..."

        // Fetch the latest data from the backend API
        const response = await fetch("/api/get_results")
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`)
        }

        const data = await response.json()
        const traces = data.traces || []

        if (traces.length === 0) {
          this.status = "No traces available to download"
          this.statusIsError = true
          return
        }

        // Create a download file with the trace data in JSON format
        const jsonData = JSON.stringify(traces, null, 2)
        const blob = new Blob([jsonData], { type: "application/json" })
        const url = URL.createObjectURL(blob)

        // Create download link and trigger download
        const a = document.createElement("a")
        a.href = url
        a.download = `traces_${new Date().toISOString().split("T")[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        this.status = `Downloaded ${traces.length} traces successfully!`
        this.statusIsError = false
      } catch (error) {
        console.error("Error downloading traces:", error)
        this.status = `Error downloading traces: ${error.message}`
        this.statusIsError = true
      }
    },

    // Clear all results from the server
    async clearResults() {
      try {
        this.status = "Clearing all results..."

        // Send a request to the backend API to clear all results
        const response = await fetch("/api/clear_results", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`)
        }

        const result = await response.json()

        // Clear local copies of trace data and heatmaps
        this.traceData = []
        this.heatmaps = []
        this.latencyResults = null
        this.showingTraces = false

        this.status = result.message || "Cleared"
        this.statusIsError = false
      } catch (error) {
        console.error("Error clearing results:", error)
        this.status = `Error clearing results: ${error.message}`
        this.statusIsError = true
      }
    },

    // Fetch existing results when the page loads
    async fetchResults() {
      try {
        const response = await fetch("/api/get_results")
        if (response.ok) {
          const data = await response.json()
          this.heatmaps = data.heatmaps || []
          if (this.heatmaps.length > 0) {
            this.showingTraces = true
          }
        }
      } catch (error) {
        console.log("No existing results found")
      }
    },
  }
}


