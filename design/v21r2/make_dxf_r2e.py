"""Laser blank for the v21-r2e steel half: one 2.5 mm sheet, two folds.

Developed width = 56 plate + 2 x (19.958 wall + 5.958 flange) = 107.83 mm.
K = 0.44, inside radius 0.2 -> bend allowance 2.042 mm.
"""
import os

import ezdxf

L = 150.0
T = 2.5
K, R_IN = 0.44, 0.2
BA = (R_IN + K * T) * 3.14159265 / 2.0
WALL_DEV = 22.0 - BA          # 19.958
FLANGE_W = 8.0
FLANGE_DEV = FLANGE_W - BA    # 5.958
W_FLAT = 56.0 + 2 * (WALL_DEV + FLANGE_DEV)
HALF = W_FLAT / 2.0
FOLD_Y = HALF - FLANGE_DEV
HOLE_Y = FOLD_Y + FLANGE_DEV / 2.0
HOLES_X = [30.0, 50.0, 80.0, 100.0]
HOLE_D = 3.4

OUT = r"C:\Users\tangy\Desktop\magnetide-v21r2-assembly\metal"
os.makedirs(OUT, exist_ok=True)
PATH = os.path.join(OUT, "clamshell-flat-2.5mm.dxf")

doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4
msp = doc.modelspace()
doc.layers.add("CUT", color=1)
doc.layers.add("FOLD", color=5, linetype="DASHED")
doc.layers.add("NOTES", color=3)

msp.add_lwpolyline([(0, -HALF), (L, -HALF), (L, HALF), (0, HALF)], close=True,
                   dxfattribs={"layer": "CUT"})
for yy in (HOLE_Y, -HOLE_Y):
    for x in HOLES_X:
        msp.add_circle((x, yy), HOLE_D / 2.0, dxfattribs={"layer": "CUT"})
for yy in (FOLD_Y, -FOLD_Y):
    msp.add_line((0, yy), (L, yy), dxfattribs={"layer": "FOLD"})

notes = [
    "MAGNETIDE v21-r2e CLAMSHELL - 2.5 mm mild steel (DC01 / SPCC / AISI 1008)",
    "Cut 2 off. Blank is symmetrical - fold both edges UP, then mirror one half.",
    "Folds: 90 deg at the two dashed lines, inside radius 0.2 (K=0.44, BA=%.2f)." % BA,
    "8 x %.1f through holes on the flange centreline. Flange is the split-line face." % HOLE_D,
    "Blank %.2f x %.1f mm, %.0f g per half." % (W_FLAT, L, L * W_FLAT * T * 7.85e-3),
]
for i, txt in enumerate(notes):
    msp.add_text(txt, dxfattribs={"layer": "NOTES", "height": 3.2}).set_placement(
        (0, -HALF - 12 - 6 * i))

doc.saveas(PATH)
print("wrote", PATH)
print("blank %.2f x %.1f  fold_y %.2f  hole_y %.2f  BA %.3f" % (W_FLAT, L, FOLD_Y, HOLE_Y, BA))
