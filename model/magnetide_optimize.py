"""Magnetide final-design optimiser.

Screens the buildable design space for the tabletop MHD drive unit and ranks on
flow-per-watt (Q/P_in), because efficiency is not attainable at this scale.

Model sources
  - B(gap): closed-form yoke-assisted pair, skill mhd-seawater-field-solver
  - v, Q, P: momentum form (f*L = rho*v^2), skill mhd-seawater-field-solver
  - E_chem = 2.57 V, R_ch slope: Delannoy et al., Magnetohydrodynamics 61 (2025) 55-66
  - coupling-length dominance: Cao et al., Magnetochemistry 12 (2026) 89

All lengths mm in the input table, metres in the physics.
Run:  python magnetide_optimize.py [disc_price_idr]
"""
import math
import sys

MU0 = 4e-7 * math.pi
BR = 1.45          # N52 remanence, T (Arnold datasheet)
SIGMA = 5.0        # seawater/5% brine conductivity, S/m
RHO = 1025.0       # brine density, kg/m3
E_CHEM = 2.57      # electrochemical overpotential at our j, V (Delannoy 2025 fit)
K_YOKE = 0.90      # real-steel leakage/duty derate on the ideal yoke formula
WALL_MM = (4.0, 2.5, 1.5)     # printed wall thickness per side
L_MM = (40, 60, 80, 100, 120)  # active (electrode) length
LM_MM = (5, 10, 15, 20, 25)    # magnet thickness per side = discs stacked
I_A = (1.15, 1.55, 2.0, 2.5, 3.0)
H_MM = 12.0        # channel inner height  (pole gap)
W_MM = 16.0        # channel inner width   (electrode gap = current path)
DISC_D = 20.0      # pole face diameter, mm
DISC_T = 5.0       # one disc thickness, mm

DISC_PRICE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0


def gap_field_T(l_m, g, br=BR, k=K_YOKE):
    """Yoke-assisted magnet pair, uniform gap (skill closed form)."""
    return k * 2 * br * l_m / (2 * l_m + 1.05 * g)


def row(wall_mm, L_mm, lm_mm, I):
    h, w, L = H_MM / 1e3, W_MM / 1e3, L_mm / 1e3
    g = (H_MM + 2 * wall_mm) / 1e3                 # magnet gap
    lm = lm_mm / 1e3
    B = gap_field_T(lm, g)
    # pole sections of DISC_D each, both sides; coverage capped at active length
    n_p = math.ceil(L_mm / DISC_D)
    cov = min(n_p * DISC_D, L_mm) / 1e3
    n_disc = 2 * n_p * max(1, round(lm_mm / DISC_T))
    # electrolytics
    A_el = h * L                                   # electrode area (side wall)
    j = I / A_el                                   # A/m2
    R_ch = w / (SIGMA * h * L)                     # ohm
    V_el = E_CHEM + I * R_ch
    P_in = V_el * I
    # momentum form, inviscid, over the region that actually sees the field
    v = math.sqrt(j * B * cov / RHO)
    v_derate = 0.80 * v                            # friction/end/field-non-uniformity
    Q = v_derate * w * h                           # m3/s
    Q_mls = Q * 1e6
    return dict(wall=wall_mm, L=L_mm, lm=lm_mm, I=I, g=g * 1e3, B=B * 1e3,
                cov=cov * 1e3, cov_pct=100 * cov / L, j=j, R_ch=R_ch, V_el=V_el,
                P=P_in, v=v_derate * 1e2, v_ideal=v * 1e2, Q=Q_mls,
                flowW=Q_mls / P_in, n_disc=n_disc,
                cost=n_disc * DISC_PRICE)


def main():
    rows = [row(*p) for p in
            ((a, b, c, d) for a in WALL_MM for b in L_MM for c in LM_MM for d in I_A)]
    # buildability gate: printed wall >= 1.2 mm ok; L/section >= 3 (skill end-effect law)
    rows = [r for r in rows if r['L'] / (4 * W_MM * H_MM / (2 * (W_MM + H_MM))) >= 3]

    def show(rs, key, title, n=12):
        print("\n" + title)
        print("-" * len(title))
        print("%4s %5s %5s %5s %6s %6s %7s %6s %7s %7s %6s" %
              ("wall", "L", "lm", "I", "g", "B", "cover%", "v cm/s", "Q ml/s",
               "ml/s/W", "discs"))
        for r in rs[:n]:
            print("%4.1f %5d %5d %5.2f %6.1f %6.0f %7.0f %6.2f %7.2f %7.3f %6d" %
                  (r['wall'], r['L'], r['lm'], r['I'], r['g'], r['B'],
                   r['cov_pct'], r['v'], r['Q'], r['flowW'], r['n_disc']))

    ok = [r for r in rows if r['Q'] >= 5.0]        # their pass target: >=5 ml/s
    show(sorted(ok, key=lambda r: -r['flowW']), 'flowW',
         "A. PASS flow target (>=5 ml/s), ranked on FLOW-PER-WATT", 15)
    show(sorted(ok, key=lambda r: -r['Q']), 'Q',
         "B. PASS flow target, ranked on RAW FLOW RATE", 15)
    show(sorted([r for r in rows if r['cov_pct'] >= 99.9],
                key=lambda r: -r['flowW']),
         'flowW', "C. Fully covered channel only (B over 100% of electrodes)", 10)

    best = sorted(ok, key=lambda r: -r['flowW'])[0]
    print("\nWINNER (flow/watt): wall %.1f mm, L %d mm, lm %d mm, I %.2f A" %
          (best['wall'], best['L'], best['lm'], best['I']))
    print("  g=%.1f mm  B=%.0f mT  coverage=%.0f%%  j=%.0f A/m2  V_el=%.2f V" %
          (best['g'], best['B'], best['cov_pct'], best['j'], best['V_el']))
    print("  v=%.2f cm/s  Q=%.2f ml/s  P=%.2f W  -> %.3f ml/s/W   discs=%d" %
          (best['v'], best['Q'], best['P'], best['flowW'], best['n_disc']))
    if DISC_PRICE:
        print("  magnet cost Rp%d at Rp%d/disc" % (best['cost'], DISC_PRICE))
    print("\nBaseline for comparison (current v19: wall 4, L 120, lm 5, I 1.55):")
    b = row(4.0, 120, 5, 1.55)
    print("  B=%.0f mT coverage=%.0f%%  v=%.2f cm/s  Q=%.2f ml/s  P=%.2f W  %.3f ml/s/W"
          % (b['B'], b['cov_pct'], b['v'], b['Q'], b['P'], b['flowW']))


if __name__ == "__main__":
    main()