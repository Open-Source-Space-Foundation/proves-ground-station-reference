# Raspberry Pi facts that affect the station layer

Resolves wayfinder ticket #6. Every fact below was read from the cited primary source on 2026-10-18. The LA
station is a Pi 400 (`proves-electra-ops/stations/RUNBOOK.md`); the CI bench is a Pi 500; `station-check.sh`
and `collect-pass.sh` grep the kernel log for undervoltage and USB events because a GRC once dropped through a
hub (`proves-electra-ops/tools/README.md`).

## Hardware, per model

Sources: `[docs]` = https://www.raspberrypi.com/documentation/computers/raspberry-pi.html (sections "Power
supply", "Universal Serial Bus (USB)", "Real Time Clock (RTC)", "Power supply warnings"); product briefs are the
PDFs linked in each row.

| Fact | Pi 4 Model B | Pi 400 | Pi 5 | Pi 500 |
|---|---|---|---|---|
| Product brief | [RP-008344, published October 2026](https://pip-assets.raspberrypi.com/categories/545-raspberry-pi-4-model-b/documents/RP-008344-DS-7-raspberry-pi-4-product-brief.pdf) | [RP-008346, published April 2026](https://pip-assets.raspberrypi.com/categories/561-raspberry-pi-400/documents/RP-008346-DS-2-raspberry-pi-400-product-brief.pdf) | [RP-008348, published October 2026](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-8-raspberry-pi-5-product-brief.pdf) | [RP-008349, published April 2026](https://pip-assets.raspberrypi.com/categories/1115-raspberry-pi-500/documents/RP-008349-DS-4-raspberry-pi-500-product-brief.pdf) |
| RTC | None. Not in the spec list of the brief; `[docs]` RTC section opens "The Raspberry Pi 5 includes an RTC module." | None. Not in the brief's spec list nor the [specifications page](https://www.raspberrypi.com/products/raspberry-pi-400/specifications/). | Yes: "Real-time clock (RTC), powered from external battery" (brief, Specification). Works without a battery (`[docs]`). | Not listed. Neither the brief's spec list nor the [product page](https://www.raspberrypi.com/products/raspberry-pi-500/) names an RTC; `[docs]` RTC section names Pi 5 only. Treat as no battery-backed RTC. |
| Battery connector | None | None | "J5 (BAT) connector", two-pin JST, to the right of the USB-C power connector (`[docs]`). Official cell: [Raspberry Pi RTC Battery](https://www.raspberrypi.com/products/rtc-battery/), ML2020 rechargeable lithium-manganese, pre-fitted plug. Charging is off by default; enable with `dtparam=rtc_bbat_vchg=3000000` (`[docs]`). | None documented |
| USB current to peripherals | "1200mA total across all ports" (`[docs]`, Maximum power output table). Brief footnote: a 2.5A PSU is only acceptable "if downstream USB peripherals consume less than 500mA in total". | 1.2A maximum total USB peripheral current (`[docs]`, Typical power requirements table) | 1.6A with a 5A USB-PD supply, 600mA "when connected to any other compatible power supply" (`[docs]`). The fan header shares that budget. Check with `vcgencmd get_config usb_max_current_enable`. | 1.6A (600mA with a 3A supply), per the same table (`[docs]`) |
| Official PSU | [Raspberry Pi 15W USB-C Power Supply](https://www.raspberrypi.com/products/type-c-power-supply/), 5.1V/3.0A, "our recommended way to power Raspberry Pi 4 and Raspberry Pi 400". Brief: "minimum 3A". | Same 15W 5.1V/3.0A supply; `[docs]` recommends 3.0A | [Raspberry Pi 27W USB-C Power Supply](https://www.raspberrypi.com/products/27w-power-supply/), 5.1V/5.0A plus 9V/12V/15V PD profiles; `[docs]` recommends 5.0A. The [45W supply](https://www.raspberrypi.com/products/45w-power-supply/) also offers 5.1V/5.0A. | `[docs]` recommends 5.0A; the Desktop Kit ships the 27W supply ([launch post, 2024-12-09](https://www.raspberrypi.com/news/raspberry-pi-500-and-raspberry-pi-monitor-on-sale-now/)). The bare unit ships no PSU (brief, Buying options). |
| Typical bare-board current | 600mA | 800mA | 800mA | 800mA (`[docs]`, Typical power requirements table) |
| Undervoltage reporting | Same on all four. `[docs]` "Power supply warnings": every model since the B+ (2014) except the Zero range has "low-voltage detection circuitry that will detect if the supply voltage drops below 4.63 V (±5%)", and "This will result in an entry being added to the kernel log." The kernel driver `drivers/hwmon/raspberrypi-hwmon.c` logs `dev_crit "Undervoltage detected!"` and `dev_info "Voltage normalised"` on each edge of the sticky bit ([rpi-6.18.y, line 51-53](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/drivers/hwmon/raspberrypi-hwmon.c), head 5d64d1e on 2026-10-18). `vcgencmd get_throttled` bit 0 = undervoltage now, bit 16 = undervoltage has occurred ([os docs](https://www.raspberrypi.com/documentation/computers/os.html#get_throttled)). | | | Pi 5 / 500 only: the bootloader also exposes `/proc/device-tree/chosen/power` with `max_current`, `usb_max_current_enable`, `usb_over_current_detected` (any USB over-current before the OS took over) and `reset_event` (PMIC reset reason, e.g. "over- or under-voltage") (`[docs]`, Power supplies and Raspberry Pi OS). |

## Software

| Fact | Value | Source (read 2026-10-18) |
|---|---|---|
| Current Raspberry Pi OS Lite (64-bit) | Release 6 Oct 2026, kernel 6.18, Debian 13 (trixie), 525 MB download | https://www.raspberrypi.com/software/operating-systems/ |
| Release notes | 2026-10-06 entry: "Linux kernel 6.18.50"; 2025-10-01 entry: "Based on Debian Trixie release"; 2023-10-10: "Based on Debian bookworm release" | https://downloads.raspberrypi.com/raspios_lite_arm64/release_notes.txt (fetched with curl; the host returns 403 to some fetchers) |
| Legacy image | "Legacy Lite (64-bit)" is still published, 6 Oct 2026, kernel 6.12, Debian 12 (bookworm) | same operating-systems page |
| Where 64-bit packages come from | pi-gen `arm64` branch, `RELEASE=trixie`: `stage0/00-configure-apt/files/debian.sources` points at `http://deb.debian.org/debian/` (trixie, trixie-updates, trixie-security; main contrib non-free non-free-firmware) plus `raspi.sources` at `http://archive.raspberrypi.com/debian/` | https://github.com/RPi-Distro/pi-gen/tree/arm64/stage0/00-configure-apt/files (branch head d346cd5, 2026-10-06) |
| What the Pi archive adds | `archive.raspberrypi.com/debian dists/trixie main binary-arm64` lists 1477 packages; none named chrony, hamlib, libhamlib*, tailscale, ntp or timesync. Those come from Debian or a vendor repo. | https://archive.raspberrypi.com/debian/dists/trixie/main/binary-arm64/Packages.gz |
| Default time sync on Lite | pi-gen `stage1/03-install-packages/00-packages` installs `systemd-timesyncd`; stage 2 ("lite system") adds no chrony. So a stock Lite image runs timesyncd, and `timedatectl` is the right check. | https://github.com/RPi-Distro/pi-gen/blob/arm64/stage1/03-install-packages/00-packages ; README "Stage 2 - lite system" |
| chrony | `apt install chrony` from Debian trixie: version 4.6.1-3+deb13u2. (bookworm: 4.3-2+deb12u3) | https://packages.debian.org/trixie/chrony |
| hamlib | Debian trixie ships source `hamlib` 4.6.2-1: `libhamlib4t64` 4.6.2-1+b1, `libhamlib-utils` 4.6.2-1+b1 (rigctl, rigctld, rotctl, rotctld, ...), `python3-hamlib` 4.6.2-1+b1. This meets the "4.5 or later" requirement. Bookworm has 4.5.4-1+b1 (`libhamlib4`, `libhamlib-utils`). There is no `hamlib-utils` package; the binary is `libhamlib-utils`. | https://packages.debian.org/trixie/libhamlib-utils ; https://packages.debian.org/search?keywords=hamlib&searchon=names&suite=all&section=all |
| Tailscale | Not in Debian (only `python3-tailscale`, `golang-github-tailscale-*-dev`). Tailscale publishes a "Raspbian Trixie (for Raspberry Pi)" repo: `https://pkgs.tailscale.com/stable/raspbian trixie main`, with an arm64 index; newest version listed 1.104.1. Install via the keyring + list commands on the packages page or `curl -fsSL https://tailscale.com/install.sh \| sh`. | https://pkgs.tailscale.com/stable/ ; https://pkgs.tailscale.com/stable/raspbian/dists/trixie/main/binary-arm64/Packages ; https://packages.debian.org/search?keywords=tailscale&searchon=names&suite=all&section=all ; https://tailscale.com/kb/1031/install-linux |

## What this changes

1. **No RTC on the Pi 400 (LA) or Pi 500 (bench).** The runbook's rule "The Pi has no RTC" holds for both, and
   only a Pi 5 with the RTC Battery changes it. The playbook keeps the clock-synchronized gate before every pass.
2. **Stock Lite runs systemd-timesyncd, not chrony.** If the station manifest wants chrony (4.6.1 in trixie), the
   provisioning step must install it and let it replace timesyncd; otherwise write the check against `timedatectl`.
3. **USB budget is 1.2A on Pi 4/400 and 600mA on Pi 5/500 behind a non-PD supply.** A GRC plus a rotator
   interface plus a hub on a 3A-supplied Pi 500 shares 600mA. The BOM must pair a Pi 5/500 with the 27W (5.1V/5A
   PD) supply, or the layout must put the hub on its own power.
4. **Undervoltage is logged as `Undervoltage detected!` at 4.63 V on every model;** `vcgencmd get_throttled`
   bits 0 and 16 and, on Pi 5/500, `/proc/device-tree/chosen/power` give the acceptance checks something to read.
5. **hamlib 4.6.2 and chrony 4.6.1 install from stock Debian trixie repos; Tailscale needs its own apt repo.**
   The software manifest can pin `libhamlib-utils` (not `hamlib-utils`) and must add the Tailscale repo step.

Note: this repo's other fact notes live in `docs/notes/`; this file is at `docs/research/` because ticket #6 asked
for that path.
