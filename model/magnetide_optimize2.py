"""Magnetide final-design optimiser, v2.

v1 failed for two reasons worth remembering:
  * coverage was sized to fit, so it always read 100% - the as-built 2-station
    case (40 mm of face over a 120 mm electrode) was never evaluated;
  * nothing was gated on money, so the "winner" needed 60 discs = Rp720k,
    more than the entire Rp700k project ceiling, on magnets alone.

v2 enumerates only buildable geometries, gates on the magnesia budget, and
reports the (Q, Q/W) Pareto frontier instead of one number, because raw flow
rate and flow-per-watt have no common optimum.

Model
  B(g)      closed-form yoke-assisted pair      skill mhd-seawater-field-solver
  v, Q      momentum form, f*L = rho*v^2        skill mhd-seawater-field-solver
  E_chem    = 2.57 V, R_ch slope                Delannoy, MHD 61 (2025) 55-66
  coupling-length dominance                     Cao, Magnetochemistry 12 (2026) 89
Run:  python magnetide_optimize2.py [price_per_disc] [magnet_budget_idr]
"""
import math
import sys

BR = 1.45          # N52 remanence, T
SIGMA = 5.0        # 5% brine, S/m
RHO = 1025.0
E_CHEM = 2.57      # V, at our current density (inside Delannoy's fit range)
K_YOKE = 0.90      # real mild-steel leakage derate on the ideal formula
H_MM, W_MM = 12.0, 16.0     # channel inner height (pole gap), width (current path)
DISC_D, DISC_T = 20.0, 5.0  # N52 disc, mm
V_DERATE = 0.80    # friction + end effects + field non-uniformity
DH_MM = 4 * W_MM * H_MM / (2 * (W_MM + H_MM))   # hydraulic diameter, 13.7 mm

WALLS = (4.0, 2.5, 1.5)
LMS = (5, 10, 15, 20, 25, 30, 35, 40)     # magnet thickness per side, mm
STATIONS = (2, 3, 4, 5, 6)                # pole positions along the length
CURRENTS = (1.15, 1.55, 2.0, 2.5, 3.0)

PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 12000.0
BUDGET = float(sys.argv[2]) if len(sys.argv) > 2 else 200000.0    # magnet allowance


def gap_field(l_m, g):
    return K_YOKE * 2 * BR * l_m / (2 * l_m + 1.05 * g)


def evaluate(wall, n_st, lm, I):
    h, w = H_MM / 1e3, W_MM / 1e3
    L = n_st * DISC_D / 1e3                      # active length matches coverage
    g = (H_MM + 2 * wall) / 1e3
    l_m = lm / 1e3
    B = gap_field(l_m, g)
    n_disc = 2 * n_st * int(lm / DISC_T)
    j = I / (h * L)
    R_ch = w / (SIGMA * h * L)
    V_el = E_CHEM + I * R_ch
    P = V_el * I
    v = math.sqrt(j * B * L / RHO) * V_DERATE
    Q = v * w * h * 1e6                          # ml/s
    return dict(wall=wall, n_st=n_st, L=L * 1e3, lm=lm, I=I, g=g * 1e3, B=B * 1e3,
                j=j, R_ch=R_ch, V=V_el, P=P, v=v * 1e2, Q=Q, flowW=Q / P,
                n=n_disc, cost=n_disc * PRICE)


def table(rows, title, n=12, key='flowW'):
    print("\n" + title + "\n" + "-" * len(title))
    print("%4s %3s %5s %5s %5s %6s %6s %6s %7s %7s %8s %8s" %
          ("wall", "stn", "L", "lm", "I", "g", "B mT", "v cm/s", "Q ml/s",
           "ml/s/W", "discs", "Rp"))
    for r in sorted(rows, key=lambda r: -r[key])[:n]:
        print("%4.1f %3d %5.0f %5d %5.2f %6.1f %6.0f %6.2f %7.2f %7.3f %8d %8.0f" %
              (r['wall'], r['n_st'], r['L'], r['lm'], r['I'], r['g'], r['B'],
               r['v'], r['Q'], r['flowW'], r['n'], r['cost']))


def main():
    phys = [evaluate(*p) for p in
            ((a, b, c, d) for a in WALLS for b in STATIONS
             for c in LMS for d in CURRENTS)]
    # buildability: L/dh >= 3 (end-effect law), electrode must tile the channel
    build = [r for r in phys if r['L'] / DH_MM >= 3]
    affordable = [r for r in build if r['cost'] <= BUDGET]

    print("price Rp%.0f/disc, magnet budget Rp%.0f" % (PRICE, BUDGET))
    print("geometries tried %d | buildable %d | affordable %d"
          % (len(phys), len(build), len(affordable)))

    table(affordable, "A. AFFORDABLE, ranked on FLOW-PER-WATT (max Q per W)", 12, 'flowW')
    table(affordable, "B. AFFORDABLE, ranked on RAW FLOW RATE", 12, 'Q')

    # Pareto frontier on (Q, flowW): no candidate strictly beaten on both
    def pareto(rows):
        out = []
        for r in rows:
            dom = any(o['Q'] >= r['Q'] and o['flowW'] >= r['flowW']
                      and (o['Q'] > r['Q'] or o['flowW'] > r['flowW'])
                      for o in rows)
            if not dom:
                out.append(r)
        return sorted(out, key=lambda r: r['Q'])
    print("\nC. PARETO FRONTIER on (Q, Q/W), affordable only\n" + "-" * 45)
    print("%4s %5s %5s %5s %6s %6s %7s %7s %8s %8s" %
          ("wall", "L", "lm", "I", "B mT", "v cm/s", "Q ml/s", "ml/s/W", "discs", "Rp"))
    for r in pareto(affordable):
        print("%4.1f %5.0f %5d %5.2f %6.0f %6.2f %7.2f %7.3f %8d %8.0f" %
              (r['wall'], r['L'], r['lm'], r['I'], r['B'], r['v'], r['Q'],
               r['flowW'], r['n'], r['cost']))

    # what ONE more payday buys: best flow/watt at each disc count
    print("\nD. SPEND LADDER: best affordable design at each disc count\n" + "-" * 50)
    print("%5s %8s %5s %5s %5s %6s %7s %7s" %
          ("discs", "Rp", "L", "lm", "I", "B mT", "Q ml/s", "ml/s/W"))
    for n in (4, 8, 12, 16, 20, 24, 30, 36, 48, 60):
        cand = [r for r in build if r['n'] == n]
        if not cand:
            continue
        b = max(cand, key=lambda r: r['flowW'])
        print("%5d %8.0f %5.0f %5d %5.2f %6.0f %7.2f %7.3f   %s" %
              (n, b['cost'], b['L'], b['lm'], b['I'], b['B'], b['Q'], b['flowW'],
               "" if b['cost'] <= BUDGET else "<- over budget"))

    # as-built vs coverage fix
    print("\nE. COVERAGE: what the current 2-station layout costs you\n" + "-" * 55)
    for n_st, tag in ((2, "as-built (2 stations, 40 mm face)"),
                      (3, "3 stations"), (4, "4 stations"), (6, "6 stations")):
        r = evaluate(4.0, n_st, 5, 1.55)
        print("%-34s L=%3.0f mm B=%.0f mT v=%.2f cm/s Q=%5.2f ml/s  %.3f ml/s/W"
              % (tag, r['L'], r['B'], r['v'], r['Q'], r['flowW']))
    print("\nNOTE: v is computed over the covered length only; a channel longer")
    print("than its magnet footprint adds dead-zone Joule loss and no thrust.")

    base = evaluate(4.0, 6, 5, 1.55)
    print("\nBaseline v19 as printed (4 discs, lm=5, I=1.55, 120 mm electrode):")
    print("  full magnetic coverage would give v=%.2f cm/s Q=%.2f ml/s"
          % (base['v'], base['Q']))
    dead = evaluate(4.0, 2, 5, 1.55)
    print("  with only 2 stations (40 mm of 120 mm):  v=%.2f cm/s Q=%.2f ml/s"
          % (dead['v'], dead['Q']))


if __name__ == "__main__":
    main()
