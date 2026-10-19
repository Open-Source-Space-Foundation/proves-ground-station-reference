# Open questions

- **Key handoff** (deferred 2026-10-18): how a mission's HMAC key reaches an uplink station without passing through a repo, and how a station proves it holds the right key. Proposed: copy over SSH from the flight-secrets folder, verify by hash published in the mission pack. Receive stations are unaffected.
- **Borrego LNA power** (2026-10-19): which 12 V supply and which DC cable Borrego uses for the mast LNA (models not recorded), and whether that DC line gets its own surge protection where it enters the building. The LNA is not fed over the coax, so the DC-blocking IS-50NX-C2 is fine in the RX chain. The BOM lists the supply and cable as unpriced split lines until the models are known.
- **TX-to-RX isolation on the split boom** (2026-10-19): how much of the TX antenna's +30 dBm reaches the RX LNA on the shared cross-boom is unmeasured.
- **LA's unrecorded RF facts** (2026-10-19): the length of LA's indoor arrestor-to-shack run (the BOM lists a 6 ft placeholder) and the gender of the 70cmCROSS16WR's N connector (the RF chain assumes N female).
- **Single-antenna bench loopback** (2026-10-19): the bench loopback needs a second, receiving GRC, but a single-antenna station's BOM lists only one GRC.
