# Assignment 2 — Website Fingerprinting (Cache Side-Channel)

A **co-located side-channel attack** that identifies which website a victim is
browsing in another tab — without seeing their screen or network traffic — by
measuring contention on the CPU's last-level cache from JavaScript, then
classifying the resulting traces with a neural network. See the
[specification](spec/specification.pdf) and my [report](report/2005048_report.pdf).

> Built and tested **only on my own machine** for the course. Educational use only.

## How It Works

**Task 1 — Timing warm-up (`static/warmup.js`).** Implements `readNlines(n)`,
which allocates an `n × LINESIZE` buffer and sweeps it at cache-line stride to
gauge the resolution of `performance.now()` (browsers deliberately coarsen it).

**Task 2 — Trace collection: Sweep Counting Attack (`static/worker.js`).** In a
web worker, repeatedly counts how many cache-line accesses fit into fixed `P`-ms
windows over ~10 s. The resulting count pattern depends on what the other tab is
doing, producing a per-website *fingerprint*. Traces are sent to the Flask
backend and stored in SQLite.

**Task 3 — Classification (`train.py`).** A **PyTorch** model is trained on the
collected traces to recognize specific websites from their sweep-count signatures.

## Layout

| Path | Role |
|------|------|
| [`static/index.html`](static/index.html) / [`index.js`](static/index.js) | Alpine.js + Pico CSS frontend; launches the worker and shows results. |
| [`static/warmup.js`](static/warmup.js) | `readNlines()` timing measurement (Task 1). |
| [`static/worker.js`](static/worker.js) | Sweep-counting trace collector (Task 2). |
| [`src/app.py`](src/app.py) | Flask backend serving the page and receiving traces. |
| [`src/collect.py`](src/collect.py) | Selenium-driven automated trace collection across sites. |
| [`src/database.py`](src/database.py) | SQLite storage layer. |
| [`src/train.py`](src/train.py) | PyTorch model training / evaluation. |
| [`src/requirements.txt`](src/requirements.txt) | Python dependencies. |

## Build & Run

```bash
pip install -r src/requirements.txt
python src/app.py            # serve the collection page (Flask)
# open the page, collect latency/sweep data; or automate with:
python src/collect.py
python src/train.py          # train & evaluate the website classifier
```
