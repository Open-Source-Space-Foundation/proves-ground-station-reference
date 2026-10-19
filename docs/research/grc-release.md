# GRC firmware release state and which build LA runs

Research for wayfinder ticket #5 (part of map #2), checked 2026-10-18 against the
`ground-radio-controller` GitHub repo, the local worktree `~/GitHut/grc-radio-stick-v2`,
the archived old clone bundle, and `proves-electra-ops`. `GRC` = the repo
https://github.com/Open-Source-Space-Foundation/ground-radio-controller (default branch `main`,
HEAD `f3b3985`, pushed 2026-10-12T06:23:57Z, per `gh api repos/...`).

## Answer in one table

| Question | Answer | Evidence |
|---|---|---|
| Any tagged release with a `.uf2`? | Yes, two: `v0.0.1` and `v0.0.2`, each with one `zephyr.uf2`. Both are V1-board (`ground_radio_controller`) images; the V2 board did not exist yet. | `gh release list`; [release assets](#releases-and-tags) |
| Can a new **V1** station flash a reproducible image today? | Only an old one. `v0.0.2` is 21 commits behind the firmware LA runs (`e8b2d44`), and the `e8b2d44` `.uf2` LA runs is published nowhere (only in `~/grc-build/grc-main` on the station). | compare `v0.0.2...e8b2d44` = ahead 21; `known-good.toml:37` |
| Can a new **V2** station flash a reproducible image today? | No. No release, no CI build, no saved `.uf2`; the LA V2 runs a `-dirty` build and no `.uf2` was kept. | `known-good.toml:43,48`; `radio-stick-v2/PROVENANCE.md:28-29` |
| LA V1 `v0.0.2-21-ge8b2d44` | `e8b2d441f56eab0b5ccf9b9a748dfec1fce3b46c`, 2026-07-11, "fix #16: Packets get stuck in FrameAccumulator buffer when GRC is overwhelmed". Was `main`'s tip from 2026-07-11 to 2026-10-12. Clean build. | `gh api repos/.../commits/e8b2d44`; `v0.0.2...main` log |
| LA V2 `v0.0.2-23-g7957c90-dirty` | `7957c9056c65c2c09a5863b13c3e07a45945d74d`, 2026-09-26, "feat: add PROVES Radio Stick V2 board support", 2nd commit of PR #26 (`feat/radio-stick-v2-board`), merged to `main` 2026-10-12 as `731d247`. `-dirty` = `settings.ini` BOARD line edited in the build tree. | `gh pr view 26`; `known-good.toml:48`; `PROVENANCE.md:7-16` |
| `patches/` upstream? | No. Only `zephyr-sx126x-wakeup-busy-delay.patch` is on GitHub `main`; the two RX patches exist only on the unpushed local branch `fix/radio-stick-v2-rx` (`a888d4f`). Zephyr upstream `main` has none of the three; it did add a separate `lora_rssi()` API after v4.3.0. | [Patches](#patches) |

## Releases and tags

| Tag | Tag commit | Published | Asset | Size | Board (from `settings.ini` at tag) | Release body |
|---|---|---|---|---|---|---|
| `v0.0.1` | `e1796cc` ("allow missing testconfig", 2026-06-25) | 2026-06-25T23:09:30Z | [zephyr.uf2](https://github.com/Open-Source-Space-Foundation/ground-radio-controller/releases/download/v0.0.1/zephyr.uf2) | 818,176 B | `ground_radio_controller/rp2350a/m33` (`settings.ini:10` @v0.0.1) | "Find attached an initial imperfect UF2" |
| `v0.0.2` | `58b16e5` | 2026-07-02T03:25:34Z | [zephyr.uf2](https://github.com/Open-Source-Space-Foundation/ground-radio-controller/releases/download/v0.0.2/zephyr.uf2) | 686,080 B | `ground_radio_controller/rp2350a/m33` (`settings.ini:10` @v0.0.2) | "v0.0.2" |

- `boards/proves/` at `v0.0.2` and at `e8b2d44` contains only `ground_radio_controller` and `proves_flight_control_board_v5`; `proves_radio_stick_v2` appears on `main` only after PR #26 (`gh api repos/.../contents/boards/proves?ref=...`).
- No release workflow exists. `.github/workflows/ci.yaml` (the only workflow) runs `make fmt` and `make build` on PRs and pushes to `main` and uploads `build-artifacts/` as a 90-day workflow artifact (`ci.yaml:31-39`).
- Releases do not record the submodule pins, the board, the dictionary, or a hash.

## Commit lineage

```
v0.0.2 (58b16e5, 2026-07-02, release .uf2, V1 board, fprime pin 751ed50)
  │  +20 commits (CI, portable builds PR #17, SCIDs, fprime pin -> 1f8a838)
  ▼
e8b2d44  2026-07-11  fix #16 FrameAccumulator          <- LA V1 "v0.0.2-21-ge8b2d44" (clean)
  │                                                      main's tip 2026-07-11 .. 2026-10-12
  ├─ 6d94e3c  2026-09-26  select LoRa driver from DT + SX126x wake-up patch   (PR #26)
  ├─ 7957c90  2026-09-26  add Radio Stick V2 board      <- LA V2 "v0.0.2-23-g7957c90-dirty"
  │     │                                                  (settings.ini BOARD edited)
  │     ├─ 3760731 ┐ 2026-10-03  rx-boosted patch
  │     ├─ 30059dc │ 2026-10-03  rx-diagnostics patch + RadioDiag (packet 7)   fix/radio-stick-v2-rx
  │     ├─ 0415bee │ 2026-10-03  MAX_PACKETIZER_CHANNELS                        (LOCAL ONLY, not on GitHub)
  │     └─ a888d4f ┘ 2026-10-03  SX127x RSSI + NULL guard   <- bench V2 "v0.0.2-27-ga888d4f-dirty"
  ├─ 6b56a14  2026-10-12  V2 cleanup (end of PR #26)
  ├─ 59e7eb8, b40d199     uplink frame headroom (PR #28)
  ├─ 731d247  2026-10-12  Merge PR #26
  ▼
f3b3985  2026-10-12  Merge PR #28  = main HEAD  (CI dictionary reports projectVersion "f3b3985")

fcfff6a  2026-07-12  Merge PR #24 on feat/v5e-board-support  <- V1's PREVIOUS firmware "fcfff6a-dirty"
         (diverged: 5 ahead / 44 behind main; full-flash backup in electra-ops bench/)
```

Sources: `gh api repos/.../compare/v0.0.2...main` (28 commits, list in that response), `compare/v0.0.2...e8b2d44` ahead 21, `compare/v0.0.2...7957c90` ahead 23, `compare/main...7957c90` behind 5, `compare/main...fcfff6a` diverged 5/44, `gh pr view 26 --json commits`, and `git --git-dir=<bundle clone> log 7957c90..a888d4f` on the archived bundle (below).

## What the two LA boards run

| Board (USB S/N) | Version string | Commit | Board target | Clean? | `.uf2` kept? | Source |
|---|---|---|---|---|---|---|
| Radio Stick V1 (`AE2083CECDFE03E5`) | `v0.0.2-21-ge8b2d44` | `e8b2d44` on `main` | `ground_radio_controller/rp2350a/m33` | yes | sha256 `84c83f80eca9990ccc0b05876353a1e41d8f55492955cd14d1ee94f6cadd6242`, file only at `~/grc-build/grc-main/build-artifacts/zephyr.uf2` on the station | `proves-electra-ops/stations/known-good.toml:30-39`; `tools/grc-dicts/radio-stick-v1-grc-main-e8b2d44/PROVENANCE.md:3-5` |
| Radio Stick V1, previous firmware | `fcfff6a-dirty` | `fcfff6a` (feat/v5e-board-support) | unknown | no | full 16 MiB flash dump `bench/v1-firmware-backup/AE2083CECDFE03E5-flash-2026-10-03.bin`, sha256 `3e881472a5fe8aab36dcf69f2d872f2d048edbff635c90aba92b228aeb986c47` | `known-good.toml:39`; `bench/v1-firmware-backup/*.sha256` |
| Radio Stick V2 (`A30C2CA5609E616A`) | `v0.0.2-23-g7957c90-dirty` | `7957c90` (then branch tip of `feat/radio-stick-v2-board`, now on `main`) | `proves_radio_stick_v2/rp2350a/m33` | no: `settings.ini` BOARD line edited | no: "No .uf2 saved: back up the board with `picotool save -a` and rebuild clean" | `known-good.toml:41-50`; `tools/grc-dicts/radio-stick-v2/PROVENANCE.md:3-29` |
| Bench V2 (this Mac, worktree `~/GitHut/grc-radio-stick-v2`) | `v0.0.2-27-ga888d4f-dirty` | `a888d4f` on local branch `fix/radio-stick-v2-rx` | `proves_radio_stick_v2/rp2350a/m33` (`settings.ini:10`) | no | `build-artifacts/zephyr.uf2`, 693,248 B, 2026-10-03 14:57, sha256 `ce6f440049c99de163fbc976d02f9163ac52298a3e336257820523a11e0597ba` | `build-artifacts/zephyr/fprime-zephyr-deployment/dict/ReferenceDeploymentTopologyDictionary.json` `metadata` |

Notes on the "-dirty" flag:

- `settings.ini` on `main` still selects `BOARD=ground_radio_controller/rp2350a/m33` with the V2 line commented out (`settings.ini:10-13` at `main`; same text in the worktree). The README tells V2 builders to edit the file (`README.md:141-147`). So every V2 build from a clean checkout is `-dirty` by construction; the flag cannot be removed without a repo change (per-board settings, or BOARD as a build argument).
- `patches/README.md` says the wake-up patch is **required** for the V2 (`patches/README.md:9-10`) and is applied with `git apply` inside the zephyr submodule (`patches/README.md:23-30`), which also dirties the superproject. The two provenance records say `settings.ini` was the only change, but the dictionary-only build they describe never applied a patch (`PROVENANCE.md:25-29`). Whether the LA V2 image has the wake-up patch applied is therefore not recorded; the `~/grc-build` trees are on the station, not on this Mac (`ls ~/grc-build` fails here; the LA Pi and bench Pi refused SSH with publickey on 2026-10-18).
- `tools/preflight.py:186-194` fails any `-dirty` version unless the board has `allow_dirty`, and compares `project_version`, `framework_version`, `library_versions` as exact strings.

## Pins

Submodule pointers from `gh api repos/.../git/trees/<ref>?recursive=1` (mode `160000`). They are identical at `e8b2d44`, `7957c90`, and `main`:

| Submodule | Pin at `e8b2d44` / `7957c90` / `main` | Pin at `v0.0.2` | What it is |
|---|---|---|---|
| `lib/fprime` (OSSF fork) | `1f8a838e5acfba4a5788f8f8ac42e7faedeee86e` | `751ed505dcfa47e42c8304e5ae5f1238f88cd838` | "add configuration option to CcsdsTcFrameDetector to accept all SCID", 2026-07-07; 29 ahead of `nasa/fprime` `v4.2.0` (`f972bed`), hence `v4.2.0-29-g1f8a838e5a` |
| `lib/fprime-zephyr` | `7f879a8a5ce28f0d213dc36bff0c3ceef0c102e3` | same | "Add LoRa SET_FREQ command [UNSAFE; NOTE BELOW]", 2026-04-18; 79 commits behind `fprime-zephyr` `main` as of 2026-10-17 |
| `lib/zephyr-workspace/zephyr` | `3568e1b6d5cdd51a6b964a2a1d6d29200fea2056` | same | Zephyr `v4.3.0` (annotated tag `981205b` -> `3568e1b`); `west.yml:20` also says `revision: v4.3.0` |
| `loramac-node` (west module) | `fb00b383072518c918e2258b0916c996f2d4eebe` | | `west.yml:37` |
| `hal_rpi_pico` (west module) | `09e957522da60581cf7958b31f8e625d969c69a5` | | `west.yml:56` |

Version-string gotchas a release must handle:

- The OSSF `fprime` fork has **no tags** (`git ls-remote --tags` returns 0 refs). The `v4.2.0-29-g…` framework string only appears when the builder's `fprime` clone carries nasa's tags. The CI build of `main` reports `frameworkVersion "1f8a838e5"` and `projectVersion "f3b3985"` (dictionary in workflow artifact of run 38212329416), because `actions/checkout` defaults to depth 1 without tags (`ci.yaml` sets no `fetch-depth`/`fetch-tags`). Either string set is valid, but `preflight.py:186` demands an exact match with `known-good.toml`.
- The CI artifact for `main` (`build-artifacts`, run 38212329416, 7.2 MB, expires 2027-01-10) contains a `zephyr.uf2` (sha256 `636a92dadcb4751db13065e5dbcf091b99e47b28f560713d9ae2823e1a5de0cd`) for the **V1** board only (`zephyr.dts` in it cites `boards/proves/ground_radio_controller/ground_radio_hardware.dtsi`). Nothing in CI builds the V2.

## Patches

Local `patches/` (worktree and `a888d4f`) versus GitHub:

| Patch | Purpose (from `patches/README.md`) | On GitHub `main`? | Added by | In upstream Zephyr `main`? |
|---|---|---|---|---|
| `zephyr-sx126x-wakeup-busy-delay.patch` | `k_busy_wait(500)` after SX126x wake-up so `SET_FREQ` is not silently dropped (~40% failure measured on v5e); required for v5e and Radio Stick V2 (`README.md:7-21`) | **Yes** (`contents/patches?ref=main` lists `README.md`, this patch) | `6d94e3c` (PR #26) | **No**: `drivers/lora/loramac-node/sx126x.c` `SX126xWakeup()` at line 377 on `main` has no `k_busy_wait`. `README.md:41` says it "should be submitted to upstream Zephyr"; no Zephyr PR found (`gh search prs`) |
| `zephyr-sx126x-rx-boosted.patch` | honour devicetree `rx-boosted` (REG_RX_GAIN 0x96, about +3 dB) on SX126x (`README.md:46-60`) | **No** | `3760731` on `fix/radio-stick-v2-rx` (local only) | **No** for the loramac-node driver: `rx_boosted` appears only in `drivers/lora/native/sx126x/*` and `lora-basics-modem/*` (`gh search code`). The binding property exists (`dts/bindings/lora/semtech,sx126x-base.yaml:63`) but loramac-node ignores it |
| `zephyr-lora-rx-diagnostics.patch` | `lora_diag.h`: RX stats (CRC/header errors, frame lengths) and instantaneous RSSI; feeds the `RadioDiag` component, telemetry packet 7 (`README.md:63-90`) | **No** | `30059dc` on `fix/radio-stick-v2-rx` (local only) | **No** `lora_diag.h` upstream. Upstream did add a `lora_rssi()` API (`include/zephyr/drivers/lora.h` `lora_api_rssi`, `sx12xx_common.c` `sx12xx_lora_rssi`) in [zephyr#113278](https://github.com/zephyrproject-rtos/zephyr/pull/113278), merged 2026-08-28, after the pinned v4.3.0 (`lora.h` at v4.3.0 has no `lora_api_rssi`) |

The unpushed branch: `fix/radio-stick-v2-rx` = `a888d4f396a3e74860b711b19f43e6b19b709e1c`, 4 commits on `7957c90`, `git describe` `v0.0.2-27-ga888d4f`, 12 files, +575/-5 (RadioDiag component, packets, `TlmPacketizerCfg.hpp`, two patches). GitHub returns `No commit found for SHA: a888d4f`. The only copy besides the worktree is the bundle `/Volumes/nvme-1tb-m4/proves/grc-old-clone-archive-2026-10-17/ground-radio-controller-all.bundle` (`git bundle list-heads` shows `refs/heads/fix/radio-stick-v2-rx`); the parent clone it belonged to was deleted in the 2026-10-17 disk cleanup, which is why `git` fails in the worktree (`.git` -> `../ground-radio-controller/.git/worktrees/grc-radio-stick-v2`).

Patch effect on the version string: patches are applied as uncommitted changes inside the zephyr submodule (`patches/README.md:23-30`), never committed anywhere, so a patched image is `-dirty` and `git describe` cannot say which patches it carries.

## What a release must contain

So that `proves-electra-ops/stations/known-good.toml` (and a future station software manifest) can point at a release instead of a path on one Pi. Rules the manifest already states: change only after verification, no unidentifiable `-dirty` builds, "keep the .uf2 next to its hash (release asset or bench/)" (`known-good.toml:5-10`).

| # | Release content | Why | Where it comes from today |
|---|---|---|---|
| 1 | `zephyr-ground_radio_controller.uf2` (V1) + sha256 | the only board a station can currently flash from a release; LA V1 runs an unpublished `e8b2d44` build | CI `make build` already produces it for `main`; needs a tagged, full-history build |
| 2 | `zephyr-proves_radio_stick_v2.uf2` (V2) + sha256 | LA uplinks with the V2; nothing builds it today | needs a second build with `BOARD=proves_radio_stick_v2/rp2350a/m33` **without** editing `settings.ini` (e.g. per-board settings file or `fprime-util` `-D BOARD=` argument), and `patches/` applied before the build |
| 3 | Per-board `ReferenceDeploymentTopologyDictionary.json` + sha256 | `preflight.py:174-176` checks `dictionary_sha256`; the GRC GDS needs it | `build-artifacts/zephyr/fprime-zephyr-deployment/dict/` of each build |
| 4 | Expected version strings: `project_version`, `framework_version`, `library_versions` | `preflight.py:186-194` compares them exactly and rejects `-dirty` | from the dictionary `metadata`; requires a clean tagged checkout with tags fetched (`fetch-depth: 0`, `fetch-tags: true`) and either nasa's `v4.2.0` tag present in the fprime clone or the manifest written with the short-hash form |
| 5 | Pins: fprime `1f8a838e5a`, fprime-zephyr `7f879a8`, zephyr `v4.3.0` (`3568e1b`), loramac-node `fb00b38`, hal_rpi_pico `09e9575`, Zephyr SDK version | reproduce the image from source; the release page today records none of these | `git trees` of the tagged commit; `west.yml:20,37,56` |
| 6 | List of applied `patches/*.patch` with their sha256, and the LoRa link parameters they affect | a patched submodule is invisible to `git describe`; the wake-up patch is required for V2 | `patches/README.md` |
| 7 | Decision on `fix/radio-stick-v2-rx` (`a888d4f`): merge or drop before tagging | the bench V2 runs it; the LA V2 does not; it is on no remote | the bundle above, or push the branch |
| 8 | Build provenance: CI run URL, board, commit, date | `known-good.toml:5-7` requires saying how a version was verified | CI run metadata |

Minimum repo changes implied: a tag on a clean `main` commit at or after `f3b3985` (so the V2 board is in-tree), a board-matrix build in CI (V1 and V2) that applies `patches/`, full-history checkout, and a release job that attaches 1-6. Until then, the honest answer to "can a new station flash a reproducible GRC image today" is: a V1 can flash `v0.0.2` (old, 21 commits behind LA, missing fix #16) and nothing else is reproducible from published artifacts.

## Checked but not available

- `~/grc-build/grc-main` and `~/grc-build/grc-v2` (the LA build trees named in `known-good.toml:37,48`) are not on this Mac; `ssh proves@proves-la-gs.local` and `ssh proves@100.67.193.13` were refused (publickey) on 2026-10-18, so the exact dirty state and the V1 `.uf2` on the station were not re-verified here. The hashes above come from `known-good.toml` and the PROVENANCE files.
