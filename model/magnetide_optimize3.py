"""Magnetide optimiser v3 - built to the ACTUAL tray cavity.

v1/v2 assumed O20x5 discs at Rp12,000. The v19 print guide specifies the tray
cavity takes a 20x10x5 mm tile (PRINT_v19.md: "check cavity with one real
tile (20x10x5)"), and that tile is Rp6,325 on Tokopedia - half the disc price
for a face that tiles a rectangular tray. So cost per unit of pole face is the
thing to compare and the block wins outright.

Geometry model
  pole face per station = 20 mm axial x 20 mm across (2 tiles of 10 mm, which
  covers the 16 mm channel width with 4 mm overlap per side)
  stack thickness = k * 5 mm, k integer (tiles stacked, no machining)
  tiles per station = 4 (2 across x 2 sides) per 5 mm of stack

Run: python magnetide_optimize3.py [price_per_tile] [budget_idr]
"""
import math
import sys

BR = 1.45
SIGMA = 5.0
RHO = 1025.0
E_CHEM = 2.57
K_YOKE = 0.90
H_MM, W_MM = 12.0, 16.0
TILE_L, TILE_W, TILE_T = 20.0, 10.0, 5.0
V_DERATE = 0.80
DH_MM = 4 * W_MM * H_MM / (2 * (W_MM + H_MM))     # 13.71 mm

WALLS = (4.0, 2.5, 1.5)
KS = (1, 2, 3, 4, 5, 6, 7, 8)        # tiles stacked per side -> lm = 5k mm
CURRENTS = (1.15, 1.55, 2.0, 2.5, 3.0)
N_ACROSS = math.ceil(W_MM / TILE_W)   # 2

PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 6325.0
BUDGET = float(sys.argv[2]) if len(sys.argv) > 2 else 700000.0


def gap_field(l_m, g):
    return K_YOKE * 2 * BR * l_m / (2 * l_m + 1.05 * g)


def evaluate(wall, n_st, k, I):
    h, w = H_MM / 1e3, W_MM / 1e3
    L = n_st * TILE_L / 1e3
    g = (H_MM + 2 * wall) / 1e3
    l_m = k * TILE_T / 1e3
    B = gap_field(l_m, g)
    n_tile = 2 * n_st * N_ACROSS * k
    j = I / (h * L)
    R_ch = w / (SIGMA * h * L)
    V_el = E_CHEM + I * R_ch
    P = V_el * I
    v = math.sqrt(j * B * L / RHO) * V_DERATE
    Q = v * w * h * 1e6
    return dict(wall=wall, n_st=n_st, L=L * 1e3, k=k, lm=l_m * 1e3, I=I,
                g=g * 1e3, B=B * 1e3, j=j, R_ch=R_ch, V=V_el, P=P,
                v=v * 1e2, Q=Q, flowW=Q / P, n=n_tile, cost=n_tile * PRICE)


def table(rows, title, key='flowW', n=12):
    print("\n" + title + "\n" + "-" * len(title))
    print("%4s %3s %5s %4s %5s %6s %6s %6s %7s %7s %6s %8s" %
          ("wall", "stn", "L", "k", "I", "g", "B mT", "v cm/s", "Q ml/s",
           "ml/s/W", "tiles", "Rp"))
    for r in sorted(rows, key=lambda r: -r[key])[:n]:
        print("%4.1f %3d %5.0f %4d %5.2f %6.1f %6.0f %6.2f %7.2f %7.3f %6d %8.0f" %
              (r['wall'], r['n_st'], r['L'], r['k'], r['I'], r['g'], r['B'],
               r['v'], r['Q'], r['flowW'], r['n'], r['cost']))


def main():
    phys = [evaluate(*p) for p in
            ((a, b, c, d) for a in WALLS for b in (2, 3, 4, 5, 6)
             for c in KS for d in CURRENTS)]
    build = [r for r in phys if r['L'] / DH_MM >= 3]
    aff = [r for r in build if r['cost'] <= BUDGET]
    print("tile Rp%.0f (20x10x5 N52), budget Rp%.0f  -> max %d tiles"
          % (PRICE, BUDGET, int(BUDGET // PRICE)))
    print("tried %d | buildable %d | affordable %d" % (len(phys), len(build), len(aff)))

    table(aff, "A. AFFORDABLE: ranked on FLOW-PER-WATT", 'flowW')
    table(aff, "B. AFFORDABLE: ranked on RAW FLOW", 'Q')

    print("\nC. SPEND LADDER (best Q/W at each tile count)\n" + "-" * 46)
    print("%6s %8s %5s %4s %5s %6s %7s %7s" %
          ("tiles", "Rp", "L", "k", "I", "B mT", "Q ml/s", "ml/s/W"))
    for n in sorted({r['n'] for r in build}):
        cand = [r for r in build if r['n'] == n]
        b = max(cand, key=lambda r: r['flowW'])
        print("%6d %8.0f %5.0f %4d %5.2f %6.0f %7.2f %7.3f  %s" %
              (n, b['cost'], b['L'], b['k'], b['I'], b['B'], b['Q'], b['flowW'],
               "" if b['cost'] <= BUDGET else "over"))

    print("\nD. COVERAGE COST at the cheapest useful stack (k=1) and I=1.55 A")
    print("-" * 62)
    for st in (2, 3, 4, 6):
        r = evaluate(4.0, st, 1, 1.55)
        print("  %d stations (L=%3.0f mm): B=%.0f mT  v=%.2f cm/s  Q=%5.2f ml/s"
              "  Q/W=%.2f  tiles=%2d  Rp%.0f"
              % (st, r['L'], r['B'], r['v'], r['Q'], r['flowW'], r['n'], r['cost']))

    bestQ = max(aff, key=lambda r: r['Q'])
    bestW = max(aff, key=lambda r: r['flowW'])
    print("\nMAX FLOW (affordable): %d st x k=%d, I=%.2f A -> B=%.0f mT, Q=%.1f ml/s,"
          " %.1f W, %d tiles, Rp%.0f"
          % (bestQ['n_st'], bestQ['k'], bestQ['I'], bestQ['B'], bestQ['Q'],
             bestQ['P'], bestQ['n'], bestQ['cost']))
    print("MAX Q/W (affordable):  %d st x k=%d, I=%.2f A -> B=%.0f mT, Q=%.1f ml/s,"
          " %.1f W, %d tiles, Rp%.0f"
          % (bestW['n_st'], bestW['k'], bestW['I'], bestW['B'], bestW['Q'],
             bestW['P'], bestW['n'], bestW['cost']))
    print("\nCurrent v19 build (4 tiles, 20x10x5, 2 stations? see note):")
    r = evaluate(4.0, 2, 1, 1.55)
    print("  2 stations k=1: B=%.0f mT v=%.2f cm/s Q=%.2f ml/s Q/W=%.2f"
          % (r['B'], r['v'], r['Q'], r['flowW']))


if __name__ == "__main__":
    main()
