# Magnetide — Project Context for the Report Rewrite (v20)

**Audience:** agent rewriting the Google Doc `Magnetide — Kelas 10.8 Kelompok 1`
**Doc ID:** `1GB8_LY5ctq8b0HIp9QwlAwimCqW2Gkm5S5XdZq8LAvo` (school Google account)
**Date:** 20 Oct 2026
**Status of build:** nothing has been printed yet. Every number below is **modelled**, not measured.

---

## 0. The single most important constraint on this rewrite

**A modelled flow rate is not an achieved flow rate.** The solver that produces
these numbers is analytic; it has never been validated against a built channel.
The report must label every Q, v and P figure as a *prediction* until the team
has measured it by timed collection with a Hall probe on the pole gap.

The doc currently carries a pass mark of 5 ml/s and an aspiration of 15 ml/s.
The model now predicts 117–183 ml/s. Writing a modelled number against a 5 ml/s
pass line is precisely the overclaim the team's own claims inventory exists to
catch. Do not do it. Either raise the targets to match the intended design, or
keep the targets as targets and report the model separately as a prediction.

---

## 1. Project identity

- **Title:** Magnetide — Penggerak Magnetik Adaptif untuk Laut Tanpa Baling-baling
- **Class:** 10.8, Pahoa School. Project advisers: Dhanang Laoshi, Selvya Laoshi.
- **Team:** a six-student group. Names withheld from this document; see the
  project report for the full roster.
- **What it is:** a benchtop MHD conduction drive. One permanent-magnet core with
  swappable housings, so the same core runs as a ducted pump or as an open boat
  thruster. No propeller, no shaft, no seal, no bearings.
- **Declared objectives:** maximise **flow rate Q** and **flow per watt Q/W**.
  Efficiency η_em is explicitly NOT claimed at this scale and should stay excluded.
- **Budget:** ~Rp700,000 total. Magnet budget inside that: ≤ Rp350,000.
- **Printer:** Creality Hi (260×260×300), PLA only.

---

## 2. Design history — what each version was

This is real iteration history and should be *preserved*, not overwritten. A
STEAM report is graded partly on evidence of iteration.

| Ver | What it was | Fate |
|---|---|---|
| v17 | home-wound electromagnets, acrylic channel | superseded |
| v18 | moved to permanent magnets; bare thrust 100.7 mN (+93%); light-plate claim retracted (×0.89); bellmouth area-matched; skid removed | superseded |
| v19 | **the printable one** — 24 STL files on Desktop `mhd_v19_stl\`. Electrodes 120×20×5 mm. Wall 4 mm, **2** pole stations, 1 tile/side. Rp614,000. Measured single-channel saline resistance **4.4 Ω** | **obsolete geometry, but the source of the one real measurement** |
| Lane A (19 Oct) | filled the tray to **6 stations**, thinned wall 4→1.5 mm, 2 tiles/side = 48 blocks. Rp303,600 | superseded by v20 |
| **v20 (20 Oct)** | **the recommended build** — see §3 | current |

### Why Lane A lost
Lane A used a **16 mm** electrode gap. The 20×10×5 magnet tile has a 10 mm edge,
so 16 % 10 = 6: **the tile never divides the channel width and every magnet has to
be cut.** That was a hidden, unbudgeted cost. Also, 16 mm at the 12 V rail gives
j = 133 mA/cm², which drives bubble coverage to θ = 0.55 — over half the
conductivity is eaten by electrolysis bubbles.

---

## 3. v20 — the recommended build

**Geometry:** channel **20 mm (h, pole gap) × 40 mm (w, electrode gap) × 120 mm (L_el)**
**Magnets:** 48 blocks, 20×10×5 mm N52, as **6 pole stations**, **1 tile deep** per side.
  Station pitch 20 mm. Soft-iron return yoke. Pole gap 15 mm, wall 1.5 mm.
**Cost:** 48 × Rp6,325 = **Rp303,600** (Tokopedia floor price, Oct 2026).
**Supply:** benchtop 30 V / 10 A in CV-CC mode, **12 V rail** for the boat.
**Fuse/measurement ceiling:** 3.2 A (INA219 shunt). All points below are under it.
**Electrodes:** graphite plates, 120 mm long, on the side walls.
**Inlet:** bellmouth, lip radius **≥ 5 mm** (= 0.25·D_h; ≥ 3 mm is the minimum
  that pays). This is free — it is just a fillet in the slicer.

### Predicted performance (all at the 12 V rail)

| Case | σ (S/m) | salinity | I | B | j | θ | v | **Q** | Q/W | P | Cl₂ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A. seawater | 5.0 | 3.5% | 1.80 A | 382 mT | 75 mA/cm² | 0.36 | 14.7 cm/s | **117 ml/s** | 5.42 | 21.6 W | 0.66 mg/s |
| B. brine (demo) | 7.0 | 5% | 2.25 A | 382 mT | 94 mA/cm² | 0.43 | 16.4 cm/s | **131 ml/s** | 4.85 | 27.1 W | 0.83 mg/s |
| C. strong brine | 10 | 7% | 2.81 A | 382 mT | 117 mA/cm² | 0.50 | 18.3 cm/s | **146 ml/s** | 4.35 | 33.7 W | 1.03 mg/s |

**With the bellmouth** (velocity derate κ_v 0.80 → 1.00):

| Case | v | **Q** | Q/W |
|---|---|---|---|
| A'. seawater | 18.3 cm/s | **147 ml/s** | 6.78 |
| B'. brine | 20.5 cm/s | **164 ml/s** | 6.06 |
| C'. strong brine | 22.9 cm/s | **183 ml/s** | 5.43 |

### For comparison (σ = 5.0, no bellmouth)

| Design | B | I | Q | Q/W | cost |
|---|---|---|---|---|---|
| v19 as-built (h12/w16/k1, wall 4, 2 st) | 421 mT | 1.91 A | 39.3 ml/s | 1.71 | Rp151,800 |
| Lane A (h12/w16/k2) | 730 mT | 1.91 A | 51.8 ml/s | 2.25 | Rp303,600 |
| Lane A alt (h20/w20/k2) | 591 mT | 2.81 A | 91.0 ml/s | 2.70 | Rp303,600 |
| **v20 (h20/w40/k1)** | **382 mT** | **1.80 A** | **117.3 ml/s** | **5.42** | **Rp303,600** |

Same magnet cost as Lane A, **2.3× the flow**, and it drops to 1.80 A — well under
the fuse — whereas Lane A's brine variants blew past it.

---

## 4. Why v20 wins — the two coupled levers

**At a fixed rail voltage, current density depends on the electrode gap `w` alone.**
Height never enters the electrical side; it enters only through the magnet gap
`g = h + 2·wall`. So the two axes are cleanly separable:

- **`w` is the bubble lever.** Widening the channel from 16 → 40 mm drops j from
  133 → 75 mA/cm², which drops bubble coverage θ from 0.55 → 0.36. That is what
  makes brine usable: you can raise conductivity without the current exploding.
- **`h` is the field lever.** `B = 2·k_yoke·Br·l_m / (2·l_m + 1.05·g)`, so `g = h + 2·wall`
  means larger `h` costs field. But Q ∝ √(B/h), and the extra area outweighs the
  field loss up to about h = 20 mm.

v20 sits at the sweet spot of both: h = 20 for area, w = 40 to keep j low, and
only 1 tile deep (k = 1) because at this gap the field is 382 mT and more depth
buys little per rupiah.

---

## 5. Salinity — declare it as brine

**Delannoy's own pump ran at 200 g/l specifically to raise conductivity.** So a
brine demo is precedent in the literature, not a dodge. But it must be declared,
because flow and thrust at σ = 7–10 are not comparable to a seawater device.

Unit note: the doc currently says "5%, di dalam rentang kerja standar 3,5%–5%".
The model's σ₀ = 5.0 S/m corresponds to **3.5%**, not 5%. 5% is closer to σ ≈ 7.
This is a units inconsistency in the doc and should be corrected.

Salinity is a genuinely large lever — the marginal return falls from 4.5 to
0.9 ml/s per S/m as σ goes 5 → 35, because θ rises from 0.36 to 0.82. So:
**moderate brine (σ ≈ 7) is the sweet spot. Piling on salt past σ ≈ 10 buys little
and costs current and chlorine.**

---

## 6. Safety — chlorine

Faraday's law gives Cl₂ evolution of 0.66–1.03 mg/s at these currents, against an
odour threshold of ~0.3 ppm in air. In a small unventilated room that is reachable
within minutes if the anode sits at the surface.

Required mitigations, and they should appear in the report:
1. **Anode submerged below the free surface.**
2. **Ventilate.**
3. **Cap runs at ~2 minutes.**
4. Treat the graphite anode as **sacrificial** — accept that it erodes.
5. Most Cl₂ disproportionates to hypochlorite in solution rather than off-gassing,
   so the inhalation risk is lower than the Faraday number implies — but it is not
   zero at high j. State this honestly rather than omitting it.

---

## 7. Model validation — the one real measurement

The team measured single-channel saline resistance at **4.4 Ω**, derived from their
own 4-parallel data (12 V, 10.8 A unballasted; 3.9 Ω ballast per channel, 5.75 A).

| Design | Model R_ch at σ = 5.0 | vs measurement |
|---|---|---|
| v19 as-built | **4.93 Ω** | +12% |
| v20 | **5.23 Ω** | +19% |

The model runs **conservative** — it predicts a higher resistance than reality, so
it understates flow. **This belongs in the report as evidence the solver is
trustworthy in the safe direction.** It is the strongest single piece of
validation the team has, and it comes from their own bench data.

---

## 8. The boat — drag-limited, not thrust-limited

Lorentz thrust at these operating points is **9–22 mN**. Drag on an 84×100 mm hull:

| Hull | Cd | drag @ 0.183 m/s | drag @ 0.228 m/s |
|---|---|---|---|
| box | 1.2 | 173 mN | 269 mN |
| teardrop | 0.12 | 17.3 mN | 26.9 mN |

**The box hull does not move. Only a low-Cd teardrop hull moves, and even then
only marginally.** Do not promise a fast boat. The honest claim is "moves a
low-drag hull at low speed", and the report should say so.

---

## 9. Joining — do not use superglue

The team proposed mounting on a boat with cyanoacrylate. **This is a bad idea and
the report should not recommend it.** The literature is unambiguous: steel-to-steel
CA bonds "rapidly lose most of their bond strength" in moist conditions —
hydrolysis scissions the polymer backbone and an oxide layer forms at the
interface, with water wicking along that interface. Saline at 30–40 °C accelerates
both.

**Use mechanical fasteners.** The exit plate should be bolt-on and removable
anyway, so the boat mount is a plate with screw bosses.

---

## 10. Open design questions not yet resolved

These are real and should be flagged as future work, not silently closed:

1. **Side-reservoir electrodes.** Leventis & Gao's high-j DC micropump avoids
   bubbles entirely by putting the platinum electrodes in *side reservoirs* behind
   a porous frit, so electrolysis gas forms away from the flow. This attacks the
   θ term directly and is printable. **Highest-value unexplored change.**
2. **Insulating baffles parallel to flow.** Yakhot & Levin (*AIAA J.* 1978),
   independently confirmed in a 2025 NSGA-II pump optimisation, found that
   nonconducting baffles parallel to the magnetic field attenuate shunting
   currents and raise net current. Estimated gain here is **+5–14%, which is a
   guess and is NOT calibrated against anything.** Report it as a hypothesis.
3. **Thrust is a free measurement.** Calibrate the analytic solver by weighing
   reaction thrust on a kitchen scale with the jet impinging on a cup — no
   dynamometer needed, and it turns a paper model into a validated one.
4. **The electrode/magnet alignment error in the doc.** The doc says the electrodes
   are 120×20×5 mm on the side walls, but w = 40 mm is the electrode gap. Resolve
   which dimension is the plate width when writing the v20 BOM.

---

## 11. Known contradictions in the current doc

These are what the rewrite must fix:

| Location | Current content | Should be |
|---|---|---|
| 3.1 Alat dan Bahan | 4× Ø20×5 N52 discs, 20 mm gap, Rp614,000 | 48× 20×10×5 blocks, 6 stations, 15 mm gap, Rp303,600 |
| Kebutuhan table, field row | 150–250 mT at 20 mm gap | 382 mT at 15 mm gap (modelled; needs Hall probe) |
| Kebutuhan table, flow row | pass 5 ml/s, aspiration 15 ml/s | raise to match intent; do **not** cite 117+ as achieved |
| Salinity in prose | "5%, di dalam rentang 3,5%–5%" | σ = 5.0 S/m ≡ 3.5%; brine demo at σ ≈ 7 ≡ 5%, declared as brine |
| Magnet/electrode spec | v19 geometry | v20 geometry, §3 above |
| Lampiran C (expert contacts) | status tracked outside this repo | see §12 |

---

## 12. Outreach already sent — the emails must match the report

Six researchers emailed from `REDACTED-EMAIL`. **The report and the emails
must not contradict each other**, because a reply makes the mismatch visible.

| To | Affiliation | Sent |
|---|---|---|
| [recipient redacted] | [redacted] | [redacted] |
| [recipient redacted] | [redacted] | [redacted] |
| [recipient redacted] | [redacted] | [redacted] |
| [recipient redacted] | [redacted] | [redacted] |
| [recipient redacted] | [redacted] | [redacted] |
| [recipient redacted] | [redacted] | [redacted] |

All six received the **0.55–0.65 T / 15 mm gap / 48-block** spec. If the report says
150–250 mT at a 20 mm gap, that is a visible contradiction. **Fix the report to
match the emails**, which is also the more defensible design.

Follow-ups are tracked outside this repository.

Not yet contacted, still open:
- [pending recipient redacted]
- [pending recipient redacted]

---

## 13. Files

| Path | What |
|---|---|
| `Desktop\steam-awg\Magnetide-final-design.md` | Lane A design doc, 19 Oct, **now superseded** |
| `Desktop\steam-awg\magnetide_predict.py` | Lane A solver, reproduces baseline exactly |
| `Desktop\steam-awg\magnetide_sweep_geom.py` | first geometry sweep, w found to be untileable at 16 |
| `Desktop\steam-awg\magnetide_sweep_geom2.py` | adds cost, tilability, fuse and end-effect gates |
| `Desktop\mhd_v19_stl\` | 24 STL files from v19, **obsolete geometry** |
| `Desktop\MHD-university-outreach.md` | outreach pack; **its email templates quote the obsolete 0.1 T spec — do not copy from them** |

---

## 14. Rules for the rewrite

1. **Nothing modelled is presented as measured.** Label predictions as predictions.
2. **Preserve the iteration history.** Do not overwrite v17–v19 in place; the
   history is evidence of process.
3. **Declare brine as brine.**
4. **State the chlorine risk.** Do not omit it for neatness.
5. **Do not recommend superglue.**
6. **Do not claim efficiency.** Q and Q/W only.
7. **Do not promise a fast boat.** Drag-limited, low speed, and honest about it.
8. **Keep the claims inventory updated** to match whatever the spec table becomes.
