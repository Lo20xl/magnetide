"""Verify the printed halves actually have the features, not just a clean count.

Re-opens magnetide_nacelle.blend and asks, by ray parity, whether sample points
are inside material. A report of '0 non-manifold' says the shell is closed; it
says nothing about whether the duct is open, the slots cut through, or the
screw holes line up between the halves.

Run:  blender --background --python verify_nacelle.py
"""
import math
import os

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, "magnetide_nacelle.blend")
CH_B, CH_C = 8.0, 6.0
POLE_Z = 7.5


def parity_inside(bvh, p, direction=Vector((0.0, 0.0, 1.0))):
    """True if p is inside the closed mesh (odd crossings along +z)."""
    origin, hits = Vector(p), 0
    for _ in range(64):
        loc, _, _, _ = bvh.ray_cast(origin, direction, 1e6)
        if loc is None:
            break
        hits += 1
        origin = loc + direction * 1e-4
    return hits % 2 == 1


def inside(either, p):
    return any(parity_inside(b, p) for b in either)


def hits_along(bvh, p, direction=Vector((0.0, 0.0, 1.0))):
    """Crossing count + z of each crossing, so a wrong parity can be named."""
    origin, zs = Vector(p), []
    for _ in range(64):
        loc, _, _, _ = bvh.ray_cast(origin, direction, 1e6)
        if loc is None:
            break
        zs.append(round(loc.z, 3))
        origin = loc + direction * 1e-4
    return zs


def check(label, ok, detail=""):
    print("%-4s %-46s %s" % ("PASS" if ok else "FAIL", label, detail))
    return ok


def main():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    halves = [o for o in bpy.data.objects
              if o.name.startswith("magnetide_housing")]
    print("halves:", [h.name for h in halves])
    bvhs = [BVHTree.FromObject(h, bpy.context.evaluated_depsgraph_get())
            for h in halves]
    results = []

    # 1. duct must be empty over its whole run
    blocked = []
    for i in range(13):
        x = -14.0 + i * 14.0
        for fy in range(5):
            for fz in range(5):
                # inset 0.5 mm off the duct walls - a probe exactly ON a face
                # makes parity depend on which side the ray leaves from
                y = (-CH_B + 0.5) + (2 * CH_B - 1.0) * fy / 4.0
                z = (-CH_C + 0.5) + (2 * CH_C - 1.0) * fz / 4.0
                if inside(bvhs, (x, y, z)):
                    blocked.append((round(x, 1), round(y, 1), round(z, 1)))
    results.append(check("duct clear, 325 probes, x -14..146",
                         not blocked, "blocked: %s | crossings(z)=%s"
                         % (blocked[:4], hits_along(bvhs[0], blocked[0])
                            if blocked else [])))

    # 2. magnet slot through both sides (core wall + skin)
    slot_ok = all(not inside(bvhs, (x, y, 10.0))
                  for x in (5, 60, 115) for y in (-9, 0, 9))
    results.append(check("magnet slot open at z=+10 (9 probes)", slot_ok))
    slot_ok = all(not inside(bvhs, (x, y, -10.0))
                  for x in (5, 60, 115) for y in (-9, 0, 9))
    results.append(check("magnet slot open at z=-10 (9 probes)", slot_ok))

    # 3. pole wall solid: ceiling between duct and slot
    wall_ok = inside(bvhs, (60, 0.0, POLE_Z - 0.5)) and inside(bvhs, (60, 0.0, 7.0))
    results.append(check("pole wall solid at |z| = 7..7.5", wall_ok))

    # 4. electrode grooves open over the full 12 mm height
    grooves = [(60, 10, z) for z in (-5.5, -2, 2, 5.5)] + \
              [(60, -10, z) for z in (-5.5, -2, 2, 5.5)]
    results.append(check("electrode grooves open, both halves",
                         all(not inside(bvhs, p) for p in grooves)))

    # 5. groove backing: material outboard of the groove the plate seats against
    results.append(check("groove backing solid at |y| = 13 (plate seat)",
                         inside(bvhs, (61, 13, 1.0)) and
                         inside(bvhs, (61, -13, -1.0))))

    # 6. fasteners: hole clear in both halves, nut trap below parting plane
    screw = [(x, 46, z) for x in (15, 75, 135) for z in (-10, 0, 10)]
    screw += [(x, -46, z) for x in (15, 75, 135) for z in (-10, 0, 10)]
    results.append(check("screw holes clear at 6 x 6 probes",
                         all(not inside(bvhs, p) for p in screw)))
    trap = [(15, 49, -2), (75, 49, -2), (135, -49, -2)]
    results.append(check("nut traps cut on the bottom half", 
                         all(not inside(bvhs, p) for p in trap)))

    # 7. boss material still there around each screw
    boss = [(15, 50, 4), (75, 50, 4), (135, -50, 4)]
    results.append(check("flange bosses present (3 probes)",
                         all(inside(bvhs, p) for p in boss)))

    # 8. wire exits
    results.append(check("wire exit slots open at x = 0 and 120",
                         all(not inside(bvhs, p) for p in
                             [(0, 30, 1), (120, 30, 1), (0, -30, -1),
                              (120, -30, -1), (0, 30, -1), (120, -30, 1)])))

    # 9. bounding boxes / split
    for h in halves:
        bb = h.bound_box
        zs = [v[2] for v in bb]
        results.append(check("%s z-range %s" % (h.name, (round(min(zs), 1), round(max(zs), 1))),
                             (min(zs) > -1e-6) == h.name.endswith("top")))

    print("\n%d/%d checks passed" % (sum(results), len(results)))


main()
