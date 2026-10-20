"""Bisect the real apertures. A checker that says 'pass' is not a measurement."""
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "magnetide_nacelle.blend"))
halves=[o for o in bpy.data.objects if o.name.startswith("magnetide_housing")]
bvhs=[BVHTree.FromObject(h, bpy.context.evaluated_depsgraph_get()) for h in halves]
def inside(p):
    o=Vector(p); n=0
    for _ in range(64):
        loc,_,_,_=bvhs and _any(bvhs,o)
        if loc is None: break
        n+=1; o=loc+Vector((0,0,1))*1e-4
    return n%2==1
def _any(bvhs,o):
    best=None
    for b in bvhs:
        loc,nor,idx,d=bvhcast(b,o)
        if loc is not None and (best is None or loc.z<best[0].z): best=(loc,)
    return best[0] if best else (None,None,None,None)
def bvhcast(b,o):
    return b.ray_cast(o,Vector((0,0,1)),1e6)
def bisect(f, lo, hi, want):
    """find t where f(t)==want, f monotone increasing"""
    for _ in range(60):
        m=0.5*(lo+hi)
        if f(m) < want: lo=m
        else: hi=m
    return 0.5*(lo+hi)
def mat(x,y,z): return 1 if inside((x,y,z)) else 0
print("duct half-width  (x=60,z=0, from centre out):", round(bisect(lambda t: mat(60,t,0.0),0,20,1),3))
print("duct half-height (x=60,y=0, from centre up):", round(bisect(lambda t: mat(60,0,t),0,20,1),3))
print("slot inner bound (x=60,y=0, up from ceiling):", round(bisect(lambda t: mat(60,0,t),8,40,1),3))
print("groove outer bound (x=61,z=0, outboard from y=10):", round(bisect(lambda t: mat(61,t,0.0),9,30,1),3))
print("screw hole radius (x=15,z=0, from centre at y=46):", round(bisect(lambda t: mat(15,46+t,0.0),0,12,1),3))
print("nut trap radius   (x=15,z=-1.5, from centre):     ", round(bisect(lambda t: mat(15,46+t,-1.5),0,12,1),3))
print("skin wall at x=60 (y=0, up from ceiling):", round(bisect(lambda t: mat(60,0,t),8,40,1),3))
