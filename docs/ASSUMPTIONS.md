# Model assumptions

Every assumption below is wrong to some degree. The question is whether it is
wrong in a direction that matters for choosing between candidate designs.

The model is a **screening tool**. It exists to rank buildable geometries against
each other in under a second per candidate. It is not a substitute for
measurement, and no number it produces should be reported as an achieved result.

---

## Control volume

A straight channel guiding fluid at velocity `U`, with a cross-flow magnetic
field `B`, and electrodes forcing current density `j` perpendicular to both.

All three fields are assumed **perfectly perpendicular and uniform** across a
brick-shaped control volume of extent `L_U`, `L_B`, `L_j` along each vector.
Real channels have fringing at the pole edges and non-uniform current injection
near the electrode lips; both are neglected.

## Separating the two lengths

| Symbol | Meaning | Sets |
|---|---|---|
| `L_el` | electrode length | electrical resistance |
| `L_drive` | axial extent of the field | Lorentz force |

These are **not** the same. A long electrode with short magnets pays full
resistive loss across `L_el` but only develops force across `L_drive`, so force
per unit resistance scales as `L_drive / L_el`. Below 100% coverage the device
should be described as a resistor with a field on it rather than as a pump.

Coverage is enforced at 100% as a buildability gate rather than treated as a
trade-off, because at less than full coverage the flow rate is unchanged while
power rises proportionally.

## Magnetic field

```
B = 2 * k_yoke * Br * l_m / (2 * l_m + 1.05 * g)
```

with `g = h + 2 * wall` the magnet gap, `l_m` the magnet thickness per side, and
`k_yoke = 0.90` an efficiency factor for the yoke.

This is a mean-field approximation. It assumes a closed low-reluctance return
path and does not model leakage between adjacent pole stations, end fringing,
or the yoke's actual permeability under the operating flux density. `Br = 1.45 T`
assumes N52-grade NdFeB at room temperature.

## Bubble coverage

Electrolysis blocks part of the electrode area:

```
θ  = 1 - exp(-θ_k * j_d)        θ_k = 0.006,  j_d in mA/cm²
σ_eff = σ0 * (1 - θ)
```

This term lives **inside** the integrator, not applied to the final answer,
because θ depends on current density nonlinearly. Applying it afterward is
equivalent to assuming a constant current density that happens to equal the mean,
which is not true in a channel where the rail sets the current.

A Bruggeman lower bound `σ0 * (1 - θ)^1.5` is quoted alongside the linear form.
Treat the pair as a band rather than picking one.

`θ_k` is fitted, not derived from first principles. It is the single least
trustworthy constant in the model.

## Electrochemistry

The electrode voltage is

```
V_el = E_chem + I * R
```

where `E_chem = 2.57 V` is a constant electrochemical term drawn from the
literature fit for platinum-coated titanium electrodes.

**Graphite behaves differently.** The constant-term assumption is approximate,
and at higher current densities the deviation grows. The model does not distinguish
anode from cathode behaviour and treats `E_chem` as symmetric, which it is not.

## Hydraulic side

The momentum balance is

```
f_L = rho * U * dU/dx  →  U = sqrt(2 * f_L * L_U / rho)
```

which for a uniform body force reduces to

```
v = k_v * sqrt(I * B / (rho * h * L_el))
```

and

```
Q = v * w * h
```

Three things are neglected:

**No Hartmann braking.** The transverse field damps the velocity profile flat
and raises wall shear. For `Ha < 10` this correction is small; for a 0.6 T field
across a 20 mm gap with seawater, `Ha ≈ 4800`, which is emphatically not small.
The model proceeds anyway, which means the hydraulic side is optimistic.

**No back-EMF reduction.** As the fluid accelerates it generates a
counter-electromotive force `UB L_j` that reduces net current. Ignored.

**`k_v = 0.80` is an empirical derate**, not a derived constant. It is intended
to absorb end losses, non-uniformity and profile effects. It is the fudge factor
that makes the model land in the right order of magnitude, and it should be
recalibrated the moment a first real velocity measurement exists.

## Electrical side

```
j = I / (h * L_el)
R = w / (sigma_eff * h * L_el)
```

**At a fixed rail voltage, current density is set by `w` alone.** Height enters
the electrical side only through the magnetic gap `g`, not through `j`. This is
the structural result that makes the optimisation separate cleanly: `h` is a
field lever, `w` is a bubble lever, and they do not fight each other directly.

Conductivity `σ0 = 5.0 S/m` corresponds to seawater at roughly 35 g/l. Higher
salinity raises `σ0` and therefore flow, but also raises `j`, which raises `θ`,
so the marginal return falls steeply — from about 4.5 to 0.9 ml/s per S/m across
σ = 5 to 35.

## Operating point

`V_el(I)` is monotone in `I`, so the operating point a real supply reaches is
found by **bisection** on `V_el(I) = V_rail`, not by sweeping current.

Sweeping current will report operating points the hardware cannot reach. The
difference matters most at low conductivity, where the resistive term dominates
and the current at the rail is far below the nominal rating.

## Gates applied to every candidate

| Gate | Threshold | Reason |
|---|---|---|
| coverage | `L_drive / L_el ≥ 0.999` | force per unit resistance collapses below full coverage |
| tilability | `w % 10 == 0`, `L % 10 == 0` | 20×10×5 tile must not need cutting |
| end effect | `L_el / D_h ≥ 3` | 1D assumption invalid below this |
| budget | magnet cost ≤ limit | priced at marketplace floor price |
| fuse | `I ≤ 3.2 A` | INA219 shunt measurement ceiling |

## What is deliberately not modelled

- Thermal effects and temperature dependence of conductivity
- Chlorine production and gas evolution dynamics
- Hull drag for the boat configuration
- Transient start-up behaviour
- Non-uniform magnetic field along the channel

## Where the model is likely to be badly wrong

1. **Hydraulics at high Hartmann number.** The omission of Hartmann braking is
   the largest known error and it biases flow optimistic.
2. **Bubble coverage.** `θ_k` is fitted and the linear form is the optimistic
   bound.
3. **Electrochemistry with graphite.** The constant `E_chem` was fitted to a
   different electrode material.
4. **End effects on efficiency.** End currents add loss without adding output;
   the model does not see them.
