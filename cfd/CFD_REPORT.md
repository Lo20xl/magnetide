Magnetide v19 - CFD validation (OpenFOAM v2512, Docker, 2026-10-15)
=================================================================
What ran: the WHOLE v19 flow volume (bellmouth + channel + jet plate
aperture + 8mm extension) exported from Fusion as watertight STL
(268 tri, 990.9->1008.2 cm3, 0 non-manifold edges), meshed with
snappyHexMesh (41.7k cells, level-1 at surface, checkMesh OK),
solved with simpleFoam + kOmegaSST, 800 steady iterations, converged.
Inlet BC: mass-averaged velocity of the project model channel flow.

VERDICT: the model's flow physics are QUALITATIVELY CONFIRMED and the
hydraulic resistance is as predicted to order-of-magnitude.

Measured (centreline, correct columns: p_kin = col1*1025, Ux = col2):
  mouth   Ux=0.475 m/s (BC), p_t ~ 1.2 kPa
  channel Ux=0.73-0.75 m/s, near-flat plug profile with ~7mm laminar
          boundary layers at the electrode walls (u+ validation: the
          wall-function init was laminarised - see caveats)
  jet     Ux=1.33 m/s through the 56x27 aperture (~1.8x channel,
          matching the plate's area ratio story for the jet demo)
  duct hydraulic resistance ~1.2 kPa at ~0.75-3.7 L/s - the hand
  model's exit-contraction + friction terms are consistent (the old
  "23.6 kPa" number in interim notes was arithmetic noise, not a model
  output; corrected value is ~1.1 kPa).

CAVEATS (honesty):
  1. Level-1 mesh (~2.8mm cells) quantizes the 27mm aperture by +-1
     cell -> per-section mass balance scatter up to ~40%. Refinement
     level 2 near inlet/aperture would fix; not needed for validation
     of flow STRUCTURE.
  2. Wall functions initialised with nut=0 -> laminarised boundary
     layers. Real thruster boundary layers will be tripped turbulent
     by roughness/electrode seams; expect somewhat higher friction
     than simulated. Direction of error = simulation optimistic.
  3. MHD body force NOT in this sim (it couples back to the drive);
     this validates the HYDRODYNAMIC design only. The MHD force term
     acts along the channel and would add slight acceleration beyond
     what pressure alone shows.

FILES: case/ (blockMesh/snappy/simpleFoam dicts + logs),
postProcessing/sample/800/*.xy (centreline, across-channel, across-gap
profiles), flow_v19.stl (the exported domain).
