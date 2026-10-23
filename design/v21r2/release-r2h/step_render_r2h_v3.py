"""LEGO-style step renders for Magnetide v21-r2h, v3.

Fixes vs v2:
  * magnet bars are spread apart so they read as separate tiles, not one slab
  * insert steps float the part high enough to see the tray cavity under it
  * step 6 uses a side camera so the stack reads as layers closing (not a wall)

usage: blender -b -P step_render_r2h_v3.py -- <stl_dir> <out_dir>
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
STL_DIR, OUT_DIR = argv[0], argv[1]
os.makedirs(OUT_DIR, exist_ok=True)

MAGS_TOP = ["mag_n_0", "mag_n_1", "mag_n_2", "mag_n_3"]
MAGS_BOT = ["mag_s_0", "mag_s_1", "mag_s_2", "mag_s_3"]
SPREAD = 1.22

C = {
    "tray_top": (0.86, 0.36, 0.06), "tray_bottom": (0.86, 0.36, 0.06),
    "cap_top": (0.95, 0.60, 0.14), "cap_bottom": (0.95, 0.60, 0.14),
    "bellmouth": (0.88, 0.40, 0.07), "rear_block": (0.88, 0.40, 0.07),
    "electrode_p": (0.06, 0.06, 0.065), "electrode_n": (0.06, 0.06, 0.065),
    "steel_top": (0.58, 0.60, 0.64), "steel_bottom": (0.58, 0.60, 0.64),
}


def col(k):
    if k in C:
        return C[k]
    if k.startswith("mag_n"):
        return (0.66, 0.09, 0.07)
    if k.startswith("mag_s"):
        return (0.07, 0.18, 0.60)
    return (0.7, 0.7, 0.7)


bpy.ops.wm.read_factory_settings(use_empty=True)
objs = {}
for f in sorted(os.listdir(STL_DIR)):
    if not f.lower().endswith(".stl"):
        continue
    k = f[:-4].lower()
    bpy.ops.wm.stl_import(filepath=os.path.join(STL_DIR, f))
    ob = bpy.context.selected_objects[0]
    ob.name = k
    mat = bpy.data.materials.new(k)
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col(k), 1.0)
    b.inputs["Roughness"].default_value = 0.48
    b.inputs["Metallic"].default_value = 0.7 if k.startswith("steel") else 0.0
    for poly in ob.data.polygons:
        poly.use_smooth = False
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.select_set(False)
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    objs[k] = ob

# magnet bars: spread sideways about the assembly centreline so the four read as tiles
ycen = {}
for m in MAGS_TOP + MAGS_BOT:
    bb = objs[m].bound_box
    ycen[m] = (bb[0][1] + bb[6][1]) / 2.0


def spread(m, dz):
    return (0.0, ycen[m] * (SPREAD - 1.0), dz)


SHOTS = [
    ("01_yoke", ["steel_top", "steel_bottom"],
     {"steel_top": (0, 0, 30), "steel_bottom": (0, 0, -30)}, "hero"),
    ("02_magnets", ["tray_top"] + MAGS_TOP,
     {m: spread(m, 40) for m in MAGS_TOP}, "top"),
    ("03_cap", ["tray_top", "cap_top"] + MAGS_TOP,
     dict({m: spread(m, 0) for m in MAGS_TOP}, cap_top=(0, 0, 22)), "top"),
    ("04_electrode", ["tray_top", "cap_top", "electrode_p"] + MAGS_TOP,
     dict({m: spread(m, 0) for m in MAGS_TOP}, cap_top=(0, 0, 0), electrode_p=(-52, 6, 0)), "top"),
    ("05_ends", ["tray_top", "cap_top", "electrode_p", "bellmouth", "rear_block"] + MAGS_TOP,
     dict({m: spread(m, 0) for m in MAGS_TOP}, cap_top=(0, 0, 0), electrode_p=(0, 0, 0),
          bellmouth=(-30, 0, 14), rear_block=(30, 0, 14)), "top"),
    ("06_close", ["steel_bottom", "steel_top", "tray_top", "tray_bottom",
                  "cap_top", "cap_bottom", "electrode_p", "bellmouth", "rear_block"]
     + MAGS_TOP + MAGS_BOT,
     dict({m: spread(m, -100) for m in MAGS_BOT},
          steel_bottom=(0, 0, -135), tray_bottom=(0, 0, -100), cap_bottom=(0, 0, -100),
          electrode_p=(0, 0, -55), bellmouth=(0, 0, -55), rear_block=(0, 0, -55),
          **{m: spread(m, 55) for m in MAGS_TOP},
          tray_top=(0, 0, 55), cap_top=(0, 0, 55), steel_top=(0, 0, 115)), "side"),
    ("07_hero", None, {}, "hero"),
]

CAM = {"hero": Vector((-0.92, 0.72, 0.46)), "top": Vector((-0.52, 0.42, 0.95)),
       "side": Vector((-0.30, 0.88, 0.36))}

sc = bpy.context.scene
sc.render.resolution_x = 1600
sc.render.resolution_y = 1100
aspect = sc.render.resolution_x / sc.render.resolution_y

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 1.15
sun.data.angle = math.radians(24)
sun.rotation_euler = (math.radians(50), math.radians(4), math.radians(28))
bpy.context.collection.objects.link(sun)

world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.world = world

sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"

for name, keep, xf, kind in SHOTS:
    for k, ob in objs.items():
        ob.hide_render = not (keep is None or any(k == p or k.startswith(p) for p in keep))
        ob.location = Vector(xf.get(k, (0, 0, 0)))
    bpy.context.view_layer.update()

    D = CAM[kind].normalized()
    vis = [ob for ob in objs.values() if not ob.hide_render]
    pts = [ob.matrix_world @ Vector(c) for ob in vis for c in ob.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (lo + hi) / 2
    size = (hi - lo).length

    right = D.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(D).normalized()
    hw = max(abs((p - ctr).dot(right)) for p in pts)
    hh = max(abs((p - ctr).dot(up)) for p in pts)
    cam_data.ortho_scale = max(2 * hw, 2 * hh * aspect) * 1.18
    cam_data.clip_start = 1.0
    cam_data.clip_end = size * 20
    cam.location = ctr + D * size * 3.0
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()

    for o in list(bpy.data.objects):
        if o.name.startswith("fill"):
            bpy.data.objects.remove(o, do_unlink=True)
    for i, (off, e) in enumerate([((0.7, 0.8, 0.6), 70), ((-0.8, 0.4, 0.1), 40)]):
        a = bpy.data.objects.new("fill%d" % i, bpy.data.lights.new("fill%d" % i, "AREA"))
        a.data.energy = e
        a.data.size = max(size, 120) * 1.6
        a.location = ctr + Vector(off) * max(size, 120) * 1.5
        a.rotation_euler = (ctr - a.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.collection.objects.link(a)

    sc.render.filepath = os.path.join(OUT_DIR, "step_%s.png" % name)
    bpy.ops.render.render(write_still=True)
    print("SHOT", name, len(vis), flush=True)

print("STEPS_DONE", flush=True)
