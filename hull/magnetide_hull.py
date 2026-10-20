"""Magnetide hull generator - teardrop fairing around the v19 core.

Builds a closed, manifold solid directly from a station table, so the shape is
exact and re-runnable instead of eyeballed in the viewport. That matters here:
a subdiv surface gives slivers and a non-manifold rim, and the slicer will not
shut up about it.

Geometry (mm, X along flow, Z up):
  outer skin   nose 0 -> -45   body -45 .. 0   tail 0 .. +160  (taper < 12 deg)
  inner duct   straight 16 x 12 prism, bellmouth flare over the first 15 mm
  end caps     annular at both ends, so the mesh is watertight

Run headless:
  blender --background --python magnetide_hull.py
"""
import math
import os

import bpy

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- parameters ------------------------------------------------------------
BODY_B, BODY_C = 42.0, 20.0      # body half-width, half-height  (84 x 40 mm)
DUCT_B, DUCT_C = 8.0, 6.0        # channel half-width, half-height (16 x 12 mm)
NOSE_L, TAIL_L = 45.0, 160.0     # nose / tail length
BELL_L = 15.0                    # bellmouth flare length
BELL_GAIN = 1.55                 # mouth half-dims = duct * gain
TAIL_B, TAIL_C = 12.0, 8.0       # small flat base, NOT a point (points stall)
SEG = 64                         # points per ring
NOSE_N, TAIL_N = 8, 10           # stations


def ring(x, b, c, seg=SEG):
    """Rounded-rectangle ring as a superellipse; smooth, closed, no slivers."""
    n = 3.0
    pts = []
    for i in range(seg):
        t = 2.0 * math.pi * i / seg
        ct, st = math.cos(t), math.sin(t)
        y = b * math.copysign(abs(ct) ** (2.0 / n), ct)
        z = c * math.copysign(abs(st) ** (2.0 / n), st)
        pts.append((x, y, z))
    return pts


def stations():
    """(x, outer half-b, outer half-c) from nose tip to tail base."""
    st = []
    # nose: quarter-cosine ease-in so the lip stays full and the tip is blunt
    for i in range(NOSE_N):
        f = i / (NOSE_N - 1.0)
        s = math.sin(0.5 * math.pi * f) ** 0.65
        st.append((-NOSE_L * (1.0 - f), BODY_B * s + 1.0, BODY_C * s + 1.0))
    # body: straight
    st.append((0.0, BODY_B, BODY_C))
    st.append((TAIL_L * 0.25, BODY_B * 0.97, BODY_C * 0.97))
    # tail: near-linear taper to a small flat base
    for i in range(1, TAIL_N + 1):
        f = i / float(TAIL_N)
        x = TAIL_L * (0.25 + 0.75 * f)
        st.append((x, BODY_B + (TAIL_B - BODY_B) * f,
                   BODY_C + (TAIL_C - BODY_C) * f))
    return st


def duct_stations():
    """(x, half-b, half-c) of the inner duct, mouth -> exit."""
    st = [(0.0, DUCT_B * BELL_GAIN, DUCT_C * BELL_GAIN)]
    for i in range(1, 5):
        f = i / 4.0
        g = 1.0 + (BELL_GAIN - 1.0) * math.cos(0.5 * math.pi * f) ** 2
        st.append((BELL_L * f, DUCT_B * g, DUCT_C * g))
    st.append((TAIL_L, DUCT_B, DUCT_C))
    return st


def loft(verts, faces, rings, inward=False):
    """Append a tube surface between consecutive rings; returns ring index lists."""
    idx = []
    for r in rings:
        base = len(verts)
        verts.extend(r)
        idx.append(list(range(base, base + len(r))))
    for a, b in zip(idx, idx[1:]):
        for i in range(len(r0 := rings[0])):
            j = (i + 1) % len(r0)
            if inward:
                faces.append((a[i], b[i], b[j], a[j]))
            else:
                faces.append((a[i], a[j], b[j], b[i]))
    return idx


def annulus(faces, outer, inner, flip=False):
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        if flip:
            faces.append((outer[i], inner[i], inner[j], outer[j]))
        else:
            faces.append((outer[i], outer[j], inner[j], inner[i]))


def build():
    verts, faces = [], []
    out_rings = [ring(x, b, c) for x, b, c in stations()]
    in_rings = [ring(x, b, c) for x, b, c in duct_stations()]

    out_idx = loft(verts, faces, out_rings)
    in_idx = loft(verts, faces, in_rings, inward=True)

    annulus(faces, out_idx[0], in_idx[0], flip=True)     # mouth
    annulus(faces, out_idx[-1], in_idx[-1])              # exit

    me = bpy.data.meshes.new("magnetide_hull")
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    me.update()

    ob = bpy.data.objects.new("magnetide_hull", me)
    bpy.context.collection.objects.link(ob)
    return ob


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    ob = build()

    stl = os.path.join(OUT, "magnetide_hull.stl")
    blend = os.path.join(OUT, "magnetide_hull.blend")
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    me = ob.data
    print("VERTS %d  FACES %d" % (len(me.vertices), len(me.polygons)))
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    print("BBOX x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f"
          % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))

    # NOTE: vertices are authored in millimetre NUMBERS (205.0 = 205 mm) and STL
    # is unitless with millimetre convention, so do NOT rescale - a 0.001 scale
    # here exports a 0.2 mm hull and the slicer silently shows an invisible part.

    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True,
                              global_scale=1.0)
    else:
        bpy.ops.export_mesh.stl(filepath=stl, use_selection=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("WROTE", stl)
    print("WROTE", blend)


main()
