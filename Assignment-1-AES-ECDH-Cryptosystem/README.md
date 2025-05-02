# Assignment 1 — AES + ECDH Cryptosystem

A symmetric cryptosystem where the key is established over a public channel via
**Elliptic-Curve Diffie–Hellman (ECDH)** and used for **AES** encryption, then
demonstrated end-to-end over TCP sockets. See the
[specification](spec/CSE406-Assignment-1.pdf).

## Tasks

**Task 1 — AES-128 from scratch** ([`src/2005048_aes.py`](src/2005048_aes.py)).
AES with the four per-round steps (`subBytes`, `shiftRows`, `mixColumns` via
Galois-field arithmetic, `addRoundKey`) and the key schedule, run in **CBC mode**
with **PKCS#7 padding** and a random IV prepended to the ciphertext. Reports
key-schedule / encryption / decryption timing.

**Task 2 — Elliptic-Curve Diffie–Hellman** ([`src/2005048_ecc.py`](src/2005048_ecc.py)).
Generates curve parameters (`y² = x³ + ax + b mod P`) with a random prime `P`
sized to the key (128/192/256), checks non-singularity, picks a base point `G`,
derives Alice's and Bob's public points, and computes the shared secret
`R = Ka·Kb·G mod P`. Benchmarked across key sizes.

**Task 3 — End-to-end over TCP sockets.** Alice and Bob negotiate the shared key
via ECDH, then Alice encrypts with AES and sends the ciphertext, which Bob
decrypts with the shared key.

- [`src/2005048_alice.py`](src/2005048_alice.py) — **sender** (connects, sends `a, b, G, P, Ka·G`, then the AES ciphertext).
- [`src/2005048_bob.py`](src/2005048_bob.py) — **receiver** (listens, replies `Kb·G`, derives the key, decrypts).

## Layout

| Path | Role |
|------|------|
| [`src/2005048_aes.py`](src/2005048_aes.py) | AES-128 (CBC + PKCS#7) implementation. |
| [`src/2005048_ecc.py`](src/2005048_ecc.py) | Elliptic-Curve Diffie–Hellman key exchange. |
| [`src/2005048_alice.py`](src/2005048_alice.py) / [`2005048_bob.py`](src/2005048_bob.py) | Socket sender / receiver tying it together. |
| [`reference/bitvector-demo.py`](reference/bitvector-demo.py) | Course-provided `BitVector` demo with the AES S-box tables. |

## Build & Run

```bash
pip install BitVector

# Task 1 — AES self-test
python src/2005048_aes.py

# Task 2 — ECDH benchmark
python src/2005048_ecc.py

# Task 3 — end-to-end (two terminals): start the receiver first, then the sender
python src/2005048_bob.py      # receiver
python src/2005048_alice.py    # sender
```
