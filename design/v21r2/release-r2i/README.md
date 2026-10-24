# Magnetide v21-r2i — MHD seawater pump

Conduction MHD pump for the Kelas 10.8 physics project. Seawater flows through a
40 × 14 mm bore, a 483 mT field crosses it, current runs between two graphite
electrodes, and the Lorentz force drives the water out the straight end.

**Envelope** 150 × 73 × 45 mm · **bore** 40 × 14 × 124 mm · **dry mass** ≈ 1.15 kg

---

## What's in this folder

| Path | What it is |
|---|---|
| `Magnetide-v21r2i-assembly.step` | Full assembly, 18 solids, mm units. Opens in Fusion/SolidWorks/FreeCAD. |
| `docs/Build-Instructions.pdf` | Picture-by-picture build manual — 7 numbered steps, one render each, pre-power checklist. |
| `docs/Design-Document.pdf` | Part list, sizes, tolerances, magnetic/electrical design, revision history. |
| `docs/archive/` | Earlier text-style assembly instructions (superseded). |
| `print/*.stl` | Four printable parts. Print settings are in the assembly guide. |
| `laser/clamshell-flat-3.0mm.dxf` | Folded yoke blank — 3.0 mm mild steel, R3 walls / R1.5 lugs. |
| `renders/` | Exploded, assembled and cutaway renders + `build_report.json`. |

## Print list

| Part | Qty | Size (mm) | Notes |
|---|---|---|---|
| `tray.stl` | 2 | 124 × 50.7 × 19.5 | closed magnet cavity, print floor down |
| `cap.stl` | 2 | 121.7 × 42.7 × 1.0 | 100 % infill, flat |
| `bellmouth.stl` | 1 | 20 × 52 × 39 | mouth up |
| `rear_block.stl` | 1 | 5.5 × 52 × 39 | flat face down |

PLA is fine for a demo run; PETG if the water is warm. The tray floor is 1.5 mm and
is the only thing keeping brine off the magnets — inspect it against a light.

## Laser list

| Part | Qty | Material |
|---|---|---|
| `clamshell-flat-3.0mm.dxf` | 2 | 3.0 mm mild steel (DC01 / SPCC / AISI 1008) |

Fold both long edges up 90° at ±28.5 on an R3 die, then fold the two lugs out 90° at ±44.06 on R1.5.
Blank is 95.57 × 150, K = 0.44, 8 × Ø3.4 holes. Per half 338 g, 676 g for the pair.

## Bought

- 96 × N52 tile 20 × 10 × 5 (nickel plated) — 48 per face, 2 layers deep
- 2 × graphite plate 134 × 14 × 2
- 8 × M3 × 14 bolt + nut + washer
- slow epoxy for the magnets and the lead exit

## Assembly in one paragraph

Fold two yokes. Epoxy 48 tiles into each tray cavity (compass-check every row), cap
them, slide the electrodes into their 1 mm grooves until the ends sit 5 mm inside the
end-block pockets, peg the bellmouth and rear block on, then bolt the two halves
together through the eight lug holes. Drill the blind lead channel through, thread the
wires, seal with epoxy.

## Before you power it

- 8 bolts seated, no gap at the lug faces
- Compass: rows on one face agree, the two faces oppose
- Tray floor unbroken over the whole magnet area
- Electrodes fully home, not shorted to steel
- Lead exit epoxied, bore clear down its 124 mm
- Fused supply, under 2 minutes per run, ventilated (Cl₂)

---

Revision r2i · model generated from the build script, dimensions read back from the
solid · bore and all leak paths probed on every rebuild.
