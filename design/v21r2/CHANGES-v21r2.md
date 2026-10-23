# Magnetide v21-r2 — what changed and why

Revision of v21-final after the build review. Shape is unchanged: 40 × 14 × 120 mm bore,
150 mm long, 96 × N52 tiles, same field. Everything here is about how the parts locate,
seal and hold together.

## 1. One part per tray (was: plate + separate walls)

The old tray was a plate with walls sitting on it as separate solids. Now the floor, both
side rails and both end walls are a **single printed solid**, so there is no joint for water
to creep through under the magnet pocket.

Wall tops sit at **z = 17 mm** from the bore centreline; the floor is 1.5 mm thick at z = 7 mm.
The electrode slot is cut into that floor (see §3).

## 2. Cap plate over the magnets (new part, pegged)

A **1.5 mm cap plate** closes the magnet pocket from above, with a rim that lands on the wall
tops and **6 pegs** into the rails (3 per side, at x = 30 / 80 / 130).

| Feature | Value |
|---|---|
| Peg | Ø3.0 × 5 mm long, run into the wall |
| Hole | Ø3.3, 5 deep (0.15 mm clearance per side) |
| Cap plate | 124 × 52 × 1.5, sits over the magnets |
| Rim | 1.5 mm, from wall top 17 to magnet top 18.5 |

The cap is **not** glued: lift it, swap a tile, put it back. The magnets are potted to the
tray floor, not to the cap, so the cap never carries a magnet load.

Bottom half is the exact mirror of the top half (same STL, printed twice).

## 3. Electrode slot — the electrodes cannot fall out or slide

Three features, all on the tray and the rear block:

- **Dado** in the tray floor, 0.6 mm deep, cut 2 mm oversized in Y on each side
  (0.2 mm clearance per side). Runs x = 19…140, so it is **open at the inlet** — you slide
  the electrode in from the front — and **blind 2 mm before the outlet** end wall.
- **Keeper rib** hanging under the floor beside the electrode (y = 22…24, full 120 mm drive
  length, z = 0…8.5). The electrode cannot tip out sideways.
- **Rear ear** on the outlet block, over the electrode end.

Result: the electrode is captive at the outlet end, guided for its whole length, and can only
be withdrawn forward — which is exactly what you want when you replace an eroded anode.

Verified in the model: electrode ∩ tray = **0.000 mm³** (clearances hold), bore clear.

## 4. Rear support — your option, chosen

The electrodes **are** the rear support. Two 120 × 14 × 2 mm graphite plates 40 mm apart,
clamped top and bottom by the keepers, and capped at the outlet end by ears on the rear
block. That is a stiffer pair than any printed rib would be, and it costs nothing.

Optional: delete `Rear_Block` and let the steel end wall own the outlet. You then lose the
ears, so add two printed tabs instead — more parts, no benefit. Recommendation: keep the block.

## 5. Pegs everywhere

| Joint | Pegs | Holes |
|---|---|---|
| Cap → tray (each half) | 6 × Ø3 × 5 | 6 × Ø3.3, in the wall tops |
| Bellmouth → tray inlet face | 6 × Ø3 × 2 | 6 × Ø3.3 blind, at z ±12.75 |
| Rear block → tray outlet face | 6 × Ø3 × 2 | same pattern, same face |

One hole pattern for both ends: the bellmouth and the rear block are interchangeable in
position, which is also a print-fixture convenience — the same jig locates both.

Print note: model the cap pegs **standing up** (cap plate on the bed, pegs vertical) so they
need no supports. Same for the 2 mm end pegs: print the bellmouth and rear block on the face
opposite the pegs.

## 6. The one dimension that had to move

The cap needs 1.5 mm above the magnets. v21 already stacked exactly to 41 mm with no
clearance, so the shell grows to **H = 44 mm**:

```
bore 14 + 2 × (floor 1.5 + magnet 10 + cap 1.5) + 2 × steel 2.0 = 44.0 mm
```

Nothing else changes: bore, length, width, lugs, bolt pattern, field, budget.

## 7. Part list

Printed (PETG or PLA, 0.4 nozzle):

| File | Qty | Note |
|---|---|---|
| `tray.stl` | 2 | one per half; mirror the second |
| `cap.stl` | 2 | pegs up, no supports |
| `bellmouth.stl` | 1 | pegs on the outlet face |
| `rear_block.stl` | 1 | pegs on the inlet face |

Everything else: 2 steel clamshell halves (laser DXF unchanged except height), 2 graphite
electrodes 2 × 14 × 120, 96 N52 tiles, 8 × M3.

## 8. Open items

- The keeper rib occupies y = 22…24 mm inside the 26 mm cavity. It clears the steel by 2 mm —
  fine for 2 mm sheet, but check the folded corner radius on the real part.
- 3 mm pegs in 1.5 mm plate rims are the weak point of the cap. If a peg snaps, the cap still
  sits; consider Ø3.5 on the two centre pegs if you reprint.
- Electrode dado depth 0.6 mm leaves 0.9 mm of floor under the electrode. Do not deepen it.
