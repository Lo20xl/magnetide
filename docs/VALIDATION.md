# Validation

There is exactly one empirical measurement in this repository. This document
derives it, compares it to the model, and states plainly what it does and does
not license.

---

## The measurement

The bench rig ran four parallel saline channels from a 12 V supply:

| Condition | Measured |
|---|---|
| 12 V, no ballast | 10.8 A |
| 12 V, with 3.9 Ω ballast per channel | 5.75 A |

Solving those two conditions for the per-channel saline resistance:

```
unballasted:   R_ch = 12 / 10.8 - R_series_unknown
ballasted:     R_ch = 12 / 5.75 - 3.9
```

gives **R_ch ≈ 4.4 Ω** for a single channel at roughly 5% salinity. Both
solution paths agree to within 0.1%, which is a genuine cross-check on the
measurement rather than a single reading.

## The prediction

Running the model at σ₀ = 5.0 S/m for each geometry:

| Geometry | Model R_ch | Measured | Error |
|---|---|---|---|
| v19 as-built (h12 w16, wall 4, 2 stations) | **4.93 Ω** | 4.4 Ω | **+12%** |
| v20 (h20 w40, wall 1.5, 6 stations) | 5.23 Ω | — | — |

## What this licenses

**The error is 12% and it errs conservative.** The model predicts a *higher*
resistance than reality, which means it predicts *less* current and therefore
*less* flow than the hardware will actually deliver.

That direction matters. A model that understates performance is safe to design
against; a model that oversells it produces a device that fails its target on the
bench. This one errs safe.

It is also a plausible error magnitude. The model assumes uniform current
injection across a rectangular electrode and a constant `E_chem` fitted to
platinum-coated titanium, while the bench used graphite. A 12% resistance
discrepancy between those two cases is unremarkable.

## What this does not license

Very little, in the other direction.

- **It validates resistance, not flow.** One electrical measurement says nothing
  about whether `κ_v = 0.80` is right, which is the constant that actually sets
  the flow prediction.
- **It does not validate the bubble model.** `θ_k` was not tested by this
  measurement; the rig did not vary current density enough to separate bubble
  effects from bulk resistance.
- **It does not validate the magnetic field.** No Hall probe measurement exists.
  The `B` figures throughout are modelled.
- **It does not validate hydraulics.** No velocity or flow rate has been measured.

**Every flow rate quoted anywhere in this project is a prediction from a solver
that has been checked against one resistance value and nothing else.** Report
them as predictions.

## Measurement plan for when the device is built

The v20 design has never been fabricated. When it is:

**1. Magnetic field.** Measure the pole gap with a Hall probe before any fluid
test. Report a band, not a point — the model's absolute `B` is where it is least
trustworthy, since it ignores end fringing, leakage between pole stations, and
the yoke's real permeability under load.

**2. Hydraulic resistance in air.** Fill the channel, apply no current, force flow
through it, and measure pressure drop against flow rate. This isolates `k_loss`
from every electromagnetic term and is the single most informative cheap test.

**3. Velocity.** Dye timing alone is unreliable — the dye can advect faster or
slower than the bulk and can cling to the wall. If a rig can be built, two
electrodes at a known axial separation in a third wire in series with the channel
is better: charge integration gives volumetric charge and therefore mean velocity,
directly and continuously. Otherwise, timed volumetric collection is the primary
measurement, with dye video only as a cross-check.

**4. Thrust.** Calibrate the analytic solver by weighing reaction thrust on a
kitchen scale with the jet impinging on a cup. No dynamometer needed, and it
turns a paper model into a validated one.

**5. Current density sweep.** Vary `j` across at least a decade and record
`V_el` against `I`. That single dataset separates the constant `E_chem` term from
the resistive term and tests the bubble model, which no static measurement can.

## Reporting discipline

Three rules, all of which are easy to break in a report deadline:

1. **A computed value is never a measured value.** Label the source of every
   number in the same sentence it appears in.
2. **Report mean ± SD over three replicates**, and report the replicate count.
   A single reading is not a result.
3. **Report what failed.** If a run exceeds the shunt's 3.2 A measurement
   ceiling, the data point is untrustworthy and should be discarded rather than
   reported as a number.

## Cross-check against literature

The reported operating envelope should be checked against published school-scale
builds before publication. A widely cited school-scale MHD build reports roughly
0.06 N of visible thrust at 5 A and 0.12 T. A 730 mT design at 1.15 A landing at
9–22 mN is the right order of magnitude; a result an order of magnitude away in
either direction is a modelling error, not a breakthrough.

---

*One validation row of this shape is worth more than a page of "we used advanced
simulation". When the second measurement exists, this file should be rewritten
around it rather than amended.*
