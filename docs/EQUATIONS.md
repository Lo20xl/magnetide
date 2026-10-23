# Magnetide — Governing Equations

Every equation below is implemented in `model/` and is checkable against the
frozen v21 numbers. GitHub renders the LaTeX; a plain-text reader still gets the
symbol tables.

## Symbols

| Symbol | Meaning | Unit |
|---|---|---|
| $B$ | magnetic flux density in the channel | T |
| $B_r$ | magnet remanence (N52: 1.45) | T |
| $I$ | drive current | A |
| $J$ | current density | A/m² |
| $w$ | electrode gap = channel width | m |
| $h$ | pole gap = channel height | m |
| $L_e$ | electrode length | m |
| $A_c$ | electrode area $= L_e h$ | m² |
| $\sigma$ | fluid conductivity | S/m |
| $\sigma_\text{eff}$ | effective conductivity with gas voids | S/m |
| $\theta$ | gas void fraction | – |
| $E_\text{chem}$ | electrochemical overpotential per cell | V |
| $u$ | mean axial velocity | m/s |
| $\rho$ | fluid density | kg/m³ |
| $\mu$ | dynamic viscosity | Pa·s |
| $D_h$ | hydraulic diameter | m |

---

## 1. Lorentz body force and thrust

The force on the fluid is the cross product of current and field integrated over
the drive volume. With uniform $B$ across the electrode gap and current spread
over the electrode area:

$$\mathbf{F} = \int (\mathbf{J} \times \mathbf{B})\,dV
\quad\Longrightarrow\quad
\boxed{F = I\,B\,w}$$

The thrust per amp is therefore set by one number only:

$$\frac{F}{I} = B\,w$$

> v21: $B = 0.483$ T, $w = 0.040$ m $\Rightarrow$ 19.3 mN/A.
> Spec at 3.06 A: 59.1 mN. MHD-1 (mhd9) measured 12 mN/A.

## 2. Current density

$$J = \frac{I}{A_c} = \frac{I}{L_e h}$$

> v21: $I = 3.06$ A, $L_e h = 0.120 \times 0.014 = 1.68\times10^{-3}$ m²
> $\Rightarrow J = 1\,821$ A/m².

Current **density**, not current, is the quantity the electrochemistry sees —
bubble size tracks $J$ (JTICE-2023), so enlarging the wetted area lowers $J$ and
shrinks bubbles without costing Lorentz force per unit volume.

## 3. Ideal pressure rise (zero flow)

The magnetic pressure available along the drive length:

$$\Delta p_\text{ideal} = J\,B\,L_e = \frac{F}{w\,h}$$

> v21: $1\,821 \times 0.483 \times 0.120 = 105.6$ Pa (10.8 mm H₂O) at zero flow.
> At the operating point (u ≈ 1.8 m/s) back-EMF removes most of it; the spec's
> ~21 Pa is the net rise at speed, not this zero-flow ceiling.

## 4. Back-EMF and the operating point

The flow itself generates a counter-voltage:

$$\mathcal{E}_\text{back} = u\,B\,w$$

so the electrical power delivered to the fluid and the useful mechanical power
are linked by the same $B w$:

$$P_\text{mech} = F\,u = I\,u\,B\,w = \mathcal{E}_\text{back}\,I$$

At short circuit ($u \to 0$) the full $I B w$ acts as pressure; as $u$ rises the
current for a fixed supply voltage falls.

## 5. Channel resistance

Ohm's law over the brine between the electrodes:

$$R = \frac{w}{\sigma_\text{eff}\,L_e\,h}$$

Gas bubbles displace conducting fluid. The spec uses the linear mixture rule

$$\sigma_\text{eff} = \sigma\,(1-\theta)$$

while the Bruggeman effective-medium form

$$\sigma_\text{eff} = \sigma\,(1-\theta)^{3/2}$$

is the more standard choice for dispersed spheres. Both are coded; the linear
form is the conservative (higher-resistance) one at large $\theta$.

> v21: $\sigma = 13.2$ S/m, $\theta = 0.56 \Rightarrow \sigma_\text{eff} = 5.81$ S/m,
> $R = 4.10\ \Omega$ with gas ($1.80\ \Omega$ without).

## 6. Cell voltage and power

$$V_\text{cell} = E_\text{chem} + I R, \qquad P = V_\text{cell}\,I$$

$E_\text{chem} \approx 2.57$ V is the electrolysis tax measured by Delannoy et
al. (2025) and used at our current density. It is fixed per cell and dominates
at low $J$ — which is why MHD pumps are inefficient by construction, not by bad
design.

> v21 at 3.06 A: $V = 15.1$ V, $P = 46$ W (cell), 58 W at the rail.

## 7. Efficiency

$$\eta = \frac{P_\text{useful}}{P_\text{electric}}
= \frac{F\,u}{I\,V_\text{cell}}
= \frac{B\,w\,u}{E_\text{chem} + J\,w/\sigma_\text{eff}}$$

Reading the levers straight off it:

- $\eta \propto B w$ — field times gap is the numerator; this is the only place
  magnets pay.
- $\eta$ falls as $J$ rises (the $J w/\sigma$ term) — so large electrode area is
  an efficiency feature, not just a thermal one.
- $\eta \propto u$ — running the jet faster is the cheapest efficiency gain.

> v21 at 1.8 m/s: $\eta \approx 0.23$%. MHD-1 measured 0.0154% — 15× worse,
> because its $B w$ is similar but its operating current is 118 A.

## 8. Magnetic circuit

Field in the gap from a magnet block of thickness $l_m$, with a steel return
path and leakage folded into $K$:

$$B = K\,\frac{2 B_r\, l_m}{2 l_m + \alpha g},
\qquad \alpha \approx 1.05,\ \ K \approx 0.90$$

This is the formula behind the sweep that shows **thickness saturates, length
does not**: as $l_m \to \infty$, $B \to K B_r$. Doubling $l_m$ from 10 to 20 mm
buys +31%; doubling the number of stations buys +100% of drive length for the
same +100% of tiles.

> v21: $l_m = 10$ mm, $g = 17$ mm $\Rightarrow B \approx 0.69$ T from the bare
> circuit law; the spec's 0.483 T includes fringe/leakage derating.

## 9. Flow regime: hydraulic diameter and Reynolds number

$$D_h = \frac{2wh}{w+h},
\qquad Re = \frac{\rho u D_h}{\mu}$$

and the entrance-length gate that keeps the field covering the driven fluid:

$$\frac{L_e}{D_h} \ge 3$$

> v21: $D_h = 20.7$ mm, $L_e/D_h = 5.8$ ✓. At 1.8 m/s, $Re \approx 3.9\times10^4$
> (turbulent).

## 10. Lorentz-force Reynolds number (JTICE-2022)

The transition criterion that classifies bubbly-jet regimes:

$$Re_L = \frac{\rho\, B\, D_h \sqrt{I}}{\mu}$$

Turbulent breakup of the bubbly jet begins at

$$Re_L \approx 1\,500$$

and bubble size stops responding to the flow at

$$Re_L \gtrsim 2\,000 \quad\text{(JTICE-2023)}$$

> v21: $Re_L \approx 18\,500$ — 12× above breakup. The open question for Chen:
> our $J$ says "electrochemistry regime", our $Re_L$ says "flow regime". Which
> one governs bubble detachment at 0.48 T?

## 11. Bubble size law (JTICE-2023)

Below the critical current density the mean bubble diameter grows with $J$:

$$D_b \propto J \quad \text{for } J < J^* \approx 10^4\ \text{A/m}^2$$

and saturates above it:

$$D_b \approx D_m \approx 270\ \mu\text{m} \quad \text{for } J \gtrsim J^*$$

> v21 runs at $J = 1\,821$ A/m² — 5.5× below $J^*$, deliberately, so bubbles stay
> in the size-controlled regime and the Lorentz force can sweep them off the
> electrodes.

## 12. Tilability constraints

The magnet grid forces two divisibility rules, so the geometry stays buildable
from whole tiles:

$$w = 10\,n_w,\qquad L_e = 20\,n_s$$

with $n_w$ tiles across the gap and $n_s$ stations along the flow.

> v21: $w=40$ (4 tiles), $L_e=120$ (6 stations) ✓.

---

## Where each equation lives

| Equation | Code |
|---|---|
| §1, §2, §5, §6, §7 | `model/magnetide_predict.py` |
| §8 magnetic circuit | `model/magnetide_predict.py::gap_field` |
| §9, §10 hydraulic regime | `docs/VALIDATION.md`, CFD case |
| §11 bubble law | `docs/ASSUMPTIONS.md` |
| §12 tilability gates | `model/magnetide_sweep_geom2.py` |
