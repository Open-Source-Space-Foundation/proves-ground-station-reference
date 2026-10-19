#!/usr/bin/env python3
"""PROTOTYPE, throwaway. Four BOM views on one page, switchable via ?variant=A..D.

Question: what should the buyer view and the developer view of the BOM look like?
A, B = university buyer (order from it). C, D = station developer (understand the system).

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


def main():
    data = {key: render.load(key) for key, _, _ in render.TIERS}
    for rows in data.values():
        for r in rows:
            r["purpose"], r["node"], r["flag"] = ANNOTATIONS[r["item"]]
    tiers = [{"key": k, "title": t, "blurb": b} for k, t, b in render.TIERS]
    page = (HERE / "prototype_views.template.html").read_text()
    page = page.replace("/*__DATA__*/null", json.dumps({"tiers": tiers, "rows": data}))
    out = render.ROOT / "docs" / "bom-prototype.html"
    out.write_text(page)
    print(f"wrote {out.relative_to(render.ROOT)}")


if __name__ == "__main__":
    main()
