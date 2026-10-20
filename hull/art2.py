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
ys=[-13,-11,-9,-7,-5,-3,-1,1,3,5,7,9,11,13]
for x in (-1.05,-1.0,-0.95):
    print("x=%6.2f  y=%s" % (x, " ".join("%+d"%y for y in ys)))
    for z in (5,3,1,0,-3,-5):
        print("        z=%+d  %s" % (z, " ".join(" #" [ins((x,y,z))] for y in ys)))
