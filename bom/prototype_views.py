#!/usr/bin/env python3
"""PROTOTYPE, throwaway. Three BOM views on one page, switchable via ?variant=A|C|D.

Question: what should the buyer view and the developer view of the BOM look like?
A = university buyer (order from it). C, D = station developer (understand the system).
Round 2: one BOM (no receive/uplink tiers), with a single-antenna vs split TX/RX (Borrego) switch.

Run: python3 -I bom/prototype_views.py  -> open docs/bom-prototype.html
Reads the real bom/*.csv through render.py's loader. The per-item `purpose`, `node`
and `flag` annotations below are prototype-only; if a view wins, they become CSV columns.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("render", HERE / "render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

# item -> (one-line purpose for a buyer, diagram node, buyer flag or "")
ANNOTATIONS = {
    "Raspberry Pi, 64-bit, 4 GB or more": ("Station computer. Runs tracking and the ground software.", "pi", ""),
    "Official 27 W USB-C power supply": ("Powers the Pi 5.", "pi", ""),
    "Official Pi 5 case with fan": ("Keeps the Pi cool through unattended passes.", "pi", ""),
    "microSD card, 32 GB or more, A2": ("Boot disk for the Pi.", "pi", "quote"),
    "Azimuth-elevation rotator mechanism": ("Turns and tilts the antenna to follow the satellite.", "rotator", ""),
    "Rotator computer interface, GS-232B emulation, USB serial": ("Lets the Pi drive the rotator over USB.", "rotctl", ""),
    "70 cm crossed Yagi, RHCP, 8+8 elements": ("The antenna. Sends and receives the satellite signal.", "antenna", "intl"),
    "LMR-400 coax, N male both ends, 100 ft": ("Low-loss cable from the roof to the radio.", "coax", ""),
    "N-type coaxial lightning arrestor, gas discharge": ("Blocks lightning surges where the cable enters the building.", "arrestor", ""),
    "N female to SMA male adapter": ("Joins the thick coax to the radio's small SMA port.", "adapter", ""),
    "GRC: Radio Stick V2": ("The radio. Talks LoRa to the satellite.", "grc", "proves"),
    "USB-A to USB-C cable, data rated, 1 m": ("Connects the radio to the Pi.", "usb", "quote"),
    "Non-penetrating roof mount and ballast": ("Holds the mast on the roof. Chosen per site.", "mount", "site"),
    "VHF/UHF digital power and SWR meter, 125 to 525 MHz": ("Checks transmit power and antenna match when commissioning.", "swr", ""),
    "SMA attenuator pads, 30 dB or more total, 5 W or more": ("Lets the radio safely talk to a second radio on the bench.", "bench", "quote"),
    "SMA male to SMA male jumper, 0.5 m": ("Bench cables for the loopback test.", "bench", "quote"),
    "Mast LNA, 70 cm": ("Boosts weak signals right at the antenna.", "lna", ""),
    "70 cm LNA kit with 1200 W T/R relays, RHCP": ("Mast amplifier with relays that protect it during transmit.", "lna", "quote"),
    "Sequencer for LNA and PA switching": ("Switches the amplifier out before the radio transmits.", "sequencer", "intl"),
    "TinyGS node": ("Independent receiver reporting to the TinyGS network.", "tinygs", ""),
    "SDR on a splitter": ("Measures the satellite's true frequency and weak signals.", "sdr", ""),
    "Pi 5 real-time clock battery": ("Keeps the Pi's clock running through a power cut.", "pi", ""),
}


# Split TX/RX (Borrego shape): every RF-chain part is bought once per chain.
RF_CHAIN = {"antenna", "coax", "arrestor", "adapter", "grc", "usb"}
# A dedicated RX antenna means the LNA never sees transmit power, so no T/R switching is needed.
SPLIT_DROPS = {"70 cm LNA kit with 1200 W T/R relays, RHCP", "Sequencer for LNA and PA switching"}
CROSSBOOM = {
    "group": "Rotator", "item": "Cross-boom for two antennas", "vendor": "?", "part": "", "url": "", "qty": "1",
    "unit_price_usd": "?", "substitute": "", "status": "untested", "last_priced": "", "flag": "verify", "node": "rotator",
    "purpose": "Carries the TX and RX antennas side by side on one rotator.",
    "note": "Borrego mounts both Yagis on one cross-boom on a single rotator. Part not recorded.",
}


def split(base, upgrades):
    rows = []
    for r in base:
        if r["node"] not in RF_CHAIN:
            rows.append(r)
            continue
        for side in ("TX", "RX"):
            c = dict(r, item=f"{r['item']} ({side})", chain=side.lower())
            if side == "RX" and r["node"] != "usb":
                c["node"] = r["node"] + "_rx"
            if side == "RX" and r["node"] == "antenna":
                c["flag"] = "verify"
                c["note"] = "Borrego's RX antenna model is not recorded here; listed as the same Yagi. " + r["note"]
            rows.append(c)
    rows.insert(next(i for i, r in enumerate(rows) if r["group"] == "Antenna"), CROSSBOOM)
    lna = next(u for u in upgrades if u["node"] == "lna" and u["item"] not in SPLIT_DROPS)
    rows.append(dict(lna, group="Antenna", chain="rx", note="In Borrego's RX chain. With a dedicated RX antenna it needs no TX bypass, "
                     "but TX-to-RX isolation on a shared boom is not measured. " + lna["note"]))
    return rows, [u for u in upgrades if u["item"] not in SPLIT_DROPS and u is not lna]


def main():
    data = {key: render.load(key) for key, _, _ in render.TIERS}
    for rows in data.values():
        for r in rows:
            r["purpose"], r["node"], r["flag"] = ANNOTATIONS[r["item"]]
    # One BOM: the uplink list. Receive-only differs by the commissioning kit alone.
    split_rows, split_upgrades = split(data["uplink"], data["upgrades"])
    payload = {"configs": {"single": data["uplink"], "split": split_rows},
               "upgrades": {"single": data["upgrades"], "split": split_upgrades}}
    page = (HERE / "prototype_views.template.html").read_text()
    page = page.replace("/*__DATA__*/null", json.dumps(payload))
    out = render.ROOT / "docs" / "bom-prototype.html"
    out.write_text(page)
    print(f"wrote {out.relative_to(render.ROOT)}")


if __name__ == "__main__":
    main()
