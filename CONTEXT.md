# PROVES ground station reference

The reference design for a PROVES ground station: what to buy, what to install, and how to prove it works, so a partner team can stand up a station that matches the ones that have closed the link to Electra.

## Language

### Deliverable

**Station kit**:
The complete package needed to stand up one ground station: the hardware BOM, the software manifest, the provisioning procedure, the station config, and the acceptance check.
_Avoid_: BOM (when the whole package is meant), kit (alone), package

**Hardware BOM**:
The parts list of a station kit: every physical component with vendor, part number, quantity, unit price, and acceptable substitutes.
_Avoid_: BOM (alone), parts list, shopping list

**Software manifest**:
The pinned versions and hashes of the software and firmware a station runs. Electra's lives in `known-good.toml`.
_Avoid_: software BOM, requirements, versions file

**Reference design**:
The exact configuration that has closed the link to a PROVES satellite. Only proven components belong in it.
_Avoid_: recommended design, baseline, standard build

**Recommended upgrade**:
A component the RF review suggests but no station has yet proven on a real pass. Listed apart from the reference design.
_Avoid_: optional, nice-to-have, future work

### Station shapes

**Ground station**:
One installed set of station-kit hardware at one site, with a name and coordinates.
_Avoid_: site (alone), GS, node

**Uplink station**:
A ground station that can command the satellite: TX-capable GRC, rotator, power meter, and the mission's key on the host.
_Avoid_: TX station, primary station, full station

**Receive station**:
A ground station that only receives: RX GRC and rotator, no key on the host. Its hardware is a strict subset of the uplink station's.
_Avoid_: RX station, feedback station, listening station, secondary station

**Station layer**:
Everything in a station kit that is the same for every mission: hardware, operating system, rotator chain, tracking tools.
_Avoid_: base, platform, infrastructure

**Mission layer**:
Everything in a station kit that changes per satellite: flight dictionary, GDS framing plugin, key handling, TLE source.
_Avoid_: payload, satellite config

### Hardware

**GRC**:
Ground Radio Controller: the USB LoRa radio board a station transmits and receives through, identified by its USB serial. Radio Stick V1 and V2 are GRCs.
_Avoid_: radio, dongle, stick (alone), modem
