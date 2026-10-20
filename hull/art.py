import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "magnetide_nacelle.blend"))
hs=[o for o in bpy.data.objects if o.name.startswith("magnetide_housing")]
bs=[BVHTree.FromObject(h, bpy.context.evaluated_depsgraph_get()) for h in hs]
U=Vector((0,0,1))
def ins(p):
    for b in bs:
        o=Vector(p); n=0
        for _ in range(64):
            l,_,_,_=b.ray_cast(o,U,1e6)
            if l is None: break
            n+=1; o=l+U*1e-4
        if n%2: return True
    return False
for x in (-1.5,-1.2,-1.05,-1.0,-0.95,-0.5,0.0,1.0):
    print("x=%7.2f  material at (y=0,z=0): %s   (y=0,z=4): %s" % (x, ins((x,0,0)), ins((x,0,4))))
