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
ROW = {"substitute": "", "last_priced": "2026-10-19", "qty": "1", "flag": ""}
LA_BOOM = dict(ROW, group="Rotator", item="Antenna boom, end-mount", vendor="McMaster-Carr",
    part="9056K38, 6 ft (6061-T6 round tube, 1-1/2 in OD, 1/8 in wall)",
    url="https://www.mcmaster.com/9056K38/", unit_price_usd="83.46",
    status="proven", node="rotator", purpose="Holds the antenna in the rotator's elevation clamp.",
    note="LA's Yagi is end-mounted, so it hangs off a metal tube clamped in the rotator, clear of the elements. "
         "9056K38 covers every length; choose 6 ft when ordering.")
CROSSBOOM = dict(ROW, group="Rotator", item="Fiberglass cross-boom for two antennas", vendor="M2 Antenna Systems",
    part="FGCB60 (CROSSBOOM, HD FG 11 ft)", url="https://www.m2inc.com/FGCB60", unit_price_usd="389.99",
    status="proven", node="rotator",
    purpose="Carries the TX and RX antennas side by side on one rotator.",
    note="Borrego's cross-boom. M2's 11 ft heavy-duty boom for the G-5500. Fiberglass keeps metal out of the near field of the center-mounted antennas.")
TX_ANT = dict(ROW, group="Antenna", item="70 cm crossed Yagi, TX", vendor="M2 Antenna Systems", part="436CP16",
    url="https://m2inc.com/FG436CP16", unit_price_usd="367.95", status="untested", node="antenna", chain="tx",
    purpose="Transmit antenna. Center-mounts on the cross-boom.",
    note="Borrego's TX antenna. It has not yet closed an uplink at Borrego. LA's reference Yagi is end-mounted, "
         "which suits a tube boom rather than a center cross-boom.")
RX_ANT = dict(ROW, group="Antenna", item="70 cm crossed Yagi, RX", vendor="M2 Antenna Systems", part="436CP30",
    url="https://m2inc.com/FG436CP30", unit_price_usd="643.99", status="proven", node="antenna_rx", chain="rx",
    purpose="Receive antenna. Longer and higher gain than the TX antenna.",
    note="Borrego's RX antenna. 15.5 dBic per M2's spec sheet. Center mount.")


def split(base, upgrades):
    rows = []
    for r in base:
        if r["node"] == "antenna":
            rows += [CROSSBOOM, TX_ANT, RX_ANT]
            continue
        if r["node"] not in RF_CHAIN:
            rows.append(r)
            continue
        for side in ("TX", "RX"):
            c = dict(r, item=f"{r['item']} ({side})", chain=side.lower())
            if side == "RX" and r["node"] != "usb":
                c["node"] = r["node"] + "_rx"
            rows.append(c)
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
    single = list(data["uplink"])
    single.insert(next(i for i, r in enumerate(single) if r["group"] == "Antenna"), LA_BOOM)
    payload = {"configs": {"single": single, "split": split_rows},
               "upgrades": {"single": data["upgrades"], "split": split_upgrades}}
    page = (HERE / "prototype_views.template.html").read_text()
    page = page.replace("/*__DATA__*/null", json.dumps(payload))
    out = render.ROOT / "docs" / "bom-prototype.html"
    out.write_text(page)
    print(f"wrote {out.relative_to(render.ROOT)}")


if __name__ == "__main__":
    main()
