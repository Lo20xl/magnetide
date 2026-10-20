"""Print the material profile along each probe line, then bisect each
transition from the bracket the profile actually shows."""
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


def profile(name, fn, start, end, step=1.0):
    """fn(t) -> point. Prints the # / . pattern so a bad bracket is visible."""
    n = int((end - start) / step)
    s = "".join("#" if mat(fn(start + i * step)) else "." for i in range(n + 1))
    print("%-34s %6.1f->%-6.1f  %s" % (name, start, end, s))
    return s


def first_change(fn, lo, hi):
    """Return the parameter where the profile flips, scanning lo -> hi."""
    a = mat(fn(lo))
    for i in range(4001):
        t = lo + (hi - lo) * i / 4000.0
        if mat(fn(t)) != a:
            return t
    return None


lines = [
    ("z up, y=0 x=60 (ceiling)", lambda t: (60, 0, t), 0, 16),
    ("y out, z=7 x=60 (wall/groove)", lambda t: (60, t, 7), 0, 20),
    ("z up, y=0 x=60 (below slot)", lambda t: (60, 0, t), 0, 45),
    ("y out, z=0 x=61 (groove)", lambda t: (61, t, 0), 0, 20),
    ("y out, z=1.5 x=15 (screw top)", lambda t: (15, 46 + t, 1.5), -10, 10),
    ("y out, z=-1.5 x=15 (nut trap)", lambda t: (15, 46 + t, -1.5), -10, 10),
    ("y out, z=4 x=15 (boss)", lambda t: (15, t, 4), 30, 65),
    ("x along, y=0 z=0 (duct run)", lambda t: (t, 0, 0), -30, 210),
]
print("profile: '#' material  '.' empty  (1 mm per character)")
for name, fn, a, b in lines:
    profile(name, fn, a, b)

print("\ntransitions (first flip scanning forward):")
checks = [
    ("duct ceiling (z, y=0)", lambda t: (60, 0, t), 0, 16, 6.0),
    ("pole face (z, y=0)", lambda t: (60, 0, t), 6.1, 45, 7.5),
    ("duct half-width (y, z=0, x=-10)", lambda t: (-10, t, 0), 0, 20, 8.0),
    ("groove outer wall (y, z=0)", lambda t: (61, t, 0), 9, 20, 12.0),
    ("screw hole radius (top)", lambda t: (15, 46 + t, 1.5), -10, 10, 1.6),
    ("nut trap radius (bottom)", lambda t: (15, 46 + t, -1.5), -10, 10, 3.2),
    ("boss outer (y, z=4)", lambda t: (15, t, 4), 65, 30, 52.0),
]
for label, fn, lo, hi, want in checks:
    got = first_change(fn, lo, hi)
    ok = got is not None and abs(abs(got) - abs(want)) <= 0.1 if "radius" in label         else (got is not None and abs(got - want) <= 0.1)
    print("%-32s want %6.2f  got %s  %s"
          % (label, want, ("%.3f" % got) if got is not None else "none",
             "PASS" if ok else "FAIL"))
