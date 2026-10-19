---
status: accepted
date: 2026-10-19
---
# One hardware BOM, two antenna configurations

The hardware BOM used to keep an uplink list and a receive list, but the receive list differed only by the commissioning kit, and the two stations that have worked a pass differ in a way those lists never captured: LA transmits and receives through one antenna, while Borrego runs separate TX and RX antennas, feedlines and GRCs on one rotator via a fiberglass cross-boom. The kit therefore has one hardware BOM, `bom/reference.csv`, with a `config` column: `single` (LA's shape), `split` (Borrego's shape) or `all`. Recommended upgrades stay in their own list, `bom/upgrades.csv`, as ADR 0001 requires. Receive and uplink remain station roles: an uplink station holds the mission key on its host and runs the commissioning TX checks; they do not select a parts list.

ADR 0001 says the reference design lists only parts that have closed the link. The split configuration is listed because Borrego runs it, and each row carries its own BOM status rather than inheriting one from the configuration. The split TX antenna (M2 436CP16) is `untested`: it has not closed an uplink at Borrego (0/60 commands), so the split configuration as a whole has not closed an uplink. Its RX side (436CP30 and the SSB LNA 70) is proven for receive.

The BOM also states how the parts connect. `bom/rf_chains.csv` lists every RF path from antenna, or the source radio on the bench, to the receiving radio, with each part's in and out connector, and `bom/render.py` refuses to render if any junction fails to mate. The earlier BOM listed one 100 ft feedline and an arrestor whose surge side was male, so the parts as listed could not be joined; the mate check is why the BOM can no longer omit a patch cable or adapter.

## Consequences

- A builder picks a configuration and orders one list. The order sheet merges the TX and RX copies of a shared part into one line.
- Adding a part to an RF path means adding it to `rf_chains.csv` with its connectors, or the render fails.
- A split station's uplink claim waits on a pass log, the same as any other part under ADR 0001.
