# Magnetide v21 — assembly package

All dimensions mm. Built with build123d (OCC kernel), so every file is
reproducible from `build.sh` without a CAD licence.

## 1. Full assembly (visualisation)

| file | what |
|---|---|
| `Magnetide-v21-assembly.step` | 15 solids: steel clamshell, trays, 6 magnet bars, 2 liners, 2 electrodes, bellmouth |
| `view_iso.png` | closed 3/4 from above-right |
| `view_open.png` | steel top + top tray hidden — magnet slots visible |
| `build_report.json` | measured size / volume / solid count per part + the channel-clearance probe |

## 2. Printable plastic (`plastic/`, 3 distinct files)

| file | qty | notes |
|---|---|---|
| `bellmouth.stl` | 1 | curved flare 48×30 mouth → 40×14 bore, 20 mm long |
| `tray.stl` | 2 | 124 × 52 × 10; 3 channels, 10 mm wide, for 20×10×5 tiles |
| `liner_top.stl` / `liner_bottom.stl` | 1 + 1 | 130 × 52 × 1.5 flat plate (identical — print twice) |

Print the tray at 0.2 mm layers, 3 perimeters. Channels are cut through on
purpose: the magnets must sit directly on the liner with nothing between them
and the channel.

## 3. Metal (`metal/`)

| file | what |
|---|---|
| `clamshell-flat.dxf` | laser-cut blank, **150 × 110.3 mm, cut 2 off** |

One blank per half; the two halves are identical, one flipped. 2.0 mm mild
steel / SPCC. Bend 90° at Y = ±28.0 (plate/wall) and ±47.15 (wall/lug).
8 × Ø3.4 holes (M3 clearance). K = 0.44, R = 0.2 — the flat uses that
allowance, so check the first bend against a coupon before running the batch.

## Fit

| joint | clearance |
|---|---|
| magnet in tray channel | 0.2 mm per side |
| tray inside steel cavity | 0 mm (clamped by the half) |
| liner on tray face | 0.5 mm bond line (epoxy) |
| electrode in liner pocket | 0.1 mm per side |

## Not in this package

M3 bolts, magnets themselves (order 96 × 20×10×5 N52), graphite blanks,
supply. See `docs/V21-FINAL-SPEC.md` in the repo for the BOM.
