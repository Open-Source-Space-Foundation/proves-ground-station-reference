---
status: accepted
date: 2026-10-18
---
# Reference design lists only proven parts

The RF review of 2026-10-01 recommends a mast LNA with a TX bypass relay, an SDR on a splitter and a VNA check of the Yagi, and both LA and Borrego already own LNA hardware. None of it has been in the chain on a pass that closed the link to Electra. The reference design therefore lists exactly the configuration that has closed the link (Radio Stick V2, no LNA, crossed Yagi over LMR-400), and everything else goes in a separate "recommended upgrades" list, each entry marked unproven until a commissioned station runs a pass with it. A new builder copies a working station first and adds opinion second.

## Consequences

- A part moves from upgrade to reference only with a pass log that shows it in the chain.
- The reference design can look conservative next to the RF review. That is intended.
