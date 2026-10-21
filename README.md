# Magnetide

A **zero-dependency** analytic screen model and parametric sweep harness for a
benchtop **magnetohydrodynamic (MHD) conduction pump** driven by permanent
magnets, plus an OpenFOAM case validating the hydraulics and Blender-based
verification of the generated STL geometry.

`model/` imports only `math` and `sys`. No numpy, no scipy, no install step.
Run it with bare `python`.

```bash
cd model
python magnetide_predict.py
python magnetide_sweep_geom2.py
```

---

## What this is

A pump that moves saltwater with no moving parts. A DC current is driven across
a channel between electrodes while a transverse magnetic field crosses it; the
Lorentz force pushes the fluid. There is no impeller, no shaft, no seal and no
bearing, so there is nothing to cavitate, leak or wear at the rotating interface.

The design question this repo answers is **which buildable geometry and operating
point** to choose — not "what is B in the bore". For that question a closed-form
model with explicit buildability gates is more useful than a CFD run, because you
can evaluate hundreds of candidates in a second and every candidate that fails a
gate is discarded before it costs us money.

## What this is not

**The CFD does not model the MHD.** [`cfd/`](cfd/) is a real OpenFOAM case, but
it solves the *hydrodynamics* of the v19 flow volume only — no Lorentz body
force, because that term couples back to the drive circuit and cannot be imposed
one-way. It validates that the channel and bellmouth pass fluid correctly. It
says nothing about flow under drive, thrust, efficiency, bubbles, or the magnetic
field. A converged hydrodynamic solve is not an MHD solve. See
[`cfd/README.md`](cfd/README.md).

Separately, the v19 project report labelled the magnetostatic field calculation
as "CFD simulation", which was wrong — that section describes a dipole field
summation, not fluid dynamics. It is renamed accordingly.

**Nothing in `model/` is a measurement.** Every flow rate, velocity and power
figure the solver prints is a *prediction* from an analytic approximation. The
only empirical anchor in this repository is one bench measurement of saline
channel resistance, in [`docs/VALIDATION.md`](docs/VALIDATION.md). Treat that
row as the entire experimental basis of the project.

## The three modelling choices that matter

**1. Electrode length and field extent are separate variables.** `L_el` sets
electrical resistance; `L_drive` sets Lorentz force. Conflating them is the most
common mistake in school-scale MHD designs — a long electrode with short magnets
pays full resistive loss across its whole length but only develops force over the
magnet footprint. Coverage below 100% means you have built a resistor with a
magnet on it, and the sweep treats that as a failed gate rather than a
performance trade-off.

**2. The bubble law lives inside the integrator.** Electrolysis bubbles form on
the electrodes and block part of the conducting area. Effective conductivity is
therefore reduced by a coverage term θ which depends on current density, and it
depends on current density *nonlinearly*, so it cannot be bolted on as a
multiplier at the end. Widening the electrode gap is the only lever that reduces
current density, which is why channel width behaves as a bubble lever rather than
a field lever.

**3. The operating point is found by bisection on the supply rail.** A bench
supply cannot invent voltage. Given a rail, the current settles where
`V_el(I) = V_rail`, and that is found by bisecting `V_el(I)`, which is monotone
in `I`. Sweeping current instead will silently report operating points the
hardware cannot reach.

## Buildability gates

A candidate that fails any one of these is discarded, not scored:

| Gate | Reason |
|---|---|
| `L_drive / L_el ≥ 0.999` | below full coverage, force per unit resistance collapses |
| `w % 10 == 0` and `L % 10 == 0` | a 20×10×5 mm magnet tile must not need cutting |
| `L_el / D_h ≥ 3` | below this the end-effect law invalidates the 1D assumption |
| magnet cost ≤ budget | priced at marketplace floor, not list |
| `I ≤ fuse` | the INA219 shunt's measurement ceiling; beyond it the data is untrustworthy |

Tilability in particular is cheap to forget and expensive to discover: a 16 mm
channel width never divides evenly by a 10 mm tile edge, so every magnet in it
needs cutting.

## Repository layout

```
model/    analytic solver, parametric sweeps, geometry sweeps — pure stdlib
cfd/      OpenFOAM v2512 case validating v19 hydraulics (+ run.sh, logs, samples)
hull/     Blender scripts (import bpy): hull/nacelle generation + STL verification
stl/      v19 printed geometry (24 files)
docs/     model assumptions, validation, design history
```

The two methods are independent and share no code. The analytic model ranks
candidate geometries in milliseconds; the CFD case checks the hydraulics of one
chosen geometry in minutes. They agree that duct hydraulic resistance is about
1.2 kPa — a cross-check between two methods with nothing in common, which is
worth more than either alone.

`hull/` requires Blender and is not part of the solver. It is included because
`measure.py`, `profile.py` and `verify_nacelle.py` do something worth keeping:
they **measure the generated STLs** — bisecting real apertures, printing material
profiles along probe lines — rather than asserting success from a clean exit
code. A checker that says "pass" is not a measurement.

## Validation

The model predicts a saline channel resistance of **4.93 Ω** for the v19
geometry. The measured value from the bench rig is **4.4 Ω**.

That is a **12% error, and it errs conservative** — the model predicts a higher
resistance than reality, which understates flow rather than overselling it. One
validation row of this shape is worth more than a page of "we used advanced
simulation". Full derivation in [`docs/VALIDATION.md`](docs/VALIDATION.md).

## Assumptions, all of them wrong to some degree

Full list with reasoning in [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md).
The load-bearing ones:

- `κ_v = 0.80` velocity derate — an empirical fudge, not a derived constant.
- Uniform perpendicular `B`, `j` and `U` in a brick-shaped control volume.
- Bubble coverage as the sole conductivity correction.
- The electrochemical overpotential term is a constant `E_chem`.
- No Hartmann braking and no back-EMF reduction in the momentum balance.

`v` scales as `√B`, so a 25% shortfall in field gives a 12% shortfall in flow,
not a 25% one. Quote results as bands, not points.

## Current design (v20)

Channel **20 mm (pole gap) × 40 mm (electrode gap) × 120 mm**. 48 blocks of
20×10×5 mm N52 in 6 pole stations, 1 tile deep, 15 mm pole gap, 1.5 mm wall.
Graphite plate electrodes. Modelled at a 12 V rail:

| Fluid | σ (S/m) | I | B | Q | Q/W |
|---|---|---|---|---|---|
| seawater | 5.0 | 1.80 A | 382 mT | 117 ml/s | 5.42 |
| brine | 7.0 | 2.25 A | 382 mT | 131 ml/s | 4.85 |
| strong brine | 10 | 2.81 A | 382 mT | 146 ml/s | 4.35 |

**All of those are modelled, not measured.** They are predictions from a solver
validated against a single resistance measurement and nothing else.

The reason v20 widens the channel to 40 mm: at a fixed rail voltage, current
density is set by the electrode gap alone. Widening it from 16 mm to 40 mm drops
current density from 133 to 75 mA/cm², which cuts bubble coverage from 0.55 to
0.36. That is what makes a brine demo usable without the current running past
the shunt's measurement ceiling.

## Safety

Electrolysis of brine evolves chlorine. Faraday's law gives roughly 0.7–1.0 mg/s
at these currents, against an odour threshold near 0.3 ppm in air. In a small
unventilated room that is reachable within minutes if the anode sits near the
surface.

- Submerge the anode below the free surface.
- Ventilate.
- Cap runs at about two minutes.
- Treat the graphite anode as sacrificial.

Most evolved chlorine disproportionates to hypochlorite in solution rather than
off-gassing, so the inhalation risk is lower than the Faraday number implies —
but it is not zero at high current density.

## Status

Stage: **design and screening, not built.** Nothing has been fabricated from the
v20 geometry. The v19 STLs in `stl/` are superseded by v20 and are kept only as
history.

## Provenance

Written as a student project. Developed with substantial AI assistance from
Mimo, DeepSeek, Codex and Claude — including the model formulation, the sweep
harness, the buildability gates and this documentation. Those systems are
recorded here as tools used, in the same sense that the Blender build and the
Python interpreter are tools used; authorship and citation attribution rest with
the human maintainer, per this file's `CITATION.cff`.

## License

MIT. See [`LICENSE`](LICENSE).
