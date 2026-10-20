"""Magnetide PREDICT - the model behind Magnetide-final-design.md

Separates the two lengths the earlier versions conflated:
  L_el    electrode length   (fixed by the printed channel: 120 mm)
  L_drive axial extent of the field = 20 mm x (number of pole stations)

That distinction is the whole point: a long electrode with short magnets pays
full resistive loss over 120 mm but only gets Lorentz force over L_drive.
Everything else (B, sigma_eff, P) follows the skill + Delannoy fit.

Rail-limited operating point is found by bisection: the PSU cannot invent
voltage, so for V_rail = 12 V the current settles where V_el(I) = V_rail.

Run:  python magnetide_predict.py
"""
import math

BR, SIGMA0, RHO = 1.45, 5.0, 1025.0
E_CHEM, K_YOKE, V_DERATE, THETA_K = 2.57, 0.90, 0.80, 0.006
H_MM, W_MM = 12.0, 16.0          # channel inner height, width (current path)
TILE_L, TILE_T = 20.0, 5.0       # 20x10x5 N52 tile
L_EL = 120.0                     # electrode length, mm (v19 print)
V_RAIL, I_FUSE = 12.0, 3.2


def gap_field(l_m_mm, g_mm):
    return K_YOKE * 2 * BR * (l_m_mm / 1e3) / (2 * (l_m_mm / 1e3) + 1.05 * (g_mm / 1e3))


def state(I, wall, n_st, k):
    """Everything at a given current. Lengths mm."""
    h, w = H_MM / 1e3, W_MM / 1e3
    l_el, l_drv = L_EL / 1e3, min(n_st * TILE_L, L_EL) / 1e3
    g = H_MM + 2 * wall
    B = gap_field(k * TILE_T, g)
    j = I / (h * l_el)
    th = 1.0 - math.exp(-THETA_K * (j / 10.0))
    se = SIGMA0 * (1.0 - th)
    R = w / (se * h * l_el)
    V_el = E_CHEM + I * R
    F = I * B * w * (l_drv / l_el)                 # Lorentz force, N
    v = math.sqrt(F / (RHO * w * h)) * V_DERATE    # f*L = rho*v^2, f = F/(w*h*L_drv)
    Q = v * w * h * 1e6
    return dict(I=I, V=V_el, P=V_el * I, B=B, j=j, th=th, se=se, R=R,
                F=F, v=v * 1e2, Q=Q, flowW=Q / (V_el * I),
                n_tile=2 * n_st * 2 * k, cov=100 * l_drv / l_el)


def at_rail(wall, n_st, k, rail=V_RAIL):
    """Current that the rail actually delivers (bisection on V_el(I) = rail)."""
    lo, hi = 0.0, 8.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if state(mid, wall, n_st, k)['V'] < rail:
            lo = mid
        else:
            hi = mid
    return state(lo, wall, n_st, k)


def line(tag, r):
    print("%-38s I=%5.2f A V=%5.2f  B=%4.0f mT cov=%3.0f%%  j=%4.2f kA/m2  "
          "F=%5.1f mN  v=%5.2f cm/s  Q=%6.2f ml/s  P=%6.2f W  Q/W=%5.2f  %2d tiles"
          % (tag, r['I'], r['V'], r['B'] * 1e3, r['cov'], r['j'] / 1e3, r['F'] * 1e3,
             r['v'], r['Q'], r['P'], r['flowW'], r['n_tile']))


def main():
    print("=" * 118)
    print("AS BUILT (v19: wall 4 mm, 2 pole stations, 1 tile/side) - rail-limited")
    print("=" * 118)
    line("as-built", at_rail(4.0, 2, 1))

    print("\n" + "=" * 118)
    print("DROP-IN FIX 1: fill the tray (6 stations) - same magnets, same wall")
    print("=" * 118)
    line("6 stations, 1 tile/side (24 tiles)", at_rail(4.0, 6, 1))
    print("\n" + "=" * 118)
    print("DROP-IN FIX 2: + thin the wall 4.0 -> 1.5 mm")
    print("=" * 118)
    line("6 stations, 1 tile/side, wall 1.5 (24)", at_rail(1.5, 6, 1))
    line("6 stations, 2 tiles/side, wall 2.5 (48)", at_rail(2.5, 6, 2))
    line("6 stations, 2 tiles/side, wall 1.5 (48)", at_rail(1.5, 6, 2))

    print("\n" + "=" * 118)
    print("CURRENT SWEEP at the recommended build (wall 1.5, 6 stations, 2 tiles)")
    print("=" * 118)
    print("%6s %7s %8s %9s %10s %9s" % ("I (A)", "V_el", "P (W)", "v cm/s", "Q ml/s", "Q/W"))
    for I in (0.5, 1.0, 1.15, 1.5, 2.0, 2.5, 3.0):
        r = state(I, 1.5, 6, 2)
        flag = "" if r['V'] <= V_RAIL else "  exceeds 12 V rail"
        print("%6.2f %7.2f %8.2f %9.2f %10.2f %9.2f%s"
              % (I, r['V'], r['P'], r['v'], r['Q'], r['flowW'], flag))

    print("\n" + "=" * 118)
    print("BUBBLE-LAW SENSITIVITY at the rail-limited recommended point")
    print("=" * 118)
    r = at_rail(1.5, 6, 2)
    def rail_current(exp):
        lo, hi = 0.0, 8.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            j = mid / (H_MM / 1e3 * L_EL / 1e3)
            th = 1.0 - math.exp(-THETA_K * (j / 10.0))
            se = SIGMA0 * (1.0 - th) ** exp
            R = (W_MM / 1e3) / (se * H_MM / 1e3 * L_EL / 1e3)
            if E_CHEM + mid * R < V_RAIL:
                lo = mid
            else:
                hi = mid
        j = lo / (H_MM / 1e3 * L_EL / 1e3)
        th = 1.0 - math.exp(-THETA_K * (j / 10.0))
        return lo, th, SIGMA0 * (1 - th) ** exp

    for name, exp in (("linear", 1.0), ("Bruggeman", 1.5)):
        I, th, se = rail_current(exp)
        rr = state(I, 1.5, 6, 2)
        print("  %-10s sigma_eff=%.2f S/m  theta=%.2f  rail current=%4.2f A  "
              "v=%5.2f cm/s  Q=%5.2f ml/s  Q/W=%5.2f"
              % (name, se, th, I, rr['v'], rr['Q'], rr['flowW']))


if __name__ == "__main__":
    main()
