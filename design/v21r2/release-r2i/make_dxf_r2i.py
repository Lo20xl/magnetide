"""Laser blank v21-r2i: 3.0 mm steel, R3 wall folds, R1.5 lug folds."""
import os

import ezdxf

L, T = 150.0, 3.0
PLATE_HALF = 28.5
WALL_DEV = 15.714
FLANGE_DEV = 3.570
HALF = PLATE_HALF + WALL_DEV + FLANGE_DEV      # 53.916
FOLD_OUT = PLATE_HALF + WALL_DEV               # 47.958
HOLE_Y = FOLD_OUT + FLANGE_DEV / 2.0           # 50.937
EAR_L, EAR_X = 24.0, (40.0, 110.0)
HOLE_PITCH = 13.0
bounds = sorted({0.0, L} | {e - EAR_L / 2 for e in EAR_X} | {e + EAR_L / 2 for e in EAR_X})


def is_ear(x0, x1):
    mid = (x0 + x1) / 2.0
    return any(abs(mid - e) <= EAR_L / 2 for e in EAR_X)


def bottom_edge():
    pts = [(0.0, -FOLD_OUT)]
    for x0, x1 in zip(bounds, bounds[1:]):
        y = -HALF if is_ear(x0, x1) else -FOLD_OUT
        if abs(y - pts[-1][1]) > 1e-9:
            pts.append((x0, y))
        pts.append((x1, y))
    return pts


poly = bottom_edge() + [(x, -y) for (x, y) in reversed(bottom_edge())]
clean = [poly[0]]
for p in poly[1:]:
    if abs(p[0] - clean[-1][0]) > 1e-9 or abs(p[1] - clean[-1][1]) > 1e-9:
        clean.append(p)

OUT = r"C:\Users\tangy\Desktop\magnetide-v21r2i-assembly\metal"
os.makedirs(OUT, exist_ok=True)
PATH = os.path.join(OUT, "clamshell-flat-3.0mm.dxf")

doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4
msp = doc.modelspace()
for name, col, lt in (("CUT", 1, "CONTINUOUS"), ("FOLD", 5, "DASHED"), ("NOTES", 3, "CONTINUOUS")):
    doc.layers.add(name, color=col, linetype=lt)

msp.add_lwpolyline(clean, close=True, dxfattribs={"layer": "CUT"})
for x in EAR_X:
    for dx in (-HOLE_PITCH / 2, HOLE_PITCH / 2):
        for yy in (HOLE_Y, -HOLE_Y):
            msp.add_circle((x + dx, yy), 1.7, dxfattribs={"layer": "CUT"})
for yy in (PLATE_HALF, -PLATE_HALF, FOLD_OUT, -FOLD_OUT):
    msp.add_line((0, yy), (L, yy), dxfattribs={"layer": "FOLD"})

notes = [
    "MAGNETIDE v21-r2i YOKE - 3.0 mm mild steel (DC01 / SPCC / AISI 1008)",
    "Cut 2, mirror one. FOLD 1 at y=+-28: wall down 90 deg along the full length.",
    "FOLD 2 at y=+-44.06: lug flange OUT 90 deg, R1.5, 2 lugs, 24 mm long.",
    "Inside radius 0.2, K = 0.44, BA 2.04. 8 x 3.4 holes per half, 2 per lug.",
    "Blank %.2f x %.0f mm, %.0f g per half." % (2 * HALF, L, L * 2 * HALF * T * 7.85e-3),
]
for i, txt in enumerate(notes):
    msp.add_text(txt, dxfattribs={"layer": "NOTES", "height": 3.0}).set_placement(
        (0, -HALF - 12 - 6 * i))

doc.saveas(PATH)
print("wrote", PATH)
print("blank %.2f x %.0f | lugs at %s | holes +-%.2f" % (2 * HALF, L, EAR_X, HOLE_Y))
