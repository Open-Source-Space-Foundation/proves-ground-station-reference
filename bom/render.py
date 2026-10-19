#!/usr/bin/env python3
"""Render docs/bom.md and docs/bom.html from bom/. Run: python3 -I bom/render.py"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOM = ROOT / "bom"
CONFIGS = {
    "single": ("Single antenna", "One antenna transmits and receives, as at LA."),
    "split": ("Split TX/RX", "Separate TX and RX antennas, feedlines and GRCs on one rotator via a fiberglass cross-boom, as at Borrego."),
}
UPGRADES_BLURB = "Suggested by the RF review but not yet in the chain on a pass that closed the link (ADR 0001)."
COLS = ["group", "item", "vendor", "part", "url", "qty", "unit_price_usd", "substitute", "status", "last_priced",
        "config", "block", "flag", "purpose", "note"]
STATUSES = {"proven", "substitute", "upgrade", "untested"}
FLAGS = {"", "intl", "proves", "site"}
# The BOM is published; device serials must not be. Mixed letter-digit run of 8+ chars.
SERIAL = re.compile(r"\b(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{8,}\b")
URL = re.compile(r"https?://\S+")


def in_config(r, cfg):
    return r["config"] in ("all", cfg)


def configs_of(r):
    return list(CONFIGS) if r["config"] == "all" else [r["config"]]


def load(name, topo):
    with open(BOM / f"{name}.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if list(r) != COLS:
            sys.exit(f"{name}.csv: columns must be {COLS}")
        it = r["item"]
        if r["status"] not in STATUSES:
            sys.exit(f"{name}.csv: bad status {r['status']!r} on {it!r}")
        if r["config"] not in ("all", *CONFIGS):
            sys.exit(f"{name}.csv: bad config {r['config']!r} on {it!r}")
        if r["flag"] not in FLAGS:
            sys.exit(f"{name}.csv: bad flag {r['flag']!r} on {it!r}")
        if not re.fullmatch(r"\d+", r["qty"]):
            sys.exit(f"{name}.csv: qty {r['qty']!r} is not an integer on {it!r}")
        if r["unit_price_usd"] != "?" and not re.fullmatch(r"\d+(\.\d+)?", r["unit_price_usd"]):
            sys.exit(f"{name}.csv: price {r['unit_price_usd']!r} is not a number or '?' on {it!r}")
        for tok in SERIAL.findall(URL.sub("", r["note"])):
            if tok not in r["part"]:
                sys.exit(f"{name}.csv: note on {it!r} carries {tok!r}, which looks like a device serial; publish the fact without the value")
        for cfg in configs_of(r):
            if r["block"] not in topo["positions"][cfg]:
                sys.exit(f"{name}.csv: block {r['block']!r} on {it!r} is not in topology.json for config {cfg}")
    return rows


def check_topology(topo):
    for cfg in CONFIGS:
        pos = topo["positions"][cfg]
        for b in pos:
            if b not in topo["blocks"]:
                sys.exit(f"topology.json: {cfg} positions block {b!r} that has no entry in blocks")
        for link in topo["links"][cfg]:
            for b in link[:2]:
                if b not in pos:
                    sys.exit(f"topology.json: {cfg} link {link[:2]} names {b!r}, which has no {cfg} position")


def check_unique(*files):
    seen = set()
    for rows in files:
        for r in rows:
            if r["item"] in seen:
                sys.exit(f"item {r['item']!r} appears more than once across reference.csv and upgrades.csv")
            seen.add(r["item"])


def totals(rows):
    """Return (sum of priced lines, count of lines priced '?')."""
    total, unknown = 0.0, 0
    for r in rows:
        if r["unit_price_usd"] == "?":
            unknown += 1
        else:
            total += float(r["unit_price_usd"]) * int(r["qty"])
    return total, unknown


def merged(rows):
    """Buyer lines: rows sharing vendor and part collapse to one line with summed qty."""
    out = {}
    for r in rows:
        key = (r["vendor"], r["part"]) if r["part"] else r["item"]
        if key in out:
            m = out[key]
            m["qty"] = str(int(m["qty"]) + int(r["qty"]))
            m["purpose"] = m["purpose"].rstrip() + " One each for TX and RX."
        else:
            out[key] = dict(r, item=re.sub(r" \(RX\)$", "", r["item"]))
    return list(out.values())


def money(r):
    return "?" if r["unit_price_usd"] == "?" else f"${float(r['unit_price_usd']):,.2f}"


def md_cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def md_table(rows, with_config=False):
    head = ["Item", "Purpose", "Vendor", "Part", "Qty", "Unit USD", "Status", "Substitute", "Last priced", "Note"]
    if with_config:
        head.insert(1, "Config")
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        part = f"[{md_cell(r['part'])}]({r['url']})" if r["url"] and r["part"] else md_cell(r["part"])
        cells = [md_cell(r["item"]), md_cell(r["purpose"]), md_cell(r["vendor"]), part, r["qty"], money(r), r["status"],
                 md_cell(r["substitute"]), r["last_priced"], md_cell(r["note"])]
        if with_config:
            cells.insert(1, r["config"])
        out.append("| " + " | ".join(cells) + " |")
    return out


def render_md(ref, upg):
    out = ["# Hardware BOM", "", "Generated by `bom/render.py` from `bom/`. Edit the CSVs and `topology.json`, not this file.", "",
           "| Configuration | Priced total (USD) | Lines without a price | With upgrades (USD) |", "|---|---|---|---|"]
    for cfg, (title, _) in CONFIGS.items():
        t, u = totals(r for r in ref if in_config(r, cfg))
        tu, _ = totals(r for r in upg if in_config(r, cfg))
        out.append(f"| {title} | ${t:,.2f} | {u} | ${t + tu:,.2f} |")
    out += ["", "Totals cover only lines with a confirmed price. Shipping, duty and tax are not included."]
    for cfg, (title, blurb) in CONFIGS.items():
        out += ["", f"## {title}", "", blurb, ""]
        out += md_table(merged(r for r in ref if in_config(r, cfg)))
    out += ["", "## Recommended upgrades", "", UPGRADES_BLURB, ""]
    out += md_table(upg, with_config=True)
    return "\n".join(out) + "\n"


def render_html(ref, upg, topo):
    data = {"configs": {k: v[0] for k, v in CONFIGS.items()}, "reference": ref, "upgrades": upg, "topology": topo}
    # "</" would close the inline <script> early.
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (BOM / "bom.template.html").read_text().replace("/*__DATA__*/null", blob)


def main():
    topo = json.loads((BOM / "topology.json").read_text())
    check_topology(topo)
    ref, upg = load("reference", topo), load("upgrades", topo)
    check_unique(ref, upg)
    (ROOT / "docs" / "bom.md").write_text(render_md(ref, upg))
    (ROOT / "docs" / "bom.html").write_text(render_html(ref, upg, topo))
    for cfg, (title, _) in CONFIGS.items():
        rows, up = [r for r in ref if in_config(r, cfg)], [r for r in upg if in_config(r, cfg)]
        t, u = totals(rows)
        tu, uu = totals(up)
        print(f"{title}: {len(rows)} lines, ${t:,.2f} priced, {u} unpriced; "
              f"upgrades {len(up)} lines, ${tu:,.2f} priced, {uu} unpriced")


if __name__ == "__main__":
    main()
