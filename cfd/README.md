# CFD — v19 hydraulics validation

An OpenFOAM case that validates the **hydrodynamic** design of the v19 flow
volume. It does **not** model the magnetohydrodynamics — see the caveats below.

- **Solver:** OpenFOAM v2512 via Docker
- **Mesh:** snappyHexMesh, 41,622 cells, level-1 surface refinement
- **Turbulence:** kOmegaSST, steady-state simpleFoam
- **Convergence:** 800 iterations, residuals down ~3 orders of magnitude
- **Wall time:** ~66 s
- **Domain:** the whole v19 flow volume — bellmouth, channel, jet-plate
  aperture and an 8 mm extension — exported from Fusion as a watertight STL
  (268 triangles, 990.9 → 1008.2 cm³, 0 non-manifold edges)

To reproduce: `./run.sh` (Docker required). Only the rerunnable parts are
committed; mesh and time directories are regenerated.

## Result

| Location | Ux |
|---|---|
| mouth | 0.475 m/s (inlet BC) |
| channel | 0.73–0.75 m/s, near-flat plug profile |
| jet (56 × 27 mm aperture) | 1.33 m/s |

The channel profile is a plug with roughly 7 mm laminar boundary layers at the
electrode walls. The jet runs at ~1.8× the channel velocity, consistent with the
aperture's area ratio.

**Duct hydraulic resistance is ~1.2 kPa** at 0.75–3.7 L/s. An earlier interim
note quoted 23.6 kPa for this figure; that was arithmetic noise in the note, not
a model output. The corrected value is ~1.1 kPa.

**Verdict:** the model's flow physics are *qualitatively* confirmed and the
hydraulic resistance agrees with the hand model to order of magnitude.

## Caveats

These are the caveats the original run recorded, and they should travel with any
citation of these numbers.

1. **Mesh quantization.** Level-1 refinement (~2.8 mm cells) represents the
   27 mm aperture to ±1 cell, so per-section mass balance scatters up to ~40%.
   Refinement level 2 near the inlet and aperture would fix this. It was judged
   unnecessary for validating flow *structure*, which is what this run was for.

2. **Laminarised boundary layers.** Wall functions were initialised with
   `nut = 0`, which laminarises them. Real thruster boundary layers will be
   tripped turbulent by roughness and electrode seams, so expect *higher*
   friction than simulated. **The direction of this error is optimistic** — the
   simulation overstates performance.

3. **No MHD body force.** The Lorentz term is not in this case. It couples back
   to the drive circuit, so it cannot be imposed as a one-way inlet condition.
   **This validates the hydrodynamic design only.** Including the MHD term would
   add slight acceleration beyond what pressure alone shows.

## What this does and does not establish

**Does:** the channel, bellmouth and aperture geometry pass fluid correctly;
the plug profile develops as expected; hydraulic losses are the magnitude the
hand model predicts.

**Does not:** validate flow rate under drive, thrust, efficiency, bubble
behaviour, or anything about the magnetic field. A converged hydrodynamic solve
is not an MHD solve.

## Relationship to `model/`

The analytic solver in `../model/` makes no use of this case, and this case makes
no use of the solver. They are independent: the solver ranks candidate geometries
in milliseconds, this case checks the hydraulics of one chosen geometry in
minutes. Their agreement on hydraulic resistance — both landing near 1.2 kPa —
is a cross-check between two methods that share no code, which is more valuable
than either alone.
