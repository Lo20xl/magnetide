# Magnetide v21 — Two Print-Ready Designs + Simulation Report

Generated 2026-10-20 from Fusion (MCP-driven build, verified programmatically).
Both designs share the frozen v21 internals (spec-exact); they differ in
joinery style and outer shape.

## Contents

```
design-a/                    Design A — SIMPLE
  printable/*.stl            10 print-ready parts
  Magnetide-A-printable.f3d
  Magnetide-A-full.f3d       + 96 tiles, graphite, hood (visualization)
design-b/                    Design B — COMPLEX (hydrodynamic fairing)
  printable/*.stl            16 print-ready parts
  Magnetide-B-printable.f3d
  Magnetide-B-full.f3d
README-old-single-design.md  previous single-design notes (kept)
```

## Design A — SIMPLE (interlocking, no fairing)

| Part | Qty | Notes |
|---|---|---|
| plate_a / plate_b | 2 | duct ceiling/floor with rail slots + magnet tray lips; B is mirrored |
| rail_left / rail_right | 2 | slide in from rear; captured axially by front flange + rear cap; wire channel beneath (y 21.5–21.9) |
| bellmouth_top/bottom/left/right | 4 | parabolic inlet flare 14→21 mm over 20 mm, slices overlap-welded |
| front_flange | 1 | ring, glues to mouth; axially captures rails |
| rear_cap | 1 | ring with center cut; bridges plate lip ends, captures rails |

**Joinery:** rails slide in x, captured by flange (front) and cap (rear);
graphite sandwiched between lip (inner) and rail (outer) with defined
clearances; magnet trays capture tiles laterally; hood clamps stacks.
Silicone only on wetted seams — no superglue in brine.

## Design B — COMPLEX (hydrodynamic fairing)

Design A core + 4-wall streamlined fairing (elliptical 30 mm nose,
power-law 70 mm tail, 5→1.2 mm variable shell) + nose/tail bulkheads.
Fairing inner faces clear every core part ≥0.5 mm.

**Why:** at boat speed the exposed A-box costs ~19 mN of 37 mN seawater
thrust (52%); the faired B costs ~0.7 mN (2%). Same internals, −96% drag.

## Recheck log (visual + logical + programmatic, 01:45)

Three defects were caught and fixed after the first build:

1. **Bulkhead axis-swap** — nose/tail bulkheads were built with swapped
   sketch axes (z ±27.2 pierced the fairing walls). Root cause: a double
   `(v,u)` coordinate remap. Fixed; interference now 0/27 containment pts.
2. **Inverted nose taper** — the old `cos()` profile gave a *fat tip* with a
   step at x=0 (mushroom). Replaced with `sqrt(2u−u²)` elliptical: thin
   1.2 mm lip at tip → 5 mm at base, zero slope at the joint.
3. **Boxy silhouette** — inner faces were constant (y±26/z±20.5), so the
   only taper was shell thickness: 15% narrowing, visually a box. Inner
   envelope now tapers too (tail runs to a needle at x=190; nose encloses
   the 23.5×10.5 inlet mouth). Loft stations sit exactly on the kinks
   (x=−22, x=122) so the piecewise envelope is never under-approximated.
   Side walls span z±h (between top/bottom walls) — no corner overlap.

Verifier hardening from the same recheck: duct-height check restored
(silently lost in a rename), interference sampling now requires the point
inside *both* bodies (bbox-only sampling false-positived on tapered lofts),
same-wall slice pairs exempt (their 0.4 mm weld overlap is by design).

Final state: Design A 10 STLs / B 16 STLs, non-manifold edges **0/0**,
interference 0, passage intruders 0, all .f3d archives post-date their
STLs. Vision verdict on B: "streamlined pod — watertight, no artifacts."

## Verified geometry (programmatic, exact)

- Duct 40.00 × 14.00 × 120; Le/Dh = 5.8
- Graphite inner faces exactly ±20.00 (flush, zero flow protrusion)
- g = 17.00; lm = 10.00 (2×5 tiles); 96 tiles × 5.00; station slack 0.40
- Fit table 7/7 OK (0.1–0.4 mm clearances on every joint)
- 0 passage intruders, 0 interference pairs (point-containment sampling)
- **0 non-manifold edges** across all STLs, both designs
- Printability: best-of-6 orientations, ≤2.9% unsupported per part —
  nothing needs real supports

## Design decisions since the frozen spec

1. **Graphite is 125 mm (−5…120), not 120** — 5 mm into the bellmouth
   closes the x=0 crevice ring. Buy 125×14 stock or trim.
2. **Wire channel:** 0.4 mm gap, graphite outer (21.5) → rail inner (21.9),
   full length, exits both ends. Route electrode leads here, pot with epoxy.
   NO holes drilled in the wetted hull.
3. **Slices overlap 0.4 mm** (bellmouth + fairing) — slicer union welds
   solid; butt joints were 20+ non-manifold artifacts before the fix.
4. **Hood clamps magnet stacks:** hood inner face at z=±18.5, exactly on
   stack tops. Epoxy tiles to trays anyway — hood closes the flux loop
   AND holds the pack down.

## Print (PLA, 0.2 mm)

| Part | Orientation | Unsupported |
|---|---|---|
| plates | +Y / −Y down (lip-end down) | 1.2% |
| rails | flat (14 mm face on bed) | 0% |
| bellmouth / fairing walls | +X down (lengthwise) | 0% |
| flange / rear_cap | flat | 1.8–2.9% (ear bridges) |
| bulkheads | flat | 0–1.2% |

## Simulation results (analytic, cross-checked vs spec)

- **Thrust law verified:** F = I·B·W = 3.06 × 0.483 × 0.040 = **59.1 mN —
  exact spec match** (seawater row: 1.90 A → 36.7 vs spec 36.8 ✓)
- **Operating point:** R_cell ≈ 1.8 Ω → 19 V wants 9+ A → brick limits at
  3.06 A. Thrust unchanged either way (I sets F), but input power is 19 W
  (CC brick) or 58 W (stiff 19 V) — **measure the brick V–I curve**; this
  resolves the spec's 58.1 W row.
- **Hydraulics:** ideal EM rise 106 Pa vs duct loss 0.003 Pa @ 5 ml/s —
  duct loss is irrelevant; a 1 mm reservoir offset (9.8 Pa) dwarfs it.
  Cébron's level-control warning is the binding constraint, confirmed.
- **Drag:** A bare box loses 52% of thrust to pod drag at 14 cm/s; B loses
  2%. Fairing = −96% pod drag (~free +49% thrust margin).

## Assembly order

1. Epoxy tiles to plate trays (compass-check every station — all six must
   drive the same way).
2. Slide rails in from rear; silicone-seal wetted joints.
3. Drop graphite plates in, leads into the rail channel, pot ends epoxy.
4. Bellmouth to plates: silicone. Flange on mouth, cap on rear.
5. Hood on top, end bars, cable-tie strap. Hood contacts magnet faces
   (flux path); insulation between hood and WIRES only.
6. Freshwater rinse after every run — nickel magnets + graphite + brine
   = galvanic cell, don't leave soaking.

## Safety (Cébron + spec §8)

- 3 A in brine makes Cl₂ (anode) and H₂ (cathode). OUTDOOR, ventilated,
  ≤2 min runs, anode submerged, teacher aware. Bubbles also steal thrust.
- Fuse the supply. N52 packs pinch.

## Open items (bench, not CAD)

1. Brick V–I curve (constant-current vs stiff) — Cébron's step 1 anyway.
2. Level control <1 mm + current-off control every session.
3. Timed collection for Q; dye front ≠ mean velocity.

## Improvement loop (converged)

Applied: fairing drag fix, fairing-slice overlap (0 artifacts), thrust-law
correction (now exact vs spec), wire-channel closure, per-part orientation
verifier. Rejected with reason: Le→160 (breaks frozen spec/budget),
w-flare bellmouth (contraction 1.5 adequate), extra magnets (spec frozen).
Remaining levers need bench data or spec sign-off → **no further gains
possible from CAD alone.**
