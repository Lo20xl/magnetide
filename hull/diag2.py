import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "magnetide_nacelle.blend"))
halves=[o for o in bpy.data.objects if o.name.startswith("magnetide_housing")]
bvhs={h.name: BVHTree.FromObject(h, bpy.context.evaluated_depsgraph_get()) for h in halves}
def hits(bvh,p):
    o=Vector(p); zs=[]
    for _ in range(40):
        loc,_,_,_=bvh.ray_cast(o,Vector((0,0,1)),1e6)
        if loc is None: break
        zs.append(round(loc.z,3)); o=loc+Vector((0,0,1))*1e-4
    return zs
print("x=-14 : material z-crossings by y (both halves)")
for y in (0, -4, -7.5, -7.9, -8.5, -13):
    print("  y=%6.1f  bottom=%-28s top=%s" % (y,
        hits(bvhs['magnetide_housing_bottom'],(-14,y,0.0)),
        hits(bvhs['magnetide_housing_top'],(-14,y,0.0))))
print("x=60 (mid) :")
for y in (0, -7.5, -8.5):
    print("  y=%6.1f  bottom=%-28s top=%s" % (y,
        hits(bvhs['magnetide_housing_bottom'],(60,y,0.0)),
        hits(bvhs['magnetide_housing_top'],(60,y,0.0))))
