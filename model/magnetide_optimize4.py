"""Magnetide optimiser v4 - adds the bubble-conductivity law.

v3 omitted it: at j = 1.2 kA/m2 the model was quietly assuming clean 5 S/m
water, which is the optimistic end of the physically defensible range. The
skill's rule is theta = 1 - exp(-0.006*jd) with jd in mA/cm2, applied INSIDE
the electrical model, plus a Bruggeman cross-check as the lower bound.

At fixed CURRENT the Lorentz force (and so v) does not depend on sigma at all -
sigma only sets the VOLTAGE you must supply to push that current through a
bubble-laden electrolyte. So the bubble law hits P, and therefore Q/W, hard.

Run: python magnetide_optimize4.py [price_per_tile] [budget_idr]
"""
import math
import sys

BR = 1.45
SIGMA0 = 5.0
RHO = 1025.0
E_CHEM = 2.57
K_YOKE = 0.90
H_MM, W_MM = 12.0, 16.0
TILE_L, TILE_T = 20.0, 5.0
V_DERATE = 0.80
DH_MM = 4 * W_MM * H_MM / (2 * (W_MM + H_MM))

WALLS = (4.0, 2.5, 1.5)
KS = (1, 2, 3, 4, 5, 6)
CURRENTS = (1.15, 1.55, 2.0, 2.5, 3.0)
N_ACROSS = 2

PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 6325.0
BUDGET = float(sys.argv[2]) if len(sys.argv) > 2 else 250000.0
V_SUPPLY = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0   # single rail, V
I_FUSE = 3.2                                                  # INA219 ceiling, A
# Belgian/English literature law; theta saturates near 1 as jd grows
THETA_K = 0.006          # per mA/cm2


def sigma_eff(jd_mAcm2, law='linear'):
    th = 1.0 - math.exp(-THETA_K * jd_mAcm2)
    if law == 'linear':
        return SIGMA0 * (1.0 - th), th
    if law == 'bruggeman':
        return SIGMA0 * (1.0 - th) ** 1.5, th
    if law == 'maxwell':
        return SIGMA0 * (1.0 - th) / (1.0 + 0.5 * th), th
    raise ValueError(law)


def gap_field(l_m, g):
    return K_YOKE * 2 * BR * l_m / (2 * l_m + 1.05 * g)


def evaluate(wall, n_st, k, I, law='linear'):
    h, w = H_MM / 1e3, W_MM / 1e3
    L = n_st * TILE_L / 1e3
    g = (H_MM + 2 * wall) / 1e3
    l_m = k * TILE_T / 1e3
    B = gap_field(l_m, g)
    n_tile = 2 * n_st * N_ACROSS * k
    j = I / (h * L)                      # A/m2
    jd = j / 10.0                        # mA/cm2  (1 mA/cm2 = 10 A/m2)
    se, th = sigma_eff(jd, law)
    R_ch = w / (se * h * L)
    V_el = E_CHEM + I * R_ch
    P = V_el * I
    v = math.sqrt(j * B * L / RHO) * V_DERATE   # momentum form: f*L = rho*v^2
    Q = v * w * h * 1e6
    return dict(wall=wall, n_st=n_st, L=L * 1e3, k=k, lm=l_m * 1e3, I=I, g=g * 1e3,
                B=B * 1e3, j=j, jd=jd, th=th, se=se, R_ch=R_ch, V=V_el, P=P,
                v=v * 1e2, Q=Q, flowW=Q / P, n=n_tile, cost=n_tile * PRICE)


def table(rows, title, key='flowW', n=10):
    print("\n" + title + "\n" + "-" * len(title))
    print("%4s %3s %5s %4s %5s %6s %6s %6s %7s %7s %6s %8s" %
          ("wall", "stn", "L", "k", "I", "B mT", "j kA/m2", "v cm/s", "Q ml/s",
           "ml/s/W", "tiles", "Rp"))
    for r in sorted(rows, key=lambda r: -r[key])[:n]:
        print("%4.1f %3d %5.0f %4d %5.2f %6.0f %8.2f %6.2f %7.2f %7.3f %6d %8.0f" %
              (r['wall'], r['n_st'], r['L'], r['k'], r['I'], r['B'], r['j'] / 1e3,
               r['v'], r['Q'], r['flowW'], r['n'], r['cost']))


def main():
    rows = [evaluate(*p) for p in
            ((a, b, c, d) for a in WALLS for b in (2, 3, 4, 5, 6)
             for c in KS for d in CURRENTS)]
    # supply gate: the PSU cannot invent voltage, so V_el <= rail and I <= fuse
    build = [r for r in rows if r['L'] / DH_MM >= 3
             and r['V'] <= V_SUPPLY and r['I'] <= I_FUSE]
    aff = [r for r in build if r['cost'] <= BUDGET]
    print("tile Rp%.0f, magnet budget Rp%.0f -> %d tiles max | rail %.0f V, fuse %.1f A"
          % (PRICE, BUDGET, int(BUDGET // PRICE), V_SUPPLY, I_FUSE))

    table(aff, "A. AFFORDABLE, ranked on FLOW-PER-WATT (bubble-corrected)", 'flowW')
    table(aff, "B. AFFORDABLE, ranked on RAW FLOW", 'Q')

    print("\nC. WHAT THE BUBBLE LAW DOES to the recommended row")
    print("-" * 52)
    for law in ('linear', 'bruggeman', 'maxwell'):
        r = evaluate(1.5, 6, 1, 1.15, law)
        print("  %-9s sigma_eff=%4.2f S/m  V_el=%5.2f V  P=%5.2f W  Q/W=%.2f"
              % (law, r['se'], r['V'], r['P'], r['flowW']))

    print("\nD. SPEND LADDER (best Q/W at each tile count)\n" + "-" * 46)
    print("%6s %8s %5s %4s %5s %6s %7s %7s" %
          ("tiles", "Rp", "L", "k", "I", "B mT", "Q ml/s", "ml/s/W"))
    for n in sorted({r['n'] for r in build}):
        cand = [r for r in build if r['n'] == n]
        b = max(cand, key=lambda r: r['flowW'])
        print("%6d %8.0f %5.0f %4d %5.2f %6.0f %7.2f %7.3f  %s" %
              (n, b['cost'], b['L'], b['k'], b['I'], b['B'], b['Q'], b['flowW'],
               "" if b['cost'] <= BUDGET else "over"))

    best = max(aff, key=lambda r: r['flowW'])
    print("\nBEST AFFORDABLE Q/W: %d st x k=%d, wall %.1f, I=%.2f A" %
          (best['n_st'], best['k'], best['wall'], best['I']))
    print("  B=%.0f mT  L=%.0f mm  g=%.0f mm  j=%.2f kA/m2  theta=%.2f  sigma_eff=%.2f"
          % (best['B'], best['L'], best['g'], best['j'] / 1e3, best['th'], best['se']))
    print("  v=%.2f cm/s  Q=%.2f ml/s  V_el=%.2f V  P=%.2f W  Q/W=%.2f  %d tiles Rp%.0f"
          % (best['v'], best['Q'], best['V'], best['P'], best['flowW'],
             best['n'], best['cost']))


if __name__ == "__main__":
    main()
