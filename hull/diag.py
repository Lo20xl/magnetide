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
for p in [(-14,-7.5,-5.5), (-14,7.5,-5.5), (0,30,1), (120,30,1), (0,-30,-1)]:
    print(p, {n: hits(b, p) for n,b in bvhs.items()})
