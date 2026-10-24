"""Generate the v21-r2i build scripts from the r2h ones.

r2i = 3.0 mm steel, R3 inside on the wall folds, R1.5 on the lug folds
(an 8 mm lug cannot take a 6 mm outside radius). Tray, magnets, electrodes,
bellmouth and rear block are unchanged, so the envelope grows by the shell.

Run:  python gen_r2i.py
"""
import re

src = open("b123d_v21r2h.py", encoding="utf-8").read()

# --- constants -------------------------------------------------------------
subs = [
    ("L = 150.0\nW = 56.0", "L = 150.0\nW = 56.7"),
    ("T = 2.5                  # ONE gauge for the whole steel half",
     "T = 3.0                  # ONE gauge for the whole steel half"),
    ("ZM = 22.0                # outside (half height)",
     "ZM = 22.5                # outside (half height)"),
    ('("steel_uniform_2.5", abs(T - 2.5) < 1e-9)',
     '("steel_uniform_3.0", abs(T - 3.0) < 1e-9)'),
    ('("stack_closes_at_22", abs(ZFL + T_FL + CAV + T_CAP + T - ZM) < 1e-6)',
     '("stack_closes_at_22.5", abs(ZFL + T_FL + CAV + T_CAP + T - ZM) < 1e-6)'),
    ("K, R_IN = 0.44, 0.2", "K, R_IN = 0.44, 3.0"),
    ("Magnetide-v21r2h-assembly", "Magnetide-v21r2i-assembly"),
    ("magnetide-v21r2-assembly", "magnetide-v21r2i-assembly"),
    ("# laser blank for the 2.5 mm folded half",
     "# laser blank for the 3.0 mm folded half (R3 wall folds, R1.5 lug folds)"),
    ('"fold_widths_mm": [round(ZM - BA, 2), round(FLANGE_W - BA, 2)],',
     '"fold_widths_mm": [round(ZM - BA, 2), round(FLANGE_W - BA + 2.02, 2)],'),
]
for a, b in subs:
    assert a in src, a[:50]
    src = src.replace(a, b)

open("b123d_v21r2i.py", "w", encoding="utf-8").write(src)

# --- DXF: two bend radii ---------------------------------------------------
d = open("make_dxf_r2h.py", encoding="utf-8").read()
d = d.replace('"""Laser blank v21-r2h: two lugs per side at x 40 and 110, 20 mm long."""',
              '"""Laser blank v21-r2i: 3.0 mm steel, R3 wall folds, R1.5 lug folds."""')
d = re.sub(r"L, T = 150\.0, 2\.5", "L, T = 150.0, 3.0", d)
d = re.sub(r"PLATE_HALF = 28\.0", "PLATE_HALF = 28.35", d)
d = re.sub(r"WALL_DEV = 19\.958", "WALL_DEV = 15.714", d)
d = re.sub(r"FLANGE_DEV = 5\.958", "FLANGE_DEV = 3.570", d)
d = d.replace('magnetide-v21r2-assembly', 'magnetide-v21r2i-assembly')
d = d.replace('clamshell-flat-2.5mm.dxf', 'clamshell-flat-3.0mm.dxf')
d = d.replace('MAGNETIDE v21-r2h YOKE - 2.5 mm mild steel',
              'MAGNETIDE v21-r2i YOKE - 3.0 mm mild steel')
d = d.replace('"FOLD 1 at y=+-28: wall down 90 deg along the full length.",',
              '"FOLD 1 at y=+-28.35: wall down 90 deg, R3 inside, full length.",')
d = d.replace('"FOLD 2 at y=+-47.96: lug flange OUT 90 deg, 2 lugs per side, 24 mm long.",',
              '"FOLD 2 at y=+-44.06: lug flange OUT 90 deg, R1.5, 2 lugs, 24 mm long.",')
open("make_dxf_r2i.py", "w", encoding="utf-8").write(d)
print("wrote b123d_v21r2i.py and make_dxf_r2i.py")
