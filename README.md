# proves-ground-station-reference
## Hardware BOM

The hardware BOM lives in `bom/uplink.csv`, `bom/receive.csv` and `bom/upgrades.csv`. Those CSVs are the source of truth and import directly into Google Sheets. `docs/bom.md` and `docs/bom.html` are generated; edit the CSVs, then regenerate:

```
python3 -I bom/render.py
```

The script uses only the standard library. It refuses to render if a column is missing, a status is not one of `proven`, `substitute`, `upgrade` or `untested`, or the receive station lists an item the uplink station does not.
