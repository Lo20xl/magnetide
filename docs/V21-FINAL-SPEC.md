# Magnetide v21-final — Frozen Build Spec

Status: FROZEN. Budget: under Rp1,000,000. All performance figures MODELLED
(analytic solver + iron-circuit field estimate), not measured. Numbers to beat
on the bench, not numbers to print.

Supersedes v22 (128 tiles, 88 mN, Rp960k, 10 A): v22 stays valid as the
max-thrust fallback, but v21-final wins on budget margin, efficiency, and
runs on existing gear + a scavenged supply.

## 1. Geometry (mm)

| Quantity | Value |
|---|---|
| Channel height h (pole gap) | 14 |
| Channel width w (electrode gap) | 40 |
| Electrode / drive length Le = Ld | 120 (6 stations × 20) |
| Coverage Ld/Le | 100% ✓ |
| Wall | 1.5 printed |
| Magnetic gap g | 17 |
| Dh | 20.7 → Le/Dh = 5.8 (gate ≥ 3 ✓) |
| Tilability | w = 40 ✓, Le = 120 ✓ |
| Inlet | printed bellmouth front part, flare r ≥ 3 mm (target 5), bolted to steel tube |

## 2. Magnets & yoke

| Quantity | Value |
|---|---|
| Tiles | 96× N52 20×10×5 (6 st × 2 poles × 2 across × 2 deep) |
| Block lm | 10 mm |
| Cost @ Rp6,325 | Rp607,200 |
| Yoke + structure | 2 mm low-carbon steel clamshell (AISI 1010/1018 or SPCC): fold-split horizontally at the channel mid-plane, M3-bolted flanges with BARE mating faces — both flux return AND structure (as Chan et al.); printed liner is the water barrier, steel stays dry behind it |
| Magnet potting | tiles potted in place in printed trays with hot glue (removable) or two-part epoxy (permanent), set before closing; NO spray coatings on nickel plating |
| Gap field (modelled) | 483 mT |

Why thin: thickening 10→20 mm buys field sublinearly and costs 96 more
tiles (Rp607k, over budget). Length pays linearly; thickness saturates.
(Sim note: your Halbach trials losing is consistent with g/tile ≈ 0.85 —
enhancement decays as exp(−2πg/λ) and the ripple wastes power. Parallel
poles, uniform gap, matched tile pairs.)

## 3. Electrodes & supply

| Quantity | Value |
|---|---|
| Graphite plates | 2× 14×120 mm, side walls |
| Supply | scavenged 19 V laptop brick (free) or 24 V-capable bench |
| Peak draw | 3.06 A — inside INA219 3.2 A, NO shunt upgrade |
| Wiring | single supply, all 6 stations same direction (compass-check!) |

## 4. Fluid

Strong brine ~100 g/l (σ ≈ 13.2 @ 25 °C, Quénot/Bešter-Rogač fit); warm if
possible (+20% σ @ 30 °C). Seawater rows below for boat day.

## 5. Predicted performance (MODELLED)

| Condition | I | F | P | F/P |
|---|---|---|---|---|
| Brine, 12 V (existing gear) | 2.30 A | 44.5 mN | 27.6 W | 1.61 |
| Brine, 19 V (laptop brick) | 3.06 A | 59.1 mN | 58.1 W | 1.02 |
| Brine, 20.6 V (shunt ceiling) | 3.19 A | 61.8 mN | 65.8 W | 0.94 |
| Seawater, 19 V (boat day) | 1.90 A | 36.8 mN | 36.2 W | 1.02 |

Ideal rise at 59 mN: ~21 Pa ≈ 2.1 mm H₂O. Level control < 1 mm + current-off
control every session (1 mm = 9.8 Pa).

## 6. BOM (Rp, marketplace floor)

| Item | Rp |
|---|---|
| 96× N52 | 607,200 |
| Graphite 2× 14×120, iron sheet, wires/terminals (est.) | ~120,000 |
| 19 V brick | scavenged (0) |
| TOTAL | ~727,000 (margin ~273,000) |

Price graphite FIRST (uncertain line). Margin covers a 24 V bench supply if
no brick is available.

## 7. Build order

1. V–I curve of YOUR graphite/brine/spacing (Cébron's request). Gives E_chem
   + R; collapses half the uncertainty; also locates the bubble choke.
2. Steel clamshell + magnet pack: pot tiles into printed trays with jig
   (hot glue/epoxy, set before closing); compass-check every station's direction;
   bolt flanges bare-face — no coating between halves.
3. Electrodes, insulated hood, bellmouth, fasteners (no superglue wetted).
4. Timed collection (primary) + kitchen-scale thrust rig + dye cross-check.
   Three replicates, mean ± SD, current-off controls.

## 8. Hazards

3.2 A in brine: ~1 mg/s Cl₂ upper bound — anode submerged, ventilated,
outdoor, ≤ 2 min runs. N52 pack pinches; chips corrode. Fuse the supply.
Graphite anodes erode — spares.
