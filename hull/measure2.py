"""Bisect the real apertures. '12/12 checks passed' is not a measurement."""
import os

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "magnetide_nacelle.blend"))
halves = [o for o in bpy.data.objects if o.name.startswith("magnetide_housing")]
bvhs = [BVHTree.FromObject(h, bpy.context.evaluated_depsgraph_get())
        for h in halves]
UP = Vector((0.0, 0.0, 1.0))


def parity(bvh, p):
    o, n = Vector(p), 0
    for _ in range(64):
        loc, _, _, _ = bvh.ray_cast(o, UP, 1e6)
        if loc is None:
            break
        n += 1
        o = loc + UP * 1e-4
    return n % 2 == 1


def mat(p):
    return 1 if any(parity(b, p) for b in bvhs) else 0


def bisect(step, lo, hi, target=1, iters=60):
    """Parameter at which the probe first reads `target` (material)."""
    for _ in range(iters):
        m = 0.5 * (lo + hi)
        if step(m) != target:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


cases = [
    ("duct half-width   x=60 z=0", lambda t: mat((60, t, 0.0)), 0.0, 20.0, 8.0),
    ("duct half-height  x=60 y=0", lambda t: mat((60, 0, t)), 0.0, 20.0, 6.0),
    ("pole wall, y=0", lambda t: mat((60, 0, t)), 6.0, 12.0, 7.5),
    ("slot starts above 7.5", lambda t: mat((60, 0, t)), 8.0, 40.0, 0.0),
    ("groove outer wall x=61", lambda t: mat((61, t, 0.0)), 9.0, 30.0, 12.0),
    ("screw hole radius x=15", lambda t: mat((15, 46 + t, 0.0)), 0.0, 12.0, 1.6),
    ("nut trap radius   x=15", lambda t: mat((15, 46 + t, -1.5)), 0.0, 12.0, 3.2),
    ("boss outer y      x=15", lambda t: mat((15, t, 4.0)), 40.0, 60.0, 52.0),
]
print("%-30s %10s %10s %s" % ("probe", "measured", "expected", "verdict"))
for label, step, lo, hi, want in cases:
    got = bisect(step, lo, hi)
    if want == 0.0:
        # first point where the probe reads NOT material, i.e. gap starts
        lo2, hi2 = lo, hi
        for _ in range(60):
            m = 0.5 * (lo2 + hi2)
            if mat((60, 0, m)) == 1:
                lo2 = m
            else:
                hi2 = m
        got = 0.5 * (lo2 + hi2)
        want = 7.5
        ok = abs(got - want) <= 0.05
    else:
        ok = abs(got - want) <= 0.05
    print("%-30s %10.3f %10.3f %s" % (label, got, want, "PASS" if ok else "FAIL"))

hw = bisect(lambda t: mat((60, t, 0.0)), 0.0, 20.0)
hh = bisect(lambda t: mat((60, 0, t)), 0.0, 20.0)
print("\nCHANNEL SECTION  %.3f x %.3f mm   (spec 16.000 x 12.000)" % (2 * hw, 2 * hh))
