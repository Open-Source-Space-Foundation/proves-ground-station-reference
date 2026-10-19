# proves-ground-station-reference
## Hardware BOM

The station has one hardware BOM with two antenna configurations: `single` (one antenna transmits and receives, as at LA) and `split` (separate TX and RX antennas on one rotator, as at Borrego). See ADR 0003. The sources live in `bom/`:

- `reference.csv` is the hardware BOM. Its `config` column says whether a line is in `all` configurations, `single` only or `split` only.
- `upgrades.csv` is the recommended-upgrades list (ADR 0001), with the same columns.
- `rf_chains.csv` lists every RF path, antenna to radio, with each part's in and out connector.
- `topology.json` holds the block diagram: blocks, their positions and links per configuration.
- `bom.template.html` is the page template.

The CSVs import directly into Google Sheets. `docs/bom.md` and `docs/bom.html` are generated; edit the sources, then regenerate:

```
python3 -I bom/render.py
```

The script uses only the standard library and prints one summary line per configuration. It refuses to render if:

- a CSV column is missing or out of order;
- a `status`, `config` or `flag` value is outside its set, a `qty` is not an integer, or a price is neither a number nor `?`;
- an item name appears twice in `reference.csv` and `upgrades.csv` taken together;
- a line's `block` has no position in `topology.json` for a configuration the line belongs to;
- `topology.json` lacks positions, links or bands for a configuration, a block lacks a label, icon or role, a position is not an `[x, y]` pair inside one of that configuration's bands, or a link names an unpositioned block or an unknown kind;
- an item, purpose, substitute or note carries what looks like a device serial number, in either case, that is not some row's part number;
- a chain in `rf_chains.csv` is missing, names an item outside its configuration, or has a junction where one part's out connector does not mate the next part's in connector (same family, N or SMA, opposite gender);
- a `reference.csv` row in an RF block (antenna, LNA, coax, arrestor, adapter, GRC, SWR meter, bench, and their RX twins) is in no chain of a configuration it belongs to, unless `render.py` lists it in `NOT_RF`.

`docs/bom.html` has three views: an order sheet for buyers, a clickable system map and a pass trace for developers. `?view=order`, `?view=map` and `?view=trace` open each one.

The live page is at <https://open-source-space-foundation.github.io/proves-ground-station-reference/>. The `BOM` workflow (`.github/workflows/bom.yml`) builds and deploys it on each push to `main`. The site holds only the rendered page and the three CSVs, so `reference.csv`, `upgrades.csv` and `rf_chains.csv` each have a stable URL next to the page. The page's "Download CSV" link points at the served `reference.csv`. It resolves on the site; when you open `docs/bom.html` locally, the CSV is in `bom/`.

CI fails a pull request whose committed `docs/bom.md` or `docs/bom.html` differs from a fresh render, or whose CSVs fail one of the checks above. Run `python3 -I bom/render.py` and commit its output with your CSV change.
