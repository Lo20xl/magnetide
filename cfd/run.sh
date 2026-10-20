#!/usr/bin/env bash
# Magnetide CFD — reproduce the v19 hydraulics validation.
#
# Requires Docker. No local OpenFOAM install needed.
# The committed case contains only the rerunnable parts (0/, system/,
# triSurface/, postProcessing/ samples and logs). The 28 MB of mesh
# (constant/polyMesh) and solver time directories are NOT committed;
# this script regenerates them.
#
# Total runtime on the original machine: ~66 s for the solver stage,
# plus meshing. Budget a few minutes end to end.
#
# NOTE: the solver stage writes into ./case, which is the committed
# directory. Run this from a COPY if you want to keep the committed
# state pristine:
#
#     cp -r cfd /tmp/magnetide-cfd && cd /tmp/magnetide-cfd && ./run.sh

set -euo pipefail

FOAM_TAG="v2512"          # the version this case was authored against
CASE="$(cd "$(dirname "$0")" && pwd)/case"

docker() {
    command docker run --rm -v "$CASE":/case -w /case \
        opencfd/openfoam-dev:${FOAM_TAG} "$@"
}

echo "== 1. blockMesh =="
docker blockMesh > logs/run.blockMesh.log 2>&1

echo "== 2. surfaceFeatureExtract =="
docker surfaceFeatureExtract > logs/run.surfaceFeatureExtract.log 2>&1

echo "== 3. snappyHexMesh (two-pass: -overwrite on pass 2) =="
docker snappyHexMesh -overwrite -mode full > logs/run.snappy.log 2>&1

echo "== 4. checkMesh =="
docker checkMesh | tee logs/run.checkMesh.log
grep -q "Mesh OK." logs/run.checkMesh.log \
    || { echo "FAILED: checkMesh did not report 'Mesh OK.'"; exit 1; }

echo "== 5. potentialFoam (initial potential field) =="
docker potentialFoam -overwrite > logs/run.potentialFoam.log 2>&1

echo "== 6. simpleFoam (800 steady iterations) =="
docker simpleFoam > logs/run.simpleFoam.log 2>&1
tail -3 logs/run.simpleFoam.log

echo "== 7. sample =="
docker sample > logs/run.sample.log 2>&1
ls -1 postProcessing/sample/800/ 2>/dev/null || true

echo
echo "Done. Profiles land in case/postProcessing/sample/800/:"
echo "  centreline_p_U.xy      axial centreline — the primary result"
echo "  acrossChannel_y_p_U.xy cross-section at the electrodes"
echo "  acrossGap_z_p_U.xy     across the pole gap"
echo "  throatLine_p_U.xy      through the throat"
echo
echo "Expected centreline Ux: mouth ~0.475 m/s (inlet BC), channel ~0.73-0.75 m/s,"
echo "jet ~1.33 m/s through the 56x27 mm aperture."
echo "See CFD_REPORT.md for the full result and its caveats."
