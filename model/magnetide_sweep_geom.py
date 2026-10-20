"""Magnetide GEOMETRY SWEEP - the axis every previous script pinned.

magnetide_optimize{1..4}.py and magnetide_predict.py all fix H_MM=12, W_MM=16 and
sweep only wall / stations / tile count. The skill names the channel-to-magnet
ratio as the biggest practical lever, so this script sweeps the cross-section.

The coupling that makes it non-trivial:

    g      = h + 2*wall          magnet gap - h is IN the gap, so raising h costs B
    B      = 2*k_yoke*Br*l_m / (2*l_m + 1.05*g)
    j      = I / (h*L_el)        shrinking h RAISES current density -> more bubbles
    Q      = v*w*h  and  v = k_v*sqrt(I*B/(rho*h*L_el))

so Q ~ sqrt(B(h)/h) - B/h falls monotonically with h, meaning SMALLER h always wins
on the field side, while the bubble law pushes back through j. That collision is
where the interior optimum comes from, which is why the bubble term must live
INSIDE the integrator (skill: do not bolt a multiplier onto the final answer).

Tile budget is DERIVED, never swept free (skill lesson 13): n = n_st * 2 *
ceil(w/10) * k, asserted exactly. Coverage must be 100% or the electrode is a
resistor with a field on it.

Run:  python magnetide_sweep_geom.py
"""
import math

BR, SIGMA0, RHO = 1.45, 5.0, 1025.0
E_CHEM, K_YOKE, V_DERATE, THETA_K = 2.57, 0.90, 0.80, 0.006
L_EL, TILE_L, TILE_W, TILE_T = 120.0, 20.0, 10.0, 5.0
V_RAIL, I_FUSE, TILE_BUDGET = 12.0, 3.2, 48


def per_station(w, k):
    """Tiles per station per side: ceil(w/TILE_W) across, k deep. Returns (count, width)."""
    n_across = int(math.ceil(w / TILE_W))
    return n_across * k, n_across * TILE_W


def state(I, h, w, wall, n_st, k):
    """One operating point. Lengths mm, returns SI + ml/s."""
    n_side, mag_w = per_station(w, k)
    n_tile = n_st * 2 * n_side
    l_m = k * TILE_T
    g = h + 2 * wall
    l_drv = min(n_st * TILE_L, L_EL)

    B = K_YOKE * 2 * BR * (l_m / 1e3) / (2 * (l_m / 1e3) + 1.05 * (g / 1e3))
    h_m, w_m, l_el_m = h / 1e3, w / 1e3, L_EL / 1e3
    j = I / (h_m * l_el_m)
    th = 1.0 - math.exp(-THETA_K * (j / 10.0))
    se = SIGMA0 * (1.0 - th)
    R = w_m / (se * h_m * l_el_m)
    V_el = E_CHEM + I * R
    F = I * B * w_m * (l_drv / L_EL)
    v = math.sqrt(F / (RHO * w_m * h_m)) * V_DERATE
    Q = v * w_m * h_m * 1e6
    return dict(n_tile=n_tile, l_m=l_m, B=B, I=I, V=V_el, P=V_el * I, F=F,
                v=v * 1e2, Q=Q, QW=Q / (V_el * I), th=th, se=se,
                cov=100 * l_drv / L_EL, mag_w=mag_w, Dh=4 * w * h / (2 * w + 2 * h))


def at_rail(h, w, wall, n_st, k):
    lo, hi = 0.0, 8.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if state(mid, h, w, wall, n_st, k)['V'] < V_RAIL:
            lo = mid
        else:
            hi = mid
    return state(lo, h, w, wall, n_st, k)


def gates(r, wall, n_st):
    """Return list of failed gates; empty means buildable."""
    bad = []
    if r['n_tile'] != TILE_BUDGET:
        bad.append("tiles=%d" % r['n_tile'])
    if r['cov'] < 99.9:
        bad.append("cov=%.0f%%" % r['cov'])
    if r['V'] > V_RAIL + 1e-6:
        bad.append("V=%.2f>rail" % r['V'])
    if r['I'] > I_FUSE:
        bad.append("I=%.2f>fuse" % r['I'])
    if L_EL / r['Dh'] < 3.0:
        bad.append("L/Dh=%.1f<3" % (L_EL / r['Dh']))
    if r['mag_w'] < w_used:
        bad.append("mag_w=%.0f<w" % r['mag_w'])
    return bad


print("=" * 100)
print("GEOMETRY SWEEP - fixed %d-tile budget, 12 V rail, full coverage (6 stations)" % TILE_BUDGET)
print("Baseline (v19 channel 12x16, wall 1.5, 6 st, k=2): h=12 w=16")
print("=" * 100)

# --- Sweep A: channel HEIGHT, everything else at the recommended build -------
print("\n--- A. channel height h at w=16, wall=1.5, 6 stations, k=2 (48 tiles) ---")
print("%5s %6s %5s %7s %5s %7s %8s %9s %8s" %
      ("h mm", "g mm", "B mT", "j kA/m2", "th", "I rail", "v cm/s", "Q ml/s", "Q/W"))
base = None
for h in (4, 6, 8, 10, 12, 14, 16, 20, 24):
    r = at_rail(h, 16.0, 1.5, 6, 2)
    if base is None:
        base = r
    tag = " <- baseline" if h == 12 else ""
    print("%5.0f %6.0f %5.0f %7.2f %5.2f %7.2f %8.2f %9.2f %8.2f%s" %
          (h, h + 3, r['B'] * 1e3, r['I'] / (h / 1e3 * L_EL / 1e3) / 1e3, r['th'],
           r['I'], r['v'], r['Q'], r['QW'], tag))

# --- Sweep B: joint (h, w) search, Pareto on (Q, Q/W) ------------------------
print("\n--- B. joint (h,w), Pareto frontier on (Q, Q/W), same budget ---")
print("   w must be covered by ceil(w/10) tiles; at 48 tiles and 6 stations")
print("   k = 48 / (6*2*ceil(w/10)), so widening the channel thins the magnet.\n")

rows = []
for h in (4, 6, 8, 10, 12, 16, 20):
    for w in (8, 10, 12, 16, 20, 24, 30, 40):
        n_across = int(math.ceil(w / TILE_W))
        denom = 6 * 2 * n_across
        if TILE_BUDGET % denom:
            continue
        k = TILE_BUDGET // denom
        if k < 1 or k > 4:
            continue
        w_used = w
        r = at_rail(h, w, 1.5, 6, k)
        if r['mag_w'] < w:
            continue
        bad = gates(r, 1.5, 6)
        rows.append((h, w, k, r, bad))

print("%5s %5s %3s %5s %6s %7s %8s %9s %7s  %s" %
      ("h", "w", "k", "l_m", "B mT", "v cm/s", "Q ml/s", "Q/W", "tiles", "gates"))
for h, w, k, r, bad in sorted(rows, key=lambda x: -x[3]['Q']):
    print("%5.0f %5.0f %3d %5.0f %6.0f %7.2f %8.2f %9.2f %7d  %s" %
          (h, w, k, r['l_m'], r['B'] * 1e3, r['v'], r['Q'], r['QW'], r['n_tile'],
           "OK" if not bad else ",".join(bad)))

print("\n--- Pareto frontier (no dominated row survives) ---")
print("%5s %5s %3s %8s %9s" % ("h", "w", "k", "Q ml/s", "Q/W"))
front = []
for h, w, k, r, bad in rows:
    if bad:
        continue
    dom = any((o[3]['Q'] >= r['Q'] and o[3]['QW'] >= r['QW'] and
               (o[3]['Q'] > r['Q'] or o[3]['QW'] > r['QW']))
              for o in rows if not o[4])
    if not dom:
        front.append((h, w, k, r))
for h, w, k, r in sorted(front, key=lambda x: -x[3]['Q']):
    print("%5.0f %5.0f %3d %8.2f %9.2f" % (h, w, k, r['Q'], r['QW']))
