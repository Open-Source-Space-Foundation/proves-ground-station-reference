---
status: accepted
date: 2026-10-18
---
# Station layer and mission layer are separate repos

The hardware, OS, rotator chain and tracking tools of a ground station serve every PROVES satellite, while the flight dictionary, GDS framing plugin, key handling and TLE source change per satellite. Electra re-enters within months and the stations outlive it, so this repo holds the station layer and each mission's ops repo (today `proves-electra-ops`) holds its mission pack. The alternative, keeping stations under the Electra repo, would make the next operator look for Atlas station builds inside an Electra repo.

## Consequences

- `proves-electra-ops` keeps pass logs, sequences and the Electra mission pack. Its station config migrates to this repo's `station.toml` schema in a separate PR.
- A station runs one or more mission packs on top of one station layer; a mission pack never carries hardware.
