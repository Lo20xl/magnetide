# Magnetide v22 — Final Design Spec Sheet

Status: design frozen for build. All performance figures are MODELLED
predictions (analytic solver + iron-circuit field estimate), not measurements.
The solver is validated against one bench resistance value only (4.4 Ω measured
vs 4.93 Ω predicted). Treat every newton below as the number to beat on the
bench, not the number to print.

## 1. Geometry (mm)

| Quantity | Value |
|---|---|
| Channel height h (pole gap) | 44 |
| Channel width w (electrode gap) | 40 |
| Electrode length Le | 160 (8 pole stations × 20) |
| Drive length Ld | 160 (= Le, coverage 100%) |
| Wall thickness | 1.5 (printed) |
| Magnetic gap g = h + 2·wall | 47 |
| Hydraulic diameter Dh | 41.9 |
| End-effect ratio Le/Dh | 3.8 (gate: ≥ 3 ✓) |
| Tilability | w = 40 ✓ (multiple of 10), Le = 160 ✓ |
| Inlet | bellmouth flare in h, r ≥ 3 mm (target 5) |

## 2. Magnets

| Quantity | Value |
|---|---|
| Grade / size | N52, 20×10×5 tiles |
| Arrangement | 8 stations × 2 poles × 2 across × 2 deep |
| Block thickness lm | 10 mm (2 deep) |
| Total tiles | 128 |
| Cost @ Rp6,325/tile | Rp809,600 |
| Yoke | insulated soft-iron hood, top + bottom, closed loop |
| Field in gap (modelled) | 229 mT |

Per-station magnet mass is identical to v20 (4 tiles/pole/station). The extra
80 tiles are LENGTH (8 vs 6 stations), not thickness — length pays linearly,
thickness saturates. Verified in sweep: thickening 10→20→30 mm buys
+66%/+29%; lengthening 120→200 buys +67% for +67% tiles.

## 3. Electrodes & electrics

| Quantity | Value |
|---|---|
| Material | graphite plates, 2× 44×160 mm, side walls |
| Electrode area (total) | 14,080 mm² |
| Rail | 12 V, high-current supply with own fuse |
| Current (strong brine, modelled) | 9.64 A |
| Channel resistance at point | 0.979 Ω |
| Current density | 1.37 kA/m², θ = 0.56, σ_eff = 5.81 S/m |
| Sensing | Hall/10 A shunt module (INA219 3.2 A ceiling exceeded) |
| Wiring | single supply; all 8 stations same drive direction (verify!) |

## 4. Fluid

| Quantity | Value |
|---|---|
| Demo fluid | strong brine ~100 g/l, σ ≈ 13.2 S/m @ 25 °C (Quénot/Bešter-Rogač fit) |
| Free upgrade | run warm (~30 °C, +20% σ) |
| Boat-day fallback | seawater 5.45 S/m (same hardware, derated — see §5) |

## 5. Predicted performance (MODELLED)

| | Strong brine | Seawater |
|---|---|---|
| Thrust F | 88.2 mN | 51.4 mN |
| Power | 115.6 W | 67.3 W |
| Thrust per watt | 0.76 mN/W | 0.76 mN/W |
| Ideal pressure rise | 50.1 Pa (5.1 mm H₂O) | 29.2 Pa (3.0 mm H₂O) |
| vs v20 as-built (29 mN) | 3.0× | 1.8× |

## 6. BOM (Rp, marketplace floor)

| Item | Rp |
|---|---|
| 128× N52 20×10×5 | 809,600 |
| Graphite plates, iron sheet, 10 A shunt, terminals (est.) | ~150,000 |
| TOTAL | ~959,600 (margin Rp40,400) |

Price graphite FIRST — it is the uncertain line. Fallback if dear: single-deep
block (lm 5, 64 tiles): 48.4 mN at Rp554,800 total.

## 7. Build notes

1. Polarity: all 8 stations must drive the SAME direction. Check with a
   compass before wiring; one flipped station subtracts instead of adding.
2. Insulate the iron hood from the water everywhere. A hood short is a pump
   bypass And a corrosion cell.
3. Bellmouth the inlet (r ≥ 5 mm target). No superglue on wetted joints —
   it hydrolyses; mechanical fasteners.
4. Sort tiles by measured strength; put matched pairs opposite each other.
   Uniformity raises average B, which is all the force sees.

## 8. Measurement (per Cébron)

1. V–I curve of YOUR graphite/brine/spacing first — gives E_chem and R,
   collapses half the uncertainty before the pump exists.
2. Timed volumetric collection = primary Q. Dye video is cross-check only
   (leading edge ≠ mean velocity).
3. Reservoir levels equal to < 1 mm; current-off control run every session
   (1 mm offset = 9.8 Pa ≈ 20% of the 50 Pa budget).
4. Thrust on kitchen-scale reaction rig. Three replicates, mean ± SD.

## 9. Hazards

- Chlorine: ~3.5 mg/s upper bound at 9.6 A (real lower; most → hypochlorite).
  Anode submerged, ventilated, outdoor, ≤ 2 min runs.
- 10 A electrics: fused supply, wire gauge to suit, no thin jumpers.
- N52 assembly at this count pinches hard; chips corrode in brine.
- Graphite anodes erode — carry spares.
