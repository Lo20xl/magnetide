"""What changes when the supply is 30 V / 10 A instead of 12 V.

The 12 V gate was the binding constraint on every high-flow design. Re-run the
same model with the real rail and the picture changes in one specific way:
flow keeps rising with current until the chemistry (bubble blanketing) or the
rail stops it - so the optimum stops being "as much current as the brick allows"
and becomes an interior point.

Run: python magnetide_rail30.py
"""
import math
import sys

BR, SIGMA0, RHO = 1.45, 5.0, 1025.0
E_CHEM, K_YOKE, V_DERATE, THETA_K = 2.57, 0.90, 0.80, 0.006
H_MM, W_MM, L_EL = 12.0, 16.0, 120.0
TILE_T = 5.0

RAIL = 30.0        # user's PSU
PSU_A = 10.0       # PSU current ceiling
INA_A = 3.2        # INA219 measurement ceiling (the real limit until replaced)


def B_of(k, wall):
    l_m, g = k * TILE_T / 1e3, (H_MM + 2 * wall) / 1e3
    return K_YOKE * 2 * BR * l_m / (2 * l_m + 1.05 * g)


def solve(I, n_st, k, wall, l_el=L_EL):
    h, w, le = H_MM / 1e3, W_MM / 1e3, l_el / 1e3
    l_drv = min(n_st * 20.0, l_el) / 1e3
    B = B_of(k, wall)
    j = I / (h * le)
    th = 1.0 - math.exp(-THETA_K * (j / 10.0))
    se = SIGMA0 * (1.0 - th)
    R = w / (se * h * le)
    V = E_CHEM + I * R
    F = I * B * w * (l_drv / le)
    v = math.sqrt(F / (RHO * w * h)) * V_DERATE
    return dict(I=I, V=V, P=V * I, B=B * 1e3, j=j, th=th, se=se, F=F * 1e3,
                v=v * 1e2, Q=v * w * h * 1e6, flowW=v * w * h * 1e6 / (V * I),
                n=2 * n_st * 2 * k, cost=2 * n_st * 2 * k * 6325)


def scan(n_st, k, wall, imax):
    """Walk current up until the rail is hit; return every feasible point."""
    out, I = [], 0.05
    while I <= imax:
        r = solve(I, n_st, k, wall)
        if r['V'] > RAIL:
            break
        out.append(r)
        I = round(I + 0.05, 2)
    return out


def main():
    print("rail %.0f V, PSU %.0f A, INA219 %.1f A\n" % (RAIL, PSU_A, INA_A))
    configs = [(6, 2, 1.5), (6, 1, 1.5), (5, 2, 1.5), (4, 3, 1.5), (6, 3, 1.5), (3, 4, 1.5)]
    print("%-22s %-28s %s" % ("geometry", "max flow (rails/fuse limited)", "best Q/W"))
    print("-" * 104)
    for n_st, k, wall in configs:
        rows = scan(n_st, k, wall, PSU_A)
        if not rows:
            continue
        feas = [r for r in rows if r['I'] <= INA_A]     # measurable today
        bestQ = max(rows, key=lambda r: r['Q'])
        bestW = max(rows, key=lambda r: r['flowW'])
        bq = max(feas, key=lambda r: r['Q']) if feas else None
        tag = "%d st x k%d (%.0f tiles)" % (n_st, k, 2 * n_st * 2 * k)
        print("%-22s Q=%5.1f ml/s @ %4.2fA %5.1fV %5.1fW  |  Q/W=%4.2f @ %.2fA %4.1fV  "
              "| meas<=3.2A: Q=%5.1f"
              % (tag, bestQ['Q'], bestQ['I'], bestQ['V'], bestQ['P'],
                 bestW['flowW'], bestW['I'], bestW['V'],
                 bq['Q'] if bq else float('nan')))

    print("\nFULL CURVE for the recommended geometry (6 stations, 2 tiles, wall 1.5):")
    print("%5s %7s %7s %6s %8s %8s %8s %7s" %
          ("I", "V_el", "P", "theta", "v cm/s", "Q ml/s", "Q/W", "note"))
    for r in scan(6, 2, 1.5, PSU_A):
        if abs(r['I'] * 10 - round(r['I'] * 10)) > 0.01:
            continue
        note = "" if r['I'] <= INA_A else "needs >3.2 A sensing"
        if abs(r['I'] * 2 - round(r['I'] * 2)) < 0.01:
            print("%5.2f %7.2f %7.1f %6.2f %8.2f %8.2f %8.2f  %s"
                  % (r['I'], r['V'], r['P'], r['th'], r['v'], r['Q'], r['flowW'], note))


if __name__ == "__main__":
    main()
