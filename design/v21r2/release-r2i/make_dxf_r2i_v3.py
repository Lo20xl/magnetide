"""Laser blank v21-r2i — 3.0 mm mild steel, wall folds R3, lug folds R1.5.

Bend development is the standard two-leg form, not a naive outside-dimension sum:

    leg_1 = plate_half - SB_wall
    leg_2 = ZM - SB_wall - SB_lug
    leg_3 = FLANGE_W - SB_lug
    half  = leg_1 + BA_wall + leg_2 + BA_lug + leg_3
    SB    = R + t                      (setback)
    BA    = (R + K t) pi/2             (bend allowance)
    bend line = leg + BA/2             (arc centre, what the brake aligns to)

The r2h-style sum (W + 2*(ZM - BA) + 2*(FL - BA)) happens to be within 0.14 mm for
R0.2, but for R3 it is 3 mm out. An 8 mm lug cannot take a 3.4 hole on 3 mm sheet
(flat flange = 3.5 mm); the lug is 12 mm, leaving a 2.05 mm edge margin.

usage:  python make_dxf_r2i_v3.py [out_dir]
"""
import math
import os
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

L = 150.0
T = 3.0
K = 0.44
R_WALL, R_LUG = 3.0, 1.5
PLATE_HALF = 28.5
ZM = 22.5
FLANGE_W = 12.0
EAR_L, EAR_X = 24.0, (40.0, 110.0)
HOLE_PITCH = 13.0
HOLE_D = 3.4

SB_WALL, SB_LUG = R_WALL + T, R_LUG + T
BA_WALL = (R_WALL + K * T) * math.pi / 2
BA_LUG = (R_LUG + K * T) * math.pi / 2

LEG_PLATE = PLATE_HALF - SB_WALL
LEG_WALL = ZM - SB_WALL - SB_LUG
LEG_LUG = FLANGE_W - SB_LUG
HALF = LEG_PLATE + BA_WALL + LEG_WALL + BA_LUG + LEG_LUG
BLANK_W = 2 * HALF

BEND_LUG = HALF - (LEG_LUG + BA_LUG / 2)                   # from the blank centre line
BEND_WALL = HALF - (LEG_LUG + BA_LUG + LEG_WALL + BA_WALL / 2)
# the hole is at the middle of the folded flange face: FLANGE_W/2 measured
# from the plate face, which lands (FLANGE_W/2 - SB_LUG) into the flat flange leg
HOLE_Y = HALF - (LEG_LUG + (FLANGE_W / 2.0 - SB_LUG))
MASS = L * BLANK_W * T * 7.85e-3

assert (FLANGE_W - SB_LUG) > HOLE_D + 1.6, "no flat flange for the hole"
assert HALF - (HOLE_Y + HOLE_D / 2) > 0.8, "hole breaks out of the edge"

OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\tangy\Desktop\magnetide-v21r2i-assembly\metal"
os.makedirs(OUT, exist_ok=True)
PATH = os.path.join(OUT, "clamshell-flat-3.0mm.dxf")

bounds = sorted({0.0, L} | {e - EAR_L / 2 for e in EAR_X} | {e + EAR_L / 2 for e in EAR_X})


def is_ear(x0, x1):
    return any(abs((x0 + x1) / 2.0 - e) <= EAR_L / 2 for e in EAR_X)


def edge():
    pts = [(0.0, -BEND_LUG)]
    for x0, x1 in zip(bounds, bounds[1:]):
        y = -(HALF if is_ear(x0, x1) else BEND_LUG)
        if abs(y - pts[-1][1]) > 1e-9:
            pts.append((x0, y))
        pts.append((x1, y))
    return pts


bottom = edge()
poly = bottom + [(x, -y) for (x, y) in reversed(bottom)]
clean = [poly[0]]
for p in poly[1:]:
    if abs(p[0] - clean[-1][0]) > 1e-9 or abs(p[1] - clean[-1][1]) > 1e-9:
        clean.append(p)

doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4
doc.header["$MEASUREMENT"] = 1
for name, col, lt in (("CUT", 1, "CONTINUOUS"), ("FOLD", 5, "DASHED"),
                      ("DIMS", 3, "CONTINUOUS"), ("NOTES", 8, "CONTINUOUS"),
                      ("TITLE", 4, "CONTINUOUS")):
    doc.layers.add(name, color=col, linetype=lt)
msp = doc.modelspace()

msp.add_lwpolyline(clean, close=True, dxfattribs={"layer": "CUT"})
for x in EAR_X:
    for dx in (-HOLE_PITCH / 2, HOLE_PITCH / 2):
        for yy in (-HOLE_Y, HOLE_Y):
            msp.add_circle((x + dx, yy), HOLE_D / 2, dxfattribs={"layer": "CUT"})
for yy in (BEND_WALL, -BEND_WALL, BEND_LUG, -BEND_LUG):
    msp.add_line((0, yy), (L, yy), dxfattribs={"layer": "FOLD"})


def tick(x, y, s=1.2):
    msp.add_line((x - s, y - s), (x + s, y + s), dxfattribs={"layer": "DIMS"})


def txt(s, x, y, h=2.6, layer="NOTES", align=TextEntityAlignment.BOTTOM_LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": layer}).set_placement((x, y), align=align)


def hdim(x0, x1, y, label, ext_from=None):
    msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "DIMS"})
    tick(x0, y)
    tick(x1, y)
    if ext_from is not None:
        for x in (x0, x1):
            msp.add_line((x, ext_from), (x, y + 1.0), dxfattribs={"layer": "DIMS"})
    txt(label, (x0 + x1) / 2.0, y + 0.9, layer="DIMS", align=TextEntityAlignment.BOTTOM_CENTER)


# ---- dims ------------------------------------------------------------------
hdim(0.0, L, -HALF - 10.0, "150", ext_from=-HALF)
hdim(EAR_X[0] - HOLE_PITCH / 2, EAR_X[0] + HOLE_PITCH / 2, -HALF - 4.5, "13", ext_from=-HOLE_Y)
hdim(HALF, HOLE_Y, -BEND_LUG - 6.0, "%.2f" % (HALF - HOLE_Y), ext_from=-HOLE_Y)

for yv, lab in ((BEND_LUG, "%.2f" % BEND_LUG), (BEND_WALL, "%.2f" % BEND_WALL)):
    msp.add_line((L + 6.0, -yv), (L + 6.0, yv), dxfattribs={"layer": "DIMS"})
    tick(L + 6.0, -yv)
    tick(L + 6.0, yv)
    txt(lab, L + 7.4, 0.0, layer="DIMS") if yv == BEND_LUG else txt(lab, L + 7.4, 3.6, layer="DIMS")

msp.add_line((-6.0, -HALF), (-6.0, HALF), dxfattribs={"layer": "DIMS"})
tick(-6.0, -HALF)
tick(-6.0, HALF)
t = msp.add_text("%.2f" % BLANK_W, height=2.6, dxfattribs={"layer": "DIMS"})
t.dxf.rotation = 90
t.set_placement((-7.2, 0.0), align=TextEntityAlignment.BOTTOM_CENTER)

# ---- lug dimensions (above the blank) --------------------------------------
VD = lambda x0, y0, y1, label: (
    msp.add_line((x0, y0), (x0, y1), dxfattribs={"layer": "DIMS"}),
    tick(x0, y0), tick(x0, y1),
    txt(label, x0 + 1.0, (y0 + y1) / 2.0, layer="DIMS"))

hdim(0.0, EAR_X[0], BEND_LUG + 14.0, "40", ext_from=BEND_LUG)
hdim(EAR_X[0] - EAR_L / 2, EAR_X[0] + EAR_L / 2, BEND_LUG + 21.0, "24", ext_from=BEND_LUG)
hdim(EAR_X[1], L, BEND_LUG + 14.0, "40", ext_from=BEND_LUG)
hdim(EAR_X[0], EAR_X[1], BEND_LUG + 28.0, "70", ext_from=BEND_LUG)
VD(-9.0, BEND_LUG, HALF, "%.2f" % (HALF - BEND_LUG))

# ---- callouts --------------------------------------------------------------
for x, y, s in [
    (9.0, -HALF - 16.0, "2x  PART     8x  \u00d83.4 THRU  (2 per lug, 13 pitch)"),
    (9.0, -HALF - 22.0, "BEND 1   y = \u00b1%.2f   R%.1f  90\u00b0 DOWN  (dashed = arc centre)" % (BEND_WALL, R_WALL)),
    (9.0, -HALF - 27.0, "BEND 2   y = \u00b1%.2f   R%.1f  90\u00b0 OUT" % (BEND_LUG, R_LUG)),
    (9.0, -HALF - 32.0, "BA %.2f wall / %.2f lug    K %.2f    setback %.1f" % (BA_WALL, BA_LUG, K, SB_WALL)),
    (9.0, -HALF - 37.0, "CHECK AFTER FOLD   22.5 high, 57 wide, lug 12, hole line 6.0 off the plate face"),
]:
    txt(s, x, y)

# ---- title block -----------------------------------------------------------
tb_x0, tb_x1, tb_y1 = 0.0, 136.0, -HALF - 44.0
tb_y0 = tb_y1 - 22.0
msp.add_lwpolyline([(tb_x0, tb_y0), (tb_x1, tb_y0), (tb_x1, tb_y1), (tb_x0, tb_y1)],
                   close=True, dxfattribs={"layer": "TITLE"})
msp.add_line((tb_x0, tb_y1 - 7.0), (tb_x1, tb_y1 - 7.0), dxfattribs={"layer": "TITLE"})
msp.add_line((92.0, tb_y0), (92.0, tb_y1), dxfattribs={"layer": "TITLE"})
txt("MAGNETIDE v21-r2i   YOKE BLANK", tb_x0 + 2.5, tb_y1 - 5.2, 3.6, "TITLE")
txt("3.0 mm mild steel   DC01 / SPCC / AISI 1008", tb_x0 + 2.5, tb_y1 - 13.5, layer="TITLE")
txt("QTY 2   mirror one   all dims mm   grain across bends", tb_x0 + 2.5, tb_y1 - 18.5, layer="TITLE")
txt("BLANK %.2f x %.1f" % (BLANK_W, L), 94.0, tb_y1 - 13.5, layer="TITLE")
txt("MASS %.0f g / half" % MASS, 94.0, tb_y1 - 18.5, layer="TITLE")

doc.saveas(PATH)
print("wrote", PATH)
print("blank %.2f x %.1f | bend centres +/-%.3f (wall) +/-%.3f (lug) | hole line +/-%.3f | edge margin %.2f"
      % (BLANK_W, L, BEND_WALL, BEND_LUG, HOLE_Y, HALF - (HOLE_Y + HOLE_D / 2)))
