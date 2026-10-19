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
# The BOM is published; device serials must not be. Mixed letter-digit run of 8+ chars, any case
# (USB serials such as the RP2350's print as lowercase hex).
SERIAL = re.compile(r"\b(?=[a-z0-9]*\d)(?=[a-z0-9]*[a-z])[a-z0-9]{8,}\b", re.I)
FREE_TEXT = ["item", "purpose", "substitute", "note"]
URL = re.compile(r"https?://\S+")
CHAIN_COLS = ["config", "chain", "item", "in", "out"]
CHAINS = [("single", "tx"), ("single", "tx-swr"), ("split", "tx"), ("split", "tx-swr"), ("split", "rx"), ("all", "bench")]
CONNECTORS = {"", "N-m", "N-f", "SMA-m", "SMA-f"}
RF_BLOCKS = {"antenna", "antenna_rx", "lna", "coax", "coax_rx", "arrestor", "arrestor_rx", "adapter", "adapter_rx",
             "grc", "grc_rx", "swr", "bench"}
# Parts that sit in an RF block on the map but carry no RF, so they join no chain: the LNA's DC feed.
NOT_RF = {"12 V DC supply for the mast LNA", "DC cable, shack to mast LNA, outdoor rated"}


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


def check_serials(files):
    """files: {csv name: rows}. A token that is some row's part number is a catalogue number, not a serial."""
    parts = " ".join(r["part"] for rows in files.values() for r in rows).casefold()
    for name, rows in files.items():
        for r in rows:
            for col in FREE_TEXT:
                for tok in SERIAL.findall(URL.sub("", r[col])):
                    if tok.casefold() not in parts:
                        sys.exit(f"{name}: {col} on {r['item']!r} carries {tok!r}, which looks like a device serial; "
                                 "publish the fact without the value")


def check_unique(files):
    """files: {csv name: rows}. Item names key rf_chains.csv, so they must be unique across both lists."""
    seen = {}
    for name, rows in files.items():
        for r in rows:
            if r["item"] in seen:
                where = f"more than once in {name}" if seen[r["item"]] == name else f"in both {seen[r['item']]} and {name}"
                sys.exit(f"item {r['item']!r} appears {where}")
            seen[r["item"]] = name


def mates(out, inp):
    """Same family, opposite gender: N-m mates N-f, never N-m or SMA-f."""
    return bool(out and inp) and out.split("-")[0] == inp.split("-")[0] and out != inp


def load_chains(items):
    """Return {(config, chain): [rows in path order]} after checking every junction mates."""
    with open(BOM / "rf_chains.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    chains = {}
    for r in rows:
        if list(r) != CHAIN_COLS:
            sys.exit(f"rf_chains.csv: columns must be {CHAIN_COLS}")
        name = f"{r['config']}/{r['chain']}"
        if (r["config"], r["chain"]) not in CHAINS:
            sys.exit(f"rf_chains.csv: unknown chain {name!r}; expected one of {[f'{c}/{n}' for c, n in CHAINS]}")
        if r["item"] not in items:
            sys.exit(f"rf_chains.csv: {name}: {r['item']!r} is not in reference.csv")
        if items[r["item"]]["config"] not in ("all", r["config"]):
            sys.exit(f"rf_chains.csv: {name}: {r['item']!r} is config {items[r['item']]['config']}, not in {r['config']}")
        for side in ("in", "out"):
            if r[side] not in CONNECTORS:
                sys.exit(f"rf_chains.csv: {name}: {r['item']!r} {side} {r[side]!r} is not one of {sorted(CONNECTORS - {''})}")
        chains.setdefault((r["config"], r["chain"]), []).append(r)
    for key in CHAINS:
        name = "/".join(key)
        path = chains.get(key)
        if not path:
            sys.exit(f"rf_chains.csv: chain {name} is missing")
        if path[0]["in"] or path[-1]["out"]:
            sys.exit(f"rf_chains.csv: {name}: path ends must have no connector; "
                     f"{path[0]['item']!r} in {path[0]['in']!r}, {path[-1]['item']!r} out {path[-1]['out']!r}")
        for a, b in zip(path, path[1:]):
            if not mates(a["out"], b["in"]):
                sys.exit(f'{name}: "{a["item"]}" out {a["out"] or "(none)"} does not mate "{b["item"]}" in {b["in"] or "(none)"}')
    for it in NOT_RF:
        if it not in items or items[it]["block"] not in RF_BLOCKS:
            sys.exit(f"render.py: NOT_RF names {it!r}, which is not a reference.csv row in an RF block; drop it from NOT_RF")
    chained = {(r["item"], cfg) for (c, _), path in chains.items() for r in path for cfg in (list(CONFIGS) if c == "all" else [c])}
    for it, r in items.items():
        if r["block"] not in RF_BLOCKS or it in NOT_RF:
            continue
        for cfg in configs_of(r):
            if (it, cfg) not in chained:
                sys.exit(f"reference.csv: {it!r} is in RF block {r['block']!r} but in no {cfg} chain of rf_chains.csv; "
                         "add it to its RF path with its connectors")
    return chains


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


def md_chains(chains):
    out = ["", "## RF chains", "",
           "Every junction from the antenna, or the source radio on the bench, to the receiving radio. "
           "`render.py` refuses to render unless each out connector mates the next in connector.", ""]
    for cfg, chain in CHAINS:
        path = chains[(cfg, chain)]
        title = "All configurations" if cfg == "all" else CONFIGS[cfg][0]
        out += [f"### {title}: {chain}", "", "| From | Out | In | To |", "|---|---|---|---|"]
        out += [f"| {md_cell(a['item'])} | {a['out']} | {b['in']} | {md_cell(b['item'])} |" for a, b in zip(path, path[1:])]
        out.append("")
    return out


def render_md(ref, upg, chains):
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
    out += md_chains(chains)
    return "\n".join(out).rstrip() + "\n"


def render_html(ref, upg, topo):
    data = {"configs": {k: v[0] for k, v in CONFIGS.items()}, "reference": ref, "upgrades": upg, "topology": topo}
    # "</" would close the inline <script> early.
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (BOM / "bom.template.html").read_text().replace("/*__DATA__*/null", blob)


def main():
    topo = json.loads((BOM / "topology.json").read_text())
    check_topology(topo)
    ref, upg = load("reference", topo), load("upgrades", topo)
    files = {"reference.csv": ref, "upgrades.csv": upg}
    check_unique(files)
    check_serials(files)
    chains = load_chains({r["item"]: r for r in ref})
    (ROOT / "docs" / "bom.md").write_text(render_md(ref, upg, chains))
    (ROOT / "docs" / "bom.html").write_text(render_html(ref, upg, topo))
    for cfg, (title, _) in CONFIGS.items():
        rows, up = [r for r in ref if in_config(r, cfg)], [r for r in upg if in_config(r, cfg)]
        t, u = totals(rows)
        tu, uu = totals(up)
        mated = [c for c_cfg, c in chains if c_cfg in ("all", cfg)]
        print(f"{title}: {len(rows)} lines, ${t:,.2f} priced, {u} unpriced; "
              f"upgrades {len(up)} lines, ${tu:,.2f} priced, {uu} unpriced; RF chains mate: {', '.join(mated)}")


if __name__ == "__main__":
    main()
