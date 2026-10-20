# Magnetide — Final Design & Optimisation
**Benchtop MHD conduction drive unit** · one core, swappable housings (pump / thruster)
Prepared for the school report · 19 Oct 2026

---

## 0. What this document decides

| Question | Answer |
|---|---|
| Is the current v19 build a pump or a boat motor? | One **permanent-magnet conduction core** in a printed housing; the nozzle plate and the open outlet are the two modes. Same core, two housings. |
| What are we optimising? | **Flow rate** and **flow per watt**. Efficiency (η_em) is not claimable at this scale and is explicitly excluded. |
| What is the single biggest design error found? | The electrode is **120 mm long** but the magnets cover only **40 mm**. Two-thirds of the electrical loss produces no thrust. |
| What does the fix cost? | **Rp151,800 → Rp303,600** in magnets depending on lane (see §6). No new housings, no new channel. |
| What should we expect to measure? | **35–40 ml/s at 1.15 A (7.7 W)**; **~47–52 ml/s at the 12 V rail (1.9 A, 23 W)**. The original target was 5 ml/s. |

---

## 1. Corrections to earlier drafts

Two errors in the previous design notes are corrected here, because both changed the conclusion:

1. **The magnet format is 20×10×5 mm blocks, not Ø20×5 mm discs.** `PRINT_v19.md` specifies the tray cavity as a 20×10×5 tile ("check cavity with one real tile"). The block is the right part and costs **Rp6,325** (Tokopedia, My Aladin, 10k+ sold, Oct 2026) versus Rp11,500–13,225 for a disc of similar volume. All cost figures below use the block.

2. **"Field > 1 T" was never supported by the model.** With a 20 mm gap and a 5 mm magnet stack, the yoke-assisted pair gives **0.42 T**, not >1 T. Reaching 1 T needs ~20 mm of magnet per side, which is 4× the magnet volume in the same footprint. The honest target band is **0.4–0.75 T**, and the design below reaches the top of it.

A third, conceptual error is the subject of §3 and is the substance of this optimisation.

---

## 2. Operating principle

Salt water in a rectangular channel. A DC current density **J** is driven across the channel by graphite plate electrodes; a permanent-magnet pair pushes **B** across the same gap, perpendicular to J. The Lorentz force **J×B** acts along the channel.

For a channel of height *h* (pole gap), width *w* (electrode gap), electrode length *L_el*, electrode current *I* and field *B*:

$$F = I\,w\,B \qquad \Delta P = \frac{I B}{h} \qquad v = \sqrt{\frac{I\,B}{\rho\, h}}\cdot\kappa_{v}$$

The velocity expression is the momentum balance for a duct discharging freely — the head must pay for both entrance loss and exit kinetic energy, which is why the energy form overpredicts by √2.

**The key structural fact.** *F* does not contain the electrode length. Making the electrode longer does **not** increase thrust at fixed current; it increases the voltage you must supply. Length matters only through **how much of it the field covers** — the fraction $\kappa = L_{drive}/L_{el}$.

---

## 3. The optimisation insight (and what the MDPI paper contributes)

> Cao, Cheng, Wang, Zhou & Zhang, *Study of Helix Angle Parameters of Helical-Channel MHD Thrusters*, **Magnetochemistry 12 (2026) 89**, doi:10.3390/magnetochemistry12080089

### 3.1 What the paper shows

A 10 T superconducting helical thruster — 600 mm long, 150 mm outer electrode, 15.5 kg/s — was simulated with three helix pitches:

| Helix angle | Thrust | η_em |
|---|---|---|
| 23.00° | 204.8 N | 4.72 % |
| 17.66° | 241.8 N | 5.01 % |
| **14.29°** | **262.6 N** | **7.23 %** |

Shorter pitch = longer effective coupling path between fluid and field → more uniform radial current, fewer eddy-current and Joule losses, more electromagnetic energy converted to pressure. **+28 % thrust, +53 % efficiency from geometry alone, at identical field and voltage.**

### 3.2 Why it matters here

The paper's mechanism is *coupling length*, not helicity. A helical channel buys coupling length inside a compact envelope; we can buy the same thing — far more cheaply — by **filling the straight channel with pole stations until the field covers the whole electrode**. Same principle, buildable on a Creality Hi.

It also sets the honesty bar: **at 10 T with a helical channel, 7.23 % is the best efficiency in this literature.** At 0.7 T and 0.2 m/s we cannot claim efficiency at all. We claim flow rate and flow per watt, both measurable with a beaker, a stopwatch and a multimeter.

### 3.3 What we do not take from it

The helical electrode/insulator stack needs a machined axisymmetric ceramic former. That option was already withdrawn on buildability. The straight channel stands; only the *sizing rule* is imported.

---

## 4. The model

Three coupled relations, all SI, implemented in `magnetide_predict.py`:

**Field** — yoke-assisted magnet pair, closed form, with a 0.90 derate for real mild-steel leakage:
$$B(g) = 0.90\cdot\frac{2 B_r l_m}{2 l_m + 1.05\,g}\,,\qquad B_r = 1.45\ \mathrm{T}\ (\mathrm{N52})$$
where *g* = channel height + 2 × wall thickness.

**Fluid** — momentum form, with friction, end losses and field non-uniformity folded into κ_v = 0.80:
$$v = 0.80\sqrt{\frac{J\,B\,L_{drive}}{\rho}}\,,\qquad Q = v\,w\,h$$

**Electrical** — Delannoy's fit, applied *inside* the model so the bubble law can act on conductivity:
$$V_{el} = E_{chem} + I R_{ch},\quad R_{ch} = \frac{w}{\sigma_{eff}\,h\,L_{el}},\quad \sigma_{eff} = \sigma_0(1-\theta),\quad \theta = 1 - e^{-0.006 j_d}$$
with *j_d* in mA/cm².

The bubble law matters because at fixed current the Lorentz force is **independent of σ** — bubbles do not reduce thrust, they reduce conductivity and therefore **raise the voltage needed to push that current**. Bubbles hit power, which is exactly what flow-per-watt measures.

### 4.1 Design gates (applied before anything is ranked)

| Gate | Rule | Why |
|---|---|---|
| **Supply rail** | V_el ≤ 12 V | A 12 V brick cannot invent voltage. Several otherwise-attractive designs need 25–75 V and are not buildable. |
| **Fuse** | I ≤ 3.2 A | INA219 measurement ceiling. |
| **Tilability** | channel dimensions are multiples of the tile's 10 mm edge | otherwise every tile needs cutting |
| **End-effect law** | L/D_h ≥ 3, D_h = 13.7 mm | below this the entrance/exit momentum terms rival the thrust |
| **Budget** | magnets ≤ Rp350k inside the ~Rp700k project envelope | the earlier design spent the whole budget on magnets, leaving nothing for the PSU |

### 4.2 The two lengths

The single most important modelling correction:

| Symbol | Value | Set by |
|---|---|---|
| **L_el** — electrode length | **120 mm** | the printed channel (v19) |
| **L_drive** — axial extent of the field | **20 mm × number of pole stations** | how many magnets you buy |

Everything resistive scales with **L_el**; everything magnetic scales with **L_drive**. Rating a channel on L_el alone is what produced the ">1 T / 0.2 m/s" mismatch in the earlier notes.

---

## 5. Results

### 5.1 As-built vs drop-in fixes (all at the 12 V rail)

| Configuration | Tiles | B | Coverage | I | P | v | Q | Q/W |
|---|---|---|---|---|---|---|---|---|
| **v19 as built** (wall 4, 2 stations, 1 tile/side) | 8 | 421 mT | 33 % | 1.91 A | 23.0 W | 11.8 cm/s | **22.7 ml/s** | 0.99 |
| Fill the tray (6 stations, wall 4) | 24 | 421 mT | 100 % | 1.91 A | 23.0 W | 20.5 cm/s | **39.3 ml/s** | 1.71 |
| + thin wall to 1.5 mm | 24 | 507 mT | 100 % | 1.91 A | 23.0 W | 22.5 cm/s | **43.1 ml/s** | 1.88 |
| + 2 tiles/side (wall 2.5) | 48 | 690 mT | 100 % | 1.91 A | 23.0 W | 26.2 cm/s | **50.3 ml/s** | 2.19 |
| **+ 2 tiles/side (wall 1.5)** | **48** | **730 mT** | **100 %** | **1.91 A** | **23.0 W** | **27.0 cm/s** | **51.8 ml/s** | **2.25** |

**Filling the tray is worth +73 % flow for zero extra power** — same supply, same current, same channel. Thinning the wall adds ~+10 %. The last two rows buy a further +20 % for double the magnet cost.

### 5.2 Current sweep at the recommended build (wall 1.5, 6 stations, 2 tiles)

| I | V_el | P | v | Q | Q/W |
|---|---|---|---|---|---|
| 0.50 A | 3.94 V | 1.97 W | 13.8 cm/s | 26.5 ml/s | 13.4 |
| 1.00 A | 5.94 V | 5.94 W | 19.5 cm/s | 37.4 ml/s | 6.30 |
| **1.15 A** | **6.70 V** | **7.70 W** | **20.9 cm/s** | **40.1 ml/s** | **5.21** |
| 1.50 A | 8.80 V | 13.2 W | 23.9 cm/s | 45.8 ml/s | 3.47 |
| 1.91 A (rail) | 12.0 V | 23.0 W | 27.0 cm/s | 51.8 ml/s | 2.25 |
| 2.50 A | 18.3 V | — | — | — | *exceeds rail* |
| 3.00 A | 25.8 V | — | — | — | *exceeds rail* |

**There is no interior optimum in current** — Q rises monotonically, Q/W falls monotonically. The choice is a statement of intent, not a discovery: run at 1.15 A for the efficiency claim, at the rail for the maximum-flow demo.

### 5.3 Bubble-law sensitivity at the rail point

| Bubble law | σ_eff | Current reached at 12 V | Q | Q/W |
|---|---|---|---|---|
| Linear σ₀(1−θ) — optimistic | 2.25 S/m | 1.91 A | 51.8 ml/s | 2.25 |
| Bruggeman σ₀(1−θ)^1.5 — lower bound | 1.86 S/m | 1.58 A | **47.0 ml/s** | 3.18 |

Quote the rail flow as **47–52 ml/s** and the efficiency number as a band. The θ coefficient is unvalidated; this is the largest single uncertainty in the model, ahead of the field.

### 5.4 Field uncertainty

The 0.90 yoke derate assumes µ_r ≈ 2000. At 0.7 T mild steel is typically 500–800, so **expect 550–650 mT measured, not 730**. Since $v \propto \sqrt{B}$:

| Assumed B | Q at 1.15 A |
|---|---|
| 730 mT (model) | 40.1 ml/s |
| 650 mT | 37.9 ml/s |
| 550 mT | 34.8 ml/s |

**Design claim: 35–40 ml/s at 1.15 A, 7.7 W** — 7–8× the original 5 ml/s target.

---

## 6. Recommended build

### Lane A — the build to make

| Parameter | Value |
|---|---|
| Channel | 16 mm wide × 12 mm high × 120 mm electrode |
| Pole stations | **6** at 20 mm pitch over the 120 mm electrode (tray is a blank plate — magnets are potted where you place them) |
| Magnets | **48 × 20×10×5 mm N52** blocks, 2 per side per station |
| Wall thickness | **1.5 mm** printed (gap g = 15 mm); fall back to 2.5 mm if the tray weeps |
| Yoke | mild-steel pole shoes + return, 20 mm gap |
| Supply | 12 V, ≥ 3 A, single rail |
| Operating point | **1.15 A, 6.7 V, 7.7 W** |
| Predicted | B 730 mT (550–650 measured) · v 21 cm/s · **Q 40 ml/s** · Q/W 5.2 |
| Magnet cost | **Rp303,600** at Rp6,325/tile |

**Changes from v19 (verified against the v19 STLs):**

- `magnet_tray_*_floor.stl` is a **blank 225.2 × 84.0 × 1.2 mm plate** and `magnet_tray_*_rim.stl` a **225.2 × 84.0 × 5.0 mm rim** — so there are no fixed "stations", the magnets are potted wherever you place them, and **the rim is exactly one tile high**. A 2-tile stack (10 mm) needs the rim reprinted to **10 mm**, not 5.
- Layout: lay the tiles as a **continuous row** along the 120 mm electrode at 20 mm pitch, same pole face to the gap, steel return behind — that is what gives 100 % coverage. Six positions × 2 sides × 2 tiles = 48.
- Reprint the tray floor with **1.5 mm walls** (keep the floor ≥ 1.2 mm and check it holds ~50 kPa head); fall back to 2.5 mm if it weeps.
- The nozzle plate and all shell parts are unchanged. Nothing about the housing, electrodes or flanges moves.

### Lane B — budget lane (Rp151,800)

24 tiles, 6 stations, 1 tile/side, wall 4 mm. **Q = 39.3 ml/s at the rail; 43.1 ml/s if the wall goes to 1.5 mm.** Half the magnet spend, ~76 % of the flow. Take this lane if the PSU and yoke also come out of the same Rp700k.

### Lane A′ — max flow (Rp303,600)

Identical hardware to Lane A, run at the 12 V rail (1.91 A, 23 W): **Q ≈ 52 ml/s**. Use for the boat-mode demo; quote Lane A's figures for the efficiency comparison.

---

## 7. What this design does not claim

- **Efficiency.** η_em at 0.7 T sits far below the 7.23 % the 10 T helical thruster achieves. Do not quote an efficiency figure; quote Q and Q/W.
- **Field above 730 mT**, and treat even that as unverified until a Hall probe has been in the gap.
- **Bollard thrust** without a load cell or a lever on a 0.01 g scale. The force model gives 9–22 mN — real, but not visible on a kitchen scale.
- **Nozzle gains.** The CFD's 1.33 m/s jet figure assumes a 1.8:1 contraction and an imposed inlet; cite `CFD_REPORT.md` caveat 3 beside it. A convergent exit *lowers* bollard thrust.
- **Helical geometry.** Cited as principle, not adopted as hardware.

---

## 8. Measurement plan — in this order

1. **B(x) map.** Hall probe along the axis at operating current. Replace the 0.90 constant with the measured profile. This moves Q by ±15 %.
2. **V–I curve.** Sweep 0 → 3 A, record V_el. Extract E_chem and R_ch. Validates or kills the Delannoy fit at our geometry, and is the best available evidence on bubble behaviour.
3. **Flow rate.** Timed collection into a measuring cylinder, 3 repeats at 1.15 A and at the rail. Cross-check with dye video at 120 fps.
4. **Conductivity.** Measure σ of the 5 % brine at operating temperature. Q ∝ σ^0.5, so a 20 % error in σ is a 10 % error in Q.
5. **Electrode condition.** Photograph the graphite plates before/after 30 min at the rail; film growth or pitting invalidates R_ch over long runs.

---

## 9. One-table summary

| | Lane A | Lane A′ | Lane B |
|---|---|---|---|
| Tiles | 48 | 48 | 24 |
| Magnet cost | Rp303,600 | Rp303,600 | Rp151,800 |
| B (model / expected) | 730 / 550–650 mT | same | 507 / 400–460 mT |
| Operating point | 1.15 A, 6.7 V, 7.7 W | 1.91 A, 12 V, 23 W | 1.91 A, 12 V, 23 W |
| v | 21 cm/s | 27 cm/s | 22 cm/s |
| Q | **40 ml/s** | **52 ml/s** | **43 ml/s** |
| Q/W | **5.2** | 2.3 | 1.9 |
| Use | efficiency claim | boat demo | budget fallback |

---

## 10. Sources

1. **Y. Delannoy et al.**, "MHD conduction pump: experimental study and corrosion mitigation", *Magnetohydrodynamics* **61** (2025) 55–66, hal-05279338 — electrochemical overpotential E_chem = 2.57 V and R_ch = 0.0407 Ω, fit valid to j ≤ 1 kA/m²; used at our 0.8 kA/m².
2. **T. Cao, Y. Cheng, Z. Wang, C. Zhou, C. Zhang**, "Study of Helix Angle Parameters of Helical-Channel Magnetohydrodynamic Thrusters", *Magnetochemistry* **12** (2026) 89, doi:10.3390/magnetochemistry12080089 — coupling-length principle; the 4.72 → 7.23 % efficiency range that bounds what is claimable.
3. **Bubble conductivity**: Bruggeman and Maxwell effective-medium relations for a gas dispersion; electrolysis gases reduce effective conductivity with gas fraction (DTIC ADA260645; OSTI 6300896).
4. **Internal**: `magnetide_predict.py` (this document's model), `magnetide_optimize4.py` (sweep), `MHD-spec-and-C1.md`, `CFD_REPORT.md`, `PRINT_v19.md`, `Magnetide_Claims_Inventory.md`.
5. **Pricing**: Tokopedia N52 20×10×5 block — Rp6,325 floor (My Aladin, 10k+ sold) vs Rp10,000–35,000 cluster, checked 19 Oct 2026.

---

### Reproduce every number in this document

```bash
cd ~/Desktop/steam-awg
python magnetide_predict.py                    # as-built vs fixes, sweep, bubble band
python magnetide_optimize4.py 6325 350000 12   # full sweep: price, budget, rail
```
