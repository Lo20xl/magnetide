# Magnetide v21 — assembly package

All dimensions mm. Built with build123d (OCC kernel), so every file is
reproducible from `build.sh` without a CAD licence.

## 1. Full visualisation

| file | what |
|---|---|
| `Magnetide-v21-assembly.step` | **17 solids**: 2 steel clamshell halves, 2 magnet trays, 8 magnet bars, 2 liners, 2 graphite electrodes, 1 bellmouth |
| `Magnetide-v21-assembly.f3d` | same 17 bodies as named components in Fusion |
| `assembly-guide.pdf` / `.html` | 5-page build guide, every figure rendered from this model |
| `view_iso.png` | closed 3/4 from above-right |
| `view_exploded.png` | stack order, halves lifted |
| `view_half.png` | steel top off — magnets in their tray |
| `view_trays.png` | both trays alone (N face red, S face blue) |
| `view_channel.png` | open channel with the graphite electrode along the wall |
| `view_mouth.png` | end-on inlet, curved flare |
| `build_report.json` | measured size / volume / solid count per part + the channel-clearance probe |

## 2. Printable plastic (`plastic/`, 3 distinct files)

| file | qty | notes |
|---|---|---|
| `bellmouth.stl` | 1 | curved flare 48×30 mouth → 40×14 bore, 20 mm long |
| `tray.stl` | 2 | 124 × 52 × 10; one 40 mm pocket per face, cut through |
| `liner_top.stl` / `liner_bottom.stl` | 1 + 1 | 130 × 52 × 1.5 flat plate (identical — print twice) |

Print the tray at 0.2 mm layers, 3 perimeters. The pocket is cut through on
purpose: magnets must sit directly on the liner with nothing between them and
the channel. All four STLs verified watertight.

## Magnet packing

96 tiles of 20 × 10 × 5 N52, per face **24**: 6 along the length × 4 across ×
2 deep. The 4 across are 40 mm — the full channel width — so no part of the
bore is un-driven. Tiles butt edge to edge; only the tray's 2 mm end ledge
retains them.

## 3. Metal (`metal/`)

| file | what |
|---|---|
| `clamshell-flat.dxf` | laser-cut blank, **150 × 110.3 mm, cut 2 off** |
| `clamshell-flat.png` | preview of the same file |

One blank per half; the two halves are identical, one flipped. 2.0 mm mild
steel / SPCC. Bend 90° at Y = ±28.0 (plate/wall) and ±47.15 (wall/lug).
8 × Ø3.4 holes (M3 clearance). K = 0.44, R = 0.2 — the flat uses that
allowance, so check the first bend against a coupon before running the batch.

## Fit

| joint | clearance |
|---|---|
| magnet in tray pocket | 0.2 mm per side |
| tray inside steel cavity | 0 mm (clamped by the half) |
| liner on tray face | 0.5 mm bond line (epoxy) |
| electrode against channel wall | 0.1 mm per side |
| M3 bolt in lug | Ø3.4 hole |

## Not in this package

M3 bolts, the 96 magnets, graphite blanks, supply. See `docs/V21-FINAL-SPEC.md` in the repo for the BOM.
