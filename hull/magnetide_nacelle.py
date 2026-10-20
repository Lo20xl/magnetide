"""Magnetide v20 - square jet-nacelle housing, printable, split up/down.

ONE core, ONE housing: the duct + magnet slots + electrode grooves from the
v19 pump, wrapped in an aircraft-engine-cowl outer skin (rounded rectangular
cross-section, blunt inlet lip, boat-tail). Split on the mid plane so both
halves print flat, split-face down, no supports.

Everything in millimetre NUMBERS (STL convention). Geometry follows
Magnetide-final-design.md Lane A:

  duct          16 (w, y) x 12 (h, z), electrode run L_el = 120 mm
  wall to magnet 1.5 mm -> pole face at |z| = 7.5
  magnet slot   20 wide (y) x 18.5 deep, through the skin, x = -1..121
                accepts 2 tiles (10 mm) + spacer + 3 mm yoke, OR 3 tiles (15)
                + 3 mm yoke - same slot, no reprint to upgrade
  electrode     groove |y| = 8..12, x = -1..121, full 12 mm height (split at 0)
                plate 120 x 12 x 4 slides in before the halves close
  fasteners     3 screws per side (x = 15/75/135, |y| = 46), M3x12, nut trap
  wire exit     one 4 x 5 slot per electrode through core wall + skin

Run:  blender --background --python magnetide_nacelle.py
"""
import math
import os

import bpy
import bmesh

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- duct / core -----------------------------------------------------------
CH_B, CH_C = 8.0, 6.0            # half-width, half-height  (16 x 12 mm)
WALL = 1.5                       # channel ceiling -> magnet pole face
L_EL = 120.0
CORE_Y, CORE_Z = 16.0, 23.0
CORE_X0, CORE_X1 = -15.0, 147.0
EL_Y0, EL_Y1 = 8.0, 12.0         # electrode groove walls
EL_X0, EL_X1 = -1.0, 121.0
SLOT_Y = 10.0                    # magnet slot half-width (2 tiles across)
POLE_Z = WALL + CH_C             # 7.5
SLOT_X0, SLOT_X1 = -1.0, 121.0

# ---- nacelle skin ----------------------------------------------------------
SKIN_B, SKIN_C = 40.0, 26.0      # 80 x 52 mm body
SKIN_T = 2.0
N_EXP = 4.0                      # 4 = square-ish rounded rectangle
SEG = 48
NOSE_X0, NOSE_TIP = -30.0, (24.0, 16.0)   # blunt lip: half-b, half-c
NOSE_X1 = 0.0                    # butt joint with the tube (no overlap -> no nested faces)
TUBE_X0, BODY_X1, TUBE_X1 = 0.0, 147.0, 202.0
TAIL_END = (14.0, 12.0)          # flat base, not a point
BELL_L, BELL_GAIN = 15.0, 1.55   # flare over the first 15 mm from the lip

# ---- parting flange / fasteners -------------------------------------------
SHELF_Z = 3.0
LIP_Y = 50.0
SCREW_X = (15.0, 75.0, 135.0)
SCREW_Y = 46.0
HOLE_R, NUT_R, NUT_DEPTH = 1.6, 3.2, 3.2
BOSS_XY, BOSS_Z = 12.0, 6.0
WIRE_X = (0.0, 120.0)
WIRE_Z = 2.5

# ---- mesh helpers ----------------------------------------------------------


def rect_ring(x, b, c, per_edge=4):
    """EXACT rectangle. Projecting uniform angles onto the boundary puts no
    vertex at the corners, so the inscribed polygon cut them off and the bore
    sagged from 6.0 mm at centre to 3.99 mm at the wall - the plates lost their
    flat seat and the cross-section was not 16x12. Vertices ON the edges, in
    order, lie exactly on the boundary: zero sag."""
    pts = []
    corners = ((b, c), (-b, c), (-b, -c), (b, -c))
    for i in range(4):
        x0, z0 = corners[i]
        x1, z1 = corners[(i + 1) % 4]
        for k in range(per_edge):
            f = k / float(per_edge)
            pts.append((x, x0 + (x1 - x0) * f, z0 + (z1 - z0) * f))
    return pts


def superellipse(x, b, c, n=N_EXP, seg=SEG):
    ring = []
    for i in range(seg):
        t = 2.0 * math.pi * i / seg
        ct, st = math.cos(t), math.sin(t)
        ring.append((x,
                     b * math.copysign(abs(ct) ** (2.0 / n), ct),
                     c * c * 0 + c * math.copysign(abs(st) ** (2.0 / n), st)))
    return ring


def quad_faces(lo, hi, n, flip=False):
    f = []
    for i in range(n):
        j = (i + 1) % n
        f.append((lo[i], lo[j], hi[j], hi[i]) if flip else (lo[i], hi[i], hi[j], lo[j]))
    return f


def make(name, verts, faces):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    seen = set()
    for f in faces:
        key = tuple(sorted(f))
        if key in seen or len(set(f)) != len(f):
            continue
        seen.add(key)
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            continue
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def solid_loft(rings, name):
    verts, faces, m = [], [], 0
    for r in rings:
        verts.extend(r)
    for a, b in zip(rings, rings[1:]):
        lo = list(range(m, m + len(a)))
        m2 = m + len(a)
        hi = list(range(m2, m2 + len(b)))
        faces.extend(quad_faces(lo, hi, len(a)))
        m = m2
    faces.append(tuple(range(len(rings[0]) - 1, -1, -1)))          # cap start
    off = len(verts) - len(rings[-1])
    faces.append(tuple(range(off, off + len(rings[-1]))))          # cap end
    return make(name, verts, faces)


def tube(outer, inner, name):
    verts, faces, m = [], [], 0
    oi, ii = [], []
    for r in outer:
        verts.extend(r)
        oi.append(list(range(m, m + len(r))))
        m += len(r)
    m2 = m
    for r in inner:
        verts.extend(r)
        ii.append(list(range(m2, m2 + len(r))))
        m2 += len(r)
    n = len(outer[0])
    for a, b in zip(oi, oi[1:]):
        faces.extend(quad_faces(a, b, n))
    for a, b in zip(ii, ii[1:]):
        faces.extend(quad_faces(a, b, n, flip=True))
    faces.extend(quad_faces(oi[0], ii[0], n, flip=True))            # mouth annulus
    faces.extend(quad_faces(oi[-1], ii[-1], n))                     # base annulus
    return make(name, verts, faces)


def box(x0, x1, y0, y1, z0, z1, name="box"):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
         (2, 3, 7, 6), (3, 0, 4, 7)]
    return make(name, v, f)


def prism(cx, cy, r, z0, z1, n=16, name="prism"):
    v = [(cx + r * math.cos(2 * math.pi * i / n),
          cy + r * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    v += [(cx + r * math.cos(2 * math.pi * i / n),
           cy + r * math.sin(2 * math.pi * i / n), z1) for i in range(n)]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    return make(name, v, f)


# ---- boolean driver --------------------------------------------------------
FAILURES = []


def boolop(target, tool, op):
    try:
        m = target.modifiers.new("b", "BOOLEAN")
        m.operation = op
        m.solver = "EXACT"
        m.object = tool
        bpy.context.view_layer.objects.active = target
        target.select_set(True)
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(tool, do_unlink=True)
    except Exception as exc:            # noqa: BLE001 - keep building, report at end
        FAILURES.append("%s %s: %s" % (op, tool.name, exc))
        try:
            bpy.data.objects.remove(tool, do_unlink=True)
        except Exception:
            pass


def ease(f, p=0.65):
    return math.sin(0.5 * math.pi * f) ** p


def build():
    # outer skin: nose solid -> body -> boat-tail
    nose, x = [], NOSE_X0
    for i in range(6):
        f = i / 5.0
        s = ease(f)
        b = NOSE_TIP[0] + (SKIN_B - NOSE_TIP[0]) * s
        c = NOSE_TIP[1] + (SKIN_C - NOSE_TIP[1]) * s
        nose.append(superellipse(NOSE_X0 + (NOSE_X1 - NOSE_X0) * f, b, c))
    nose_solid = solid_loft(nose, "nose")

    outer, inner = [], []
    for i in range(3):
        f = i / 2.0
        outer.append(superellipse(TUBE_X0 + (BODY_X1 - TUBE_X0) * f, SKIN_B, SKIN_C))
        inner.append(superellipse(TUBE_X0 + (BODY_X1 - TUBE_X0) * f,
                                  SKIN_B - SKIN_T, SKIN_C - SKIN_T))
    for i in range(1, 7):
        f = i / 6.0
        b = SKIN_B + (TAIL_END[0] - SKIN_B) * ease(f, 1.0)
        c = SKIN_C + (TAIL_END[1] - SKIN_C) * ease(f, 1.0)
        outer.append(superellipse(BODY_X1 + (TUBE_X1 - BODY_X1) * f, b, c))
        inner.append(superellipse(BODY_X1 + (TUBE_X1 - BODY_X1) * f,
                                  b - SKIN_T, c - SKIN_T))
    skin = tube(outer, inner, "skin")

    core = box(CORE_X0, CORE_X1, -CORE_Y, CORE_Y, -CORE_Z, CORE_Z, "core")
    shelf = box(CORE_X0, 150.0, -LIP_Y, LIP_Y, -SHELF_Z, SHELF_Z, "shelf")
    parts = [nose_solid, skin, core, shelf]
    for sx in SCREW_X:
        for sy in (SCREW_Y, -SCREW_Y):
            parts.append(box(sx - BOSS_XY / 2, sx + BOSS_XY / 2,
                             sy - BOSS_XY / 2, sy + BOSS_XY / 2,
                             -BOSS_Z, BOSS_Z, "boss"))

    body = parts[0]
    for p in parts[1:]:
        boolop(body, p, "UNION")

    # duct: bellmouth lip -> straight 16x12 through the tail
    duct_st = []
    for i in range(6):
        f = i / 5.0
        g = 1.0 + (BELL_GAIN - 1.0) * math.cos(0.5 * math.pi * f) ** 2
        duct_st.append(rect_ring(NOSE_X0 + BELL_L * f, CH_B * g, CH_C * g))
    duct_st.append(rect_ring(BODY_X1, CH_B, CH_C))
    duct_st.append(rect_ring(TUBE_X1, CH_B, CH_C))
    boolop(body, solid_loft(duct_st, "duct"), "DIFFERENCE")

    # magnet slots: through the core wall AND the skin, both sides
    for sgn in (1, -1):
        boolop(body, box(SLOT_X0, SLOT_X1, -SLOT_Y, SLOT_Y,
                         sgn * POLE_Z, sgn * 40.0, "slot"), "DIFFERENCE")

    # electrode grooves, full channel height (each half keeps its own 6 mm)
    for y0, y1 in ((EL_Y0, EL_Y1), (-EL_Y1, -EL_Y0)):
        boolop(body, box(EL_X0, EL_X1, y0, y1, -CH_C, CH_C, "groove"), "DIFFERENCE")

    # wire exits: groove -> cavity -> skin
    for wx in WIRE_X:
        for y0, y1 in ((EL_Y1, 55.0), (-55.0, -EL_Y1)):
            boolop(body, box(wx - 2, wx + 2, y0, y1, -WIRE_Z, WIRE_Z, "wire"),
                   "DIFFERENCE")

    # fasteners: through hole both halves, nut trap only below the parting plane
    for sx in SCREW_X:
        for sy in (SCREW_Y, -SCREW_Y):
            boolop(body, prism(sx, sy, HOLE_R, -30, 30, 16, "screw"), "DIFFERENCE")
            boolop(body, prism(sx, sy, NUT_R, -NUT_DEPTH, 0.0, 16, "nut"), "DIFFERENCE")
    return body


def split(body):
    """Clamp each copy to its own z-range. DIFFERENCE with the half you WANT
    removes it, so both sides must be INTERSECT - that inversion produced two
    identical top halves the first time."""
    dup = body.copy()
    dup.data = body.data.copy()
    bpy.context.collection.objects.link(dup)
    boolop(body, box(-100, 300, -150, 150, 0.0, 120.0, "keep_top"), "INTERSECT")
    boolop(dup, box(-100, 300, -150, 150, -120.0, 0.0, "keep_bot"), "INTERSECT")
    body.name, dup.name = "magnetide_housing_top", "magnetide_housing_bottom"
    return body, dup


def tidy(ob):
    """Collapse the degenerate T-junction the electrode groove leaves on the
    parting plane (its wall is coincident with the duct wall at y=+-8, so the
    z=0 cut ends up with three faces on one edge)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.validate(verbose=False)
    ob.data.update()


def stats(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    nonman = [e for e in bm.edges if not e.is_manifold]
    if nonman:
        e = nonman[0]
        print("   non-manifold sample at", [tuple(round(c, 2) for c in v.co)
                                            for v in e.verts])
    loose = sum(1 for v in bm.verts if not v.link_faces)
    vol = bm.calc_volume(signed=False) / 1000.0      # mm3 -> cm3
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    bm.free()
    return nonman, loose, vol, (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    body = build()
    if FAILURES:
        print("BOOLEAN FAILURES:", FAILURES)
        return
    top, bottom = split(body)

    for ob in (top, bottom):
        tidy(ob)
        nm, loose, vol, xr, yr, zr = stats(ob)
        print("%-26s faces=%5d nonmanifold=%d loose=%d vol=%7.1f cm3 (%5.0f g) "
              "x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f"
              % (ob.name, len(ob.data.polygons), len(nm), loose, vol, vol * 1.24,
                 xr[0], xr[1], yr[0], yr[1], zr[0], zr[1]))
        if nm or loose:
            print("   ^^ NOT WATERTIGHT")
        ob.data.validate(verbose=False)
        ob.data.update()

    for ob in (top, bottom):
        st = os.path.join(OUT, ob.name + ".stl")
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if hasattr(bpy.ops.wm, "stl_export"):
            bpy.ops.wm.stl_export(filepath=st, export_selected_objects=True,
                                  global_scale=1.0)
        else:
            bpy.ops.export_mesh.stl(filepath=st, use_selection=True)
        print("WROTE", st)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "magnetide_nacelle.blend"))


main()
