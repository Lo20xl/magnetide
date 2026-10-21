# Magnetide v21 — Print & Assembly Package

Generated 2026-10-20 from Fusion (MCP-driven build, verified programmatically).

## Contents

| File | What | Print notes |
|---|---|---|
| `printable/plate_top.stl` | Duct ceiling + tray lips (1 piece) | 1.5 mm base — brim ON, low fan, or it WILL warp |
| `printable/plate_bottom.stl` | Same, mirrored | same |
| `printable/rail_left.stl` / `rail_right.stl` | Electrode retainers / 14 mm spacers | print FLAT (14 mm footprint down), not on the 2 mm edge |
| `printable/bellmouth.stl` | 4-wall inlet flare, merged | print walls separately if supports-in-passage bother you: slices overlap 0.4 mm, each wall can be split at the X stations |
| `Magnetide-v21-printable.f3d` | Fusion archive, printable doc | |
| `Magnetide-v21-full.f3d` | Fusion archive, full assembly (96 tiles, graphite, hood) | |

Print PLA, 0.2 mm layers. Creality Hi bed is big enough for every part flat.

## Verified geometry (programmatic, exact)

- Duct 40.00 × 14.00 × 120 mm; Le/Dh = 5.8
- Graphite inner faces exactly ±20.00 (flush — zero protrusion into flow)
- Magnetic gap g = 17.00; block lm = 10.00 (2×5 mm tiles)
- 96 tiles, stations 20 mm with 0.4 mm clearance (tiles drop in)
- Bellmouth: parabolic flare 14→21 mm over 20 mm, zero slope at the duct joint
- 0 passage intruders, 0 interference pairs (point-containment sampling)

## Design decisions since the frozen spec

1. **Graphite is 125 mm (−5…120), not 120.** Extends 5 mm into the bellmouth
   so the x=0 butt joint has no crevice ring. You buy 125×14 stock or trim.
2. **Wire channel:** 0.4 mm gap between graphite outer face (21.5) and rail
   inner face (21.9) runs the full length and exits at both ends — route the
   electrode leads here, pot with epoxy. NO holes drilled in the wetted hull.
3. **Bellmouth slices overlap 0.4 mm** (was butt-jointed) — slicer union
   welds them solid; the old seams were potential leak lines.
4. **Hood clamps the magnet stacks:** hood inner face sits at z=±18.5,
   exactly on the stack tops. Epoxy each tile to the plate anyway — the
   hood closes the flux loop AND holds the pack down.

## Assembly order

1. Epoxy tiles to plate trays (mind N/S orientation — compass-check every
   station, all six must drive the same way).
2. Silicone-seal rails to plates (wetted joints = silicone, not superglue —
   superglue fails in brine).
3. Drop graphite plates in, leads into the rail channel, pot ends with epoxy.
4. Bellmouth to plates: silicone.
5. Hood on top, 4 end bars, cable-tie or strap. Hood contacts magnet faces —
   that's the flux path; keep insulation between hood and WIRES only.
6. Freshwater rinse after every run. Nickel-plated magnets + graphite +
   brine = galvanic cell; don't leave it soaking.

## Safety (from Cébron + spec §8)

- 3 A in brine makes Cl₂ at the anode and H₂ at the cathode. OUTDOOR,
  ventilated, ≤2 min runs, anode submerged, teacher aware. Gas bubbles in
  the duct also steal thrust — one more reason for short runs.
- Fuse the supply. N52 packs pinch.

## Known open items (bench, not CAD)

- **Operating point:** the cell wants ~9–10 A at 19 V short-circuit
  (R_cell ≈ 2 Ω in 100 g/L brine). The brick's 3.06 A cap is what actually
  sets the operating point; whether it's constant-current or hiccup-shutdown
  must be measured (V–I curve, Cébron's step 1). Trust the brick's behavior
  over any modelled voltage row.
- Level control < 1 mm + current-off control every session (1 mm = 9.8 Pa
  against a ~21 Pa budget).
- Timed collection for Q; dye front ≠ mean velocity (Cébron).
