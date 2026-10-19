# RF chain facts, as stated by the operator on 2026-10-18

These were never written down in `proves-electra-ops`. They feed the hardware BOM and each station's `station.toml`.

## Los Angeles (uplink station)

| Item | Fact | Status |
|---|---|---|
| Antenna | Antennas-Amplifiers 70cmCROSS16WR, from the 70 cm LEO pack (https://antennas-amplifiers.com/70cm-leo-pack-antenna/) | proven |
| Antenna substitute | M2 Antennas 16-element 70 cm Yagi | works, per operator |
| Rotator mechanism | Yaesu G-5500 | proven |
| Rotator controller | ERC Duo, GS-232B emulation, FTDI FT230X USB serial D30EHHCE | proven |
| Feedline | LMR-400, about 100 ft total, to a lightning arrestor, then into the shack | proven |
| Lightning arrestor | Generic N-type arrestor from Ham Radio Outlet | proven, exact part not recorded |
| Power meter | Mcbazel Surecom SW-102 digital VHF/UHF 125-525 MHz power and SWR meter (https://a.co/d/05T7MDRE) | proven |
| Bench attenuation | A 20 dB bench link plus at least 10 dB more, so the receiving GRC sees no more than 0 dBm (its absolute maximum is +10 dBm; the V2 transmits +30 dBm). Exact pads not recorded. | proven in use, parts open |
| Shack adapter | N to SMA, into the GRC | proven, exact adapter not recorded |
| LNA | Antennas-Amplifiers EME2-432 RHCP kit with Advanced Sequencer, owned, not connected | recommended upgrade |
| Mast | Non-penetrating tripod roof mount (roof camera 2026-10-05 confirms the shape). Mount and ballast are a per-site civil decision, not a BOM line. | site-specific |
| Roof camera | Reolink, mounted upside down | accessory |

## Borrego Springs (receive station, uplink hardware present)

| Item | Fact | Status |
|---|---|---|
| RX antenna | M2 Antennas 436CP30 | proven for receive |
| TX antenna | M2 Antennas 436CP16 | never closed an uplink (0/60 commands) |
| LNA | SSB Electronic LNA70 in the receive chain | in the chain on receive passes |
| Feedline | LMR-400, about 100 ft total | proven |
| Rotator | Yaesu on OEM controller behind a GS-232B interface, FTDI FTEK843Y | proven |

## Open facts

- Exact bench attenuator pads at LA (the BOM lists a generic SMA pad set, 30 dB or more total, 5 W or more).
- Grounding provision at each site.
- Whether the Borrego LNA has a TX bypass, since a TX antenna exists there.
