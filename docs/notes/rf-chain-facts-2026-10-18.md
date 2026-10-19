# RF chain facts, as stated by the operator on 2026-10-18

These were never written down in `proves-electra-ops`. They feed the hardware BOM and each station's `station.toml`.

## Los Angeles (uplink station)

| Item | Fact | Status |
|---|---|---|
| Antenna | Antennas-Amplifiers 70cmCROSS16WR, from the 70 cm LEO pack (https://antennas-amplifiers.com/70cm-leo-pack-antenna/) | proven |
| Antenna substitute | M2 Antennas 16-element 70 cm Yagi | works, per operator |
| Rotator mechanism | Yaesu G-5500 | proven |
| Rotator controller | ERC Duo, GS-232B emulation, FTDI FT230X USB serial D30EHHCE | proven |
| Feedline | LMR-400, length as needed, to a lightning arrestor, then into the shack | proven, length not recorded |
| Shack adapter | N to SMA, into the GRC | proven, exact adapter not recorded |
| LNA | Antennas-Amplifiers EME2-432 RHCP kit with Advanced Sequencer, owned, not connected | recommended upgrade |
| Mast | Non-penetrating tripod roof mount, model not recorded (roof camera 2026-10-05 confirms the shape) | proven, model open |
| Roof camera | Reolink, mounted upside down | accessory |

## Borrego Springs (receive station, uplink hardware present)

| Item | Fact | Status |
|---|---|---|
| RX antenna | M2 Antennas 436CP30 | proven for receive |
| TX antenna | M2 Antennas 436CP16 | never closed an uplink (0/60 commands) |
| LNA | LNA70 (vendor not recorded) in the receive chain | in the chain on receive passes |
| Rotator | Yaesu on OEM controller behind a GS-232B interface, FTDI FTEK843Y | proven |

## Open facts

- LMR-400 run lengths at both sites.
- Lightning arrestor make and model, and the grounding provision.
- Non-penetrating mount make and model.
- LNA70 vendor.
- Whether the Borrego LNA has a TX bypass, since a TX antenna exists there.
