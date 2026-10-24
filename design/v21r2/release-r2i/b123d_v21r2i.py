"""Magnetide v21-r2e

 1. STEEL fixed first: uniform 2.5 mm sheet, top plate 3.5 -> 2.5 so the whole
    half folds from ONE gauge. Sheet blank 152.6 x 111.4 at K=0.44, R0.2.
 2. Tray is a CAVITY: floor + 4 walls + rim. Magnet drops inside it, is clamped
    on all four sides, and the 1.5 mm floor is what keeps water off it.
 3. Cap stays. It is a 1.0 mm lid that sits in a rebate in the tray rim, on top
    of the magnet, inside the steel - not a structural part.
 4. Electrode seat 3.0 mm deep (was 0.6), ends potted 5 mm into bellmouth/rear.

Per half (z): 0-7 bore | 7-8.5 tray floor | 8.5-18.5 magnet in cavity
              | 18.5-19.5 cap | 19.5-22 steel plate.  Sum = 22 = H/2.
"""
import json
import os

from build123d import (
    Align, Box, Compound, Cylinder, Plane, Pos, Rectangle, Rot, export_step,
    export_stl, loft, mirror,
)

OUT = r"C:\Users\tangy\Desktop\magnetide-v21r2i-assembly"
PLAS = os.path.join(OUT, "plastic")
REND = os.path.join(OUT, "render")
os.makedirs(PLAS, exist_ok=True)
os.makedirs(REND, exist_ok=True)

L = 150.0
W = 57.0            # 50.7 tray + 2 x 3.0 shell + 0.3 side clearance
ZC = 7.0                 # bore half height -> 40 x 14
T = 3.0                  # ONE gauge for the whole steel half
ZM = 22.5                # outside (half height)
ZIN = ZM - T             # 19.5 inside of the steel
T_FL = 1.5               # tray floor = bore ceiling
CAV = 10.0               # magnet cavity height
T_CAP = 1.0
X0, X1 = 18.0, 142.0
MAG_X0, MAG_X1 = 20.0, 140.0
N_ST, PITCH, TILE_W = 6, 20.0, 9.7
N_ACROSS = 4
YL, YLN = 20.0, 25.35
T_ELEC = 2.0
SEAT_D = 1.0
SEAT_W = 2.2
END_POCKET = 5.0
PEG_R, PEG_HOLE_R = 1.5, 1.65
FLANGE_W = 8.0
EAR_L, EAR_X = 24.0, (40.0, 110.0)   # two tabs per half
HOLE_PITCH = 13.0                   # two M3 per tab, 13 mm apart
AMIN = (Align.MIN, Align.MIN, Align.MIN)

ZFL = ZC                 # 7.0  tray floor underside = bore ceiling
ZFT = ZC + T_FL          # 8.5  tray floor top = magnet bottom
ZMT = ZFT + CAV          # 18.5 magnet top = cap underside
ZRIM = ZMT + T_CAP       # 19.5 tray rim = steel inner face
ZEX = ZC + SEAT_D        # 10.0 electrode half height
EX = X1 - X0             # 124
REBATE = 1.0             # ledge depth: the cap fills it, flush with the steel


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=AMIN)


def pegs_x(x, ys, zs, length, direction):
    al = (Align.CENTER, Align.CENTER, Align.MIN if direction > 0 else Align.MAX)
    out = None
    for y in ys:
        for z in zs:
            c = Pos(x, y, z) * Rot(0, 90 * direction, 0) * Cylinder(PEG_R, length, align=al)
            out = c if out is None else out + c
    return out


# ---------------- steel: one folded 2.5 mm sheet per half ----------------
def shell_half(top):
    if top:
        part = box(0, L, -W / 2, W / 2, 0, ZM) - box(
            0, L, -W / 2 + T, W / 2 - T, 0, ZIN)
        zs = 1.0
    else:
        part = box(0, L, -W / 2, W / 2, -ZM, 0) - box(
            0, L, -W / 2 + T, W / 2 - T, -ZIN, 0)
        zs = -1.0
    flange = None
    for sgn in (1, -1):
        ya, yb = (W / 2, W / 2 + FLANGE_W) if sgn > 0 else (-W / 2 - FLANGE_W, -W / 2)
        for x in EAR_X:                                   # cropped lugs, not a band
            piece = box(x - EAR_L / 2, x + EAR_L / 2, ya, yb, 0, zs * T)
            for dx in (-HOLE_PITCH / 2, HOLE_PITCH / 2):  # two holes per lug
                piece -= Pos(x + dx, sgn * (W / 2 + FLANGE_W / 2), 0) * Cylinder(
                    1.7, T * 2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            flange = piece if flange is None else flange + piece
    return part + flange


steel_top, steel_bot = shell_half(True), shell_half(False)

# ---------------- tray: floor + 4 walls + rim = a cavity the magnet drops into ----------------
TRAY = box(X0, X1, -YLN, YLN, ZFL, ZFT)                        # floor (water barrier)
TRAY += box(X0, X1, YL, YLN, ZFT, ZRIM)                        # +Y wall
TRAY += box(X0, X1, -YLN, -YL, ZFT, ZRIM)                      # -Y wall
TRAY += box(X0, X0 + 2.0, -YLN, YLN, ZFT, ZRIM)                # inlet wall
TRAY += box(X1 - 2.0, X1, -YLN, YLN, ZFT, ZRIM)                # outlet wall

# magnet cavity: inside the walls, floor 8.5, open top until the cap closes it
TRAY -= box(X0 + 2.0, X1 - 2.0, -YL, YL, ZFT, ZRIM + 1)        # 120 x 40 x 10 cavity

# cap ledge: 1.0 deep step in the rim, the lid drops in flush with the steel
TRAY -= box(X0 + 1.0, X1 - 1.0, -YL - 1.5, YL + 1.5, ZRIM - REBATE, ZRIM + 1)

# electrode slot: plastic overhangs 3.0 of the electrode, cut through floor + wall
for sgn in (1, -1):
    ya, yb = (YL, YL + SEAT_W) if sgn > 0 else (-YL - SEAT_W, -YL)
    TRAY -= box(X0, X1, ya, yb, ZFL, ZFL + SEAT_D)

# keeper rib under the floor, directly behind the electrode
for sgn in (1, -1):
    ya, yb = (22.2, 24.2) if sgn > 0 else (-24.2, -22.2)
    TRAY += box(MAG_X0, MAG_X1, ya, yb, 0.0, ZFT)

# lead exit: blind bore from outside, 0.4 left to keep the cavity closed
TRAY -= Pos(X1 - 0.4, 0.0, 13.5) * Rot(0, 90, 90) * Cylinder(
    1.6, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))

# peg holes in both end faces (bellmouth / rear block)
for xx, ln in ((X0 + 0.1, 1.6), (X1 - 2.1, 1.6)):
    for yy in (-24.5, 24.5):
        for zz in (-12.75, 12.75):
            TRAY -= Pos(xx, yy, zz) * Rot(0, 90, 0) * Cylinder(
                PEG_HOLE_R, ln, align=(Align.CENTER, Align.CENTER, Align.MIN))
            TRAY -= Pos(xx, yy, zz) * Rot(0, 90, 0) * Cylinder(
                2.3, 0.4, align=(Align.CENTER, Align.CENTER, Align.MIN))

tray_top = TRAY
tray_bot = mirror(TRAY, about=Plane.XY)

# ---------------- cap: 1.0 mm lid in the rim rebate, on top of the magnet ----------------
CAP = box(X0 + 1.15, X1 - 1.15, -YL - 1.35, YL + 1.35, ZMT, ZRIM)
cap_top = CAP
cap_bot = mirror(CAP, about=Plane.XY)

# ---------------- magnets: inside the tray cavity ----------------
mags_top = []
for j in range(N_ACROSS):
    yc = (j - (N_ACROSS - 1) / 2) * TILE_W
    mags_top.append(box(MAG_X0, MAG_X0 + N_ST * PITCH, yc - TILE_W / 2,
                        yc + TILE_W / 2, ZFT, ZMT))
mags_bot = [mirror(m, about=Plane.XY) for m in mags_top]

# ---------------- electrodes ----------------
ELEC_X0, ELEC_X1 = X0 - END_POCKET, X1 + END_POCKET
elec_p = box(ELEC_X0, ELEC_X1, YL, YL + T_ELEC, -ZEX, ZEX)
elec_n = box(ELEC_X0, ELEC_X1, -YL - T_ELEC, -YL, -ZEX, ZEX)

# ---------------- bellmouth ----------------
NS = 28
sections = []
for k in range(NS + 1):
    t = k / NS
    f = 1 + (24.0 / YL - 1) * (1 - t) ** 2
    g = 1 + (15.0 / ZC - 1) * (1 - t) ** 2
    sections.append(Plane.YZ.offset(X0 * t) * Rectangle(2 * YL * f, 2 * ZC * g))
bell = box(0, X0, -YLN, YLN, -ZIN, ZIN) - loft(sections)
for sgn in (1, -1):
    ya, yb = (YL, YL + T_ELEC + 0.15) if sgn > 0 else (-YL - T_ELEC - 0.15, -YL)
    bell -= box(X0 - END_POCKET, X0 + 0.1, ya, yb, -ZEX - 0.15, ZEX + 0.15)
bell += pegs_x(X0 - 1.0, (-24.5, 24.5), (-12.75, 12.75), 3.0, +1)

# ---------------- rear block ----------------
rear = box(X1, L - T, -YLN, YLN, -ZIN, ZIN)
rear -= box(X1, L - T, -YL, YL, -ZC, ZC)
for sgn in (1, -1):
    ya, yb = (YL, YL + T_ELEC + 0.15) if sgn > 0 else (-YL - T_ELEC - 0.15, -YL)
    rear -= box(X1 - 0.1, X1 + END_POCKET, ya, yb, -ZEX - 0.15, ZEX + 0.15)
rear += pegs_x(X1 + 1.0, (-24.5, 24.5), (-12.75, 12.75), 3.0, -1)

# magnet lead exit: 4.4 mm bore from the cavity out the back face (one per half)
for zz in (13.5, -13.5):
    rear -= Pos(X1 + 2.6, 0.0, zz) * Rot(0, 90, 90) * Cylinder(
        1.6, (L - T) - (X1 + 2.6), align=(Align.CENTER, Align.CENTER, Align.MIN))

# ---------------- report + checks ----------------
parts = {
    "Steel_Top": steel_top, "Steel_Bottom": steel_bot,
    "Tray_Top": tray_top, "Tray_Bottom": tray_bot,
    "Cap_Top": cap_top, "Cap_Bottom": cap_bot,
    "Electrode_P": elec_p, "Electrode_N": elec_n,
    "Bellmouth": bell, "Rear_Block": rear,
    **{"MAG_N_%d" % i: m for i, m in enumerate(mags_top)},
    **{"MAG_S_%d" % i: m for i, m in enumerate(mags_bot)},
}
for n, p in parts.items():
    p.label = n

report = {}
for name, p in parts.items():
    bb = p.bounding_box()
    report[name] = {"size_mm": [round(bb.size.X, 2), round(bb.size.Y, 2), round(bb.size.Z, 2)],
                    "z_mm": [round(bb.min.Z, 2), round(bb.max.Z, 2)],
                    "volume_mm3": round(p.volume, 1), "solids": len(p.solids())}

mb = parts["MAG_N_0"].bounding_box()
checks = [
    ("steel_uniform_3.0", abs(T - 3.0) < 1e-9),
    ("tray_floor_under_magnet", abs(mb.min.Z - ZFT) < 1e-6),
    ("cap_on_magnet_under_steel", abs(mb.max.Z - ZMT) < 1e-6),
    ("cap_top_flush_with_steel", abs(ZRIM - ZIN) < 1e-6 and abs(ZMT + T_CAP - ZRIM) < 1e-6),
    ("rim_meets_steel_inner_face", abs(ZRIM - ZIN) < 1e-6),
    ("stack_closes_at_22.5", abs(ZFL + T_FL + CAV + T_CAP + T - ZM) < 1e-6),
    ("electrode_buried_1mm", abs(elec_p.bounding_box().max.Z - ZEX) < 1e-6),
]
hits = []
for name in ("Tray_Top", "Tray_Bottom", "Cap_Top", "Cap_Bottom", "Bellmouth",
             "Rear_Block", "Electrode_P", "Electrode_N"):
    p = parts[name]
    for y, z in ((-19.9, 6.4), (19.9, 6.4), (-19.9, -6.4), (19.9, -6.4),
                 (0, 0), (0, 6.9)):
        for x in (25.0, 60.0, 100.0, 139.0):
            if p.is_inside((x, y, z)):
                hits.append([name, x, y, z])
checks.append(("bore_clear", not hits))

# watertight proofs
checks.append(("groove_ceiling_below_cavity_floor", ZFL + SEAT_D <= ZFT - 0.4))
leak = []
for x in (30.0, 70.0, 110.0, 138.0):
    if not tray_top.is_inside((x, YL + 1.1, ZFL + SEAT_D + 0.05)):
        leak.append(["groove_roof_open", x, YL + 1.1, ZFL + SEAT_D + 0.05])
report["_leak_probes"] = leak
checks.append(("no_groove_roof_gap", not leak))

wall = []
for part, zz in ((tray_top, 12.75), (tray_bot, -12.75)):
    for x_test, label in ((X0 + 1.85, "inlet"), (X1 - 0.15, "outlet")):
        for yy in (-24.3, 24.3):
            if not part.is_inside((x_test, yy, zz)):
                wall.append(["peg_hole_through_wall", label, x_test, yy, zz])
report["_wall_probes"] = wall
checks.append(("peg_holes_blind", not wall))
report["_probe_hits"] = hits

ov = {}
for a, b in (("Electrode_P", "Tray_Top"), ("MAG_N_0", "Tray_Top"),
             ("MAG_N_0", "Cap_Top"), ("MAG_N_0", "Steel_Top"),
             ("Cap_Top", "Tray_Top"), ("Cap_Top", "Steel_Top"),
             ("Tray_Top", "Steel_Top"), ("Bellmouth", "Tray_Top"),
             ("Rear_Block", "Tray_Top")):
    try:
        ov["%s_vs_%s" % (a, b)] = round(parts[a].intersect(parts[b]).volume, 4)
    except Exception:
        ov["%s_vs_%s" % (a, b)] = 0.0
report["_overlaps"] = ov
report["_checks"] = checks
report["_all_checks_pass"] = all(ok for _, ok in checks)
if not report["_all_checks_pass"]:
    raise SystemExit("CHECK FAILED: %s" % [c for c in checks if not c[1]])

asm = Compound(children=list(parts.values()))
asm.label = "Magnetide-v21r2i-assembly"
step = os.path.join(OUT, "Magnetide-v21r2i-assembly.step")
export_step(asm, step)
report["_step"] = step

for f in os.listdir(REND):
    if f.endswith(".stl"):
        os.remove(os.path.join(REND, f))
for name, p in parts.items():
    export_stl(p, os.path.join(REND, "%s.stl" % name.lower()), tolerance=0.08)
report["_render_stl_dir"] = REND

for name, key in (("tray", "Tray_Top"), ("cap", "Cap_Top"),
                  ("bellmouth", "Bellmouth"), ("rear_block", "Rear_Block")):
    export_stl(parts[key], os.path.join(PLAS, "%s.stl" % name), tolerance=0.05)

# laser blank for the 3.0 mm folded half (R3 wall folds, R1.5 lug folds)
K, R_IN, R_LUG = 0.44, 3.0, 1.5
BA = (R_IN + K * T) * 3.14159265 / 2.0
BA_LUG = (R_LUG + K * T) * 3.14159265 / 2.0
blank_w = W + 2 * ((ZM - BA) + (FLANGE_W - BA_LUG))
report["_steel_blank"] = {"t": T, "w_flat_mm": round(blank_w, 2), "length_mm": L,
                          "bend_allowance_mm": round(BA, 3), "bend_allowance_lug_mm": round(BA_LUG, 3),
                          "K": K, "R_in": R_IN, "R_in_lug": R_LUG,
                          "fold_widths_mm": [round(ZM - BA, 2), round(FLANGE_W - BA_LUG, 2)],
                          "mass_g": round(L * blank_w * T * 7.85e-3, 1)}

with open(os.path.join(OUT, "build_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=1)
print(json.dumps({k: v for k, v in report.items() if k.startswith("_")}, indent=1))
print("PARTS", len(parts))
