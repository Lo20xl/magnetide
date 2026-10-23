"""Render Magnetide v21-r2: exploded view or half-section. Blender 4.5, Cycles CPU.

usage: blender -b -P av_render2.py -- <stl_dir> <out_png> <explode|section>
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
STL_DIR, OUT_PNG, MODE = argv[0], argv[1], argv[2]

OFF = {
    "steel_top": (0, 0, 152), "cap_top": (0, 0, 136), "tray_top": (0, 0, 78),
    "steel_bottom": (0, 0, -152), "cap_bottom": (0, 0, -136), "tray_bottom": (0, 0, -78),
    "bellmouth": (-110, 0, 0), "rear_block": (110, 0, 0),
    "electrode_p": (0, 58, 0), "electrode_n": (0, -58, 0),
}
for i in range(4):  # 4 rows x 6 tiles, exploded above the tray cavity
    OFF["mag_n_%d" % i] = (0, 0, 118)
    OFF["mag_s_%d" % i] = (0, 0, -118)

C = {
    "tray_top": (0.86, 0.36, 0.06), "tray_bottom": (0.86, 0.36, 0.06),
    "cap_top": (0.94, 0.55, 0.12), "cap_bottom": (0.94, 0.55, 0.12),
    "bellmouth": (0.84, 0.33, 0.05), "rear_block": (0.84, 0.33, 0.05),
    "electrode_p": (0.05, 0.05, 0.055), "electrode_n": (0.05, 0.05, 0.055),
    "steel_top": (0.55, 0.57, 0.61), "steel_bottom": (0.55, 0.57, 0.61),
}


def col(k):
    if k in C:
        return C[k]
    if k.startswith("mag_n"):
        return (0.62, 0.07, 0.06)
    if k.startswith("mag_s"):
        return (0.06, 0.16, 0.55)
    return (0.7, 0.7, 0.7)


bpy.ops.wm.read_factory_settings(use_empty=True)
objs = []
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
    b.inputs["Roughness"].default_value = 0.5
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
    if MODE == "explode":
        dx, dy, dz = OFF.get(k, (0, 0, 0))
        ob.location = Vector((dx, dy, dz))
    objs.append(ob)

pts = [ob.matrix_world @ Vector(c) for ob in objs for c in ob.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2
size = (hi - lo).length

if MODE == "explode":
    d = Vector((-0.92, 0.78, 0.55))
else:
    d = Vector((-0.98, 0.55, 0.30))
d = d.normalized()

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)

sc = bpy.context.scene
sc.render.resolution_x = 2400
sc.render.resolution_y = 1500
aspect = sc.render.resolution_x / sc.render.resolution_y

right = d.cross(Vector((0, 0, 1))).normalized()
up = right.cross(d).normalized()
hw = max(abs((p - ctr).dot(right)) for p in pts)
hh = max(abs((p - ctr).dot(up)) for p in pts)
cam_data.ortho_scale = max(2 * hw, 2 * hh * aspect) * 1.16
cam_data.clip_start = 1.0
cam_data.clip_end = size * 20
cam.location = ctr + d * size * 3.0
cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 1.1
sun.data.angle = math.radians(26)
sun.rotation_euler = (math.radians(52), math.radians(6), math.radians(30))
bpy.context.collection.objects.link(sun)

for i, (off, e) in enumerate([((0.7, 0.8, 0.6), 70), ((-0.8, 0.4, 0.1), 40)]):
    a = bpy.data.objects.new("fill%d" % i, bpy.data.lights.new("fill%d" % i, "AREA"))
    a.data.energy = e
    a.data.size = size * 2
    a.location = ctr + Vector(off) * size * 1.6
    a.rotation_euler = (ctr - a.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(a)

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
sc.render.filepath = OUT_PNG
bpy.ops.render.render(write_still=True)
print("RENDERED", OUT_PNG, MODE, flush=True)
