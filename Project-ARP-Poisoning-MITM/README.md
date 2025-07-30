# Project — ARP Cache Poisoning + Man-in-the-Middle

A term project implementing **ARP cache poisoning** to set up a
**man-in-the-middle (MITM)** position between a client and a server, together
with a **detection/defense** mechanism. All packet crafting is done from scratch
(no off-the-shelf attack tools), as required by the course. See the
[project spec](spec/CSE406ProjectJan2025.pdf).

> 🔒 **Controlled-lab work, educational use only.** The attack targets a private
> **VirtualBox host-only network** (`192.168.56.0/24`) with VMs I controlled
> (attacker / client / server). It must **never** be used on networks or hosts you
> do not own or are not authorized to test — doing so is illegal.
>
> This was a **group project**; this archive holds my group's submission. Per-member
> responsibilities are documented in the reports.

## What It Does

**The attack — `src/arp_poisoning_attack.py`.** Forges unsolicited ARP replies to
poison the client's and server's ARP caches so both map each other's IP to the
attacker's MAC, routing their traffic through the attacker:

- Resolves victim MACs, crafts ARP packets (via Scapy when available, else raw
  sockets), and sends rapid poisoning bursts on a background thread.
- Enables IP forwarding and monitors the intercepted traffic, achieving the MITM
  position between client (`.200`) and server (`.250`).

**The defense — `src/arp_defense_final.sh`.** A countermeasure (the project's
bonus task) that pins **static ARP entries** for the client↔server pair so forged
ARP replies are ignored, neutralizing the poisoning.

## Reports

| File | Contents |
|------|----------|
| [`reports/DesignReport_arp_poisoning_attack.pdf`](reports/DesignReport_arp_poisoning_attack.pdf) | Attack topology, protocol/timing diagrams, packet/frame details, design rationale. |
| [`reports/Final_Report.pdf`](reports/Final_Report.pdf) | Attack steps, screenshots, results, and the countermeasure. |
| [`reports/Presentation.pdf`](reports/Presentation.pdf) | Demo slides. |

## Running (in an isolated lab only)

```bash
# On the attacker VM in the host-only network:
sudo python3 src/arp_poisoning_attack.py

# Defense — run on client and server VMs to pin static ARP entries:
sudo bash src/arp_defense_final.sh server   # on the client
sudo bash src/arp_defense_final.sh client   # on the server
```

> Adjust the hard-coded `192.168.56.x` addresses to match your lab VMs.
