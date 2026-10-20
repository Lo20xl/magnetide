"""Magnetide GEOMETRY SWEEP v2 - with cost, tilability and the fuse gate that bites.

Supersedes magnetide_sweep_geom.py, whose Pareto frontier degenerated to w=40
because NOTHING cost anything. This version carries the constraints the skill
demands (lesson 13) and checks them before ranking:

  * magnet count is DERIVED: n = n_station * 2 * ceil(w/TILE_W) * k
  * tiles must be TILABLE:  w % 10 == 0  and  L % 10 == 0
  * budget: n * price <= budget   (price at the marketplace FLOOR, Rp6325)
  * graphite: the electrode plates cost real money, Rp45000 per 120x20 plate
  * rail: 12 V found by BISECTION on V_el(I) = V_rail, never by sweeping I
  * fuse:  I <= 3.2 A   (INA219 measurement ceiling)
  * end-effect: L_el / D_h >= 3

The structural result this sweep exists to test:

  V_el = E_chem + j*w/sigma_eff(j)   =>   at a fixed rail, j is fixed by w ALONE.

Height never enters the electrical side; it only enters through the magnet gap
g = h + 2*wall. So h is a pure field lever (smaller = stronger B) and w is a
pure bubble lever (wider = lower j = fewer bubbles). They do not fight each
other directly, which is why the optimum separates cleanly instead of sitting
at some interior compromise.

Ranking metric is B*w*h*L (skill: an area-blind proxy hides w entirely).

Run:  python magnetide_sweep_geom2.py
"""
import math

BR, SIGMA0, RHO = 1.45, 5.0, 1025.0
E_CHEM, K_YOKE, V_DERATE, THETA_K = 2.57, 0.90, 0.80, 0.006
L_EL, TILE_L, TILE_W, TILE_T = 120.0, 20.0, 10.0, 5.0
V_RAIL, I_FUSE = 12.0, 3.2
PRICE_TILE = 6325.0        # Tokopedia floor, 20x10x5 N52 block
PLATE_PRICE = 45000.0      # graphite plate 120x20 mm
BUDGET = 350000.0          # magnet budget inside the ~Rp700k envelope
WALL = 1.5                 # printed wall, mm


def solve(h, w, n_st, k):
    """One candidate. Returns None if not buildable, else a row dict."""
    n_across = int(math.ceil(w / TILE_W))
    n_tile = n_st * 2 * n_across * k
    l_m = k * TILE_T
    g = h + 2 * WALL
    l_drv = min(n_st * TILE_L, L_EL)

    # -- gates that do not need the solve -----------------------------------
    if w % 10 or L_EL % 10:
        return None                                   # not tilable
    if l_drv / L_EL < 0.999:
        return None                                   # coverage < 100% -> resistor
    Dh = 4 * w * h / (2 * w + 2 * h)
    if L_EL / Dh < 3.0:
        return None                                   # end effects dominate
    mag_cost = n_tile * PRICE_TILE
    if mag_cost > BUDGET:
        return None                                   # over budget

    B = K_YOKE * 2 * BR * (l_m / 1e3) / (2 * (l_m / 1e3) + 1.05 * (g / 1e3))
    h_m, w_m, l_el = h / 1e3, w / 1e3, L_EL / 1e3
    A = h_m * l_el

    lo, hi = 0.0, 8.0                                # bisection on the rail
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        th = 1.0 - math.exp(-THETA_K * (mid / A / 10.0))
        R = w_m / (SIGMA0 * (1.0 - th) * A)
        if E_CHEM + mid * R < V_RAIL:
            lo = mid
        else:
            hi = mid
    I = lo
    if I > I_FUSE:
        return None                                   # over the measurement ceiling
    j = I / A
    th = 1.0 - math.exp(-THETA_K * (j / 10.0))
    se = SIGMA0 * (1.0 - th)
    R = w_m / (se * A)
    V = E_CHEM + I * R
    F = I * B * w_m
    v = math.sqrt(F / (RHO * w_m * h_m)) * V_DERATE
    Q = v * w_m * h_m * 1e6

    plates = 2 * n_st                                # one plate per station per side
    return dict(h=h, w=w, k=k, n_tile=n_tile, l_m=l_m, B=B, I=I, V=V, j=j,
                th=th, se=se, F=F * 1e3, v=v * 1e2, Q=Q, QW=Q / (V * I),
                mag=mag_cost, plate=plates * PLATE_PRICE / n_st,
                cost=mag_cost + 2 * PLATE_PRICE, rank=B * w * h * L_EL,
                Dh=Dh)


print("=" * 116)
print("GEOMETRY SWEEP v2  -  12 V rail, 6 stations, wall %.1f mm, budget Rp%dk"
      % (WALL, BUDGET / 1000))
print("Gates: tilable w%%10==0 | coverage 100%% | L/Dh>=3 | magnets<=budget | I<=3.2 A")
print("=" * 116)

rows = []
for h in (4, 6, 8, 10, 12, 16, 20):
    for w in (10, 20, 30, 40):
        for k in (1, 2, 3, 4):
            r = solve(h, w, 6, k)
            if r:
                rows.append(r)

print("\n%4s %4s %2s %3s %6s %6s %6s %6s %7s %8s %7s %10s"
      % ("h", "w", "k", "n", "B mT", "I A", "mA/c", "th", "v cm/s", "Q ml/s", "Q/W", "Rp"))
for r in sorted(rows, key=lambda x: -x['rank']):
    print("%4.0f %4.0f %2d %3d %6.0f %6.2f %6.0f %6.3f %7.2f %8.2f %7.2f %10.0f"
          % (r['h'], r['w'], r['k'], r['n_tile'], r['B'] * 1e3, r['I'], r['j'] / 10,
             r['th'], r['v'], r['Q'], r['QW'], r['cost']))

print("\n--- Pareto frontier on (Q, Q/W) among buildable rows ---")
print("%4s %4s %2s %6s %7s %8s %7s %10s"
      % ("h", "w", "k", "B mT", "v cm/s", "Q ml/s", "Q/W", "Rp"))
for r in sorted(rows, key=lambda x: -x['Q']):
    dom = any(o['Q'] >= r['Q'] and o['QW'] >= r['QW'] and
              (o['Q'] > r['Q'] or o['QW'] > r['QW']) for o in rows)
    if not dom:
        print("%4.0f %4.0f %2d %6.0f %7.2f %8.2f %7.2f %10.0f"
              % (r['h'], r['w'], r['k'], r['B'] * 1e3, r['v'], r['Q'], r['QW'], r['cost']))

print("\n--- Best Q/W under Rp200k (budget lane, leaves room for PSU + yoke) ---")
cheap = [r for r in rows if r['cost'] <= 200000]
if cheap:
    r = max(cheap, key=lambda x: x['QW'])
    print("%4.0f %4.0f %2d  B=%4.0f mT  I=%.2f A  v=%.2f cm/s  Q=%.2f ml/s  "
          "Q/W=%.2f  Rp%0.0f"
          % (r['h'], r['w'], r['k'], r['B'] * 1e3, r['I'], r['v'], r['Q'], r['QW'], r['cost']))

print("\n--- Best Q at any budget ---")
if rows:
    r = max(rows, key=lambda x: x['Q'])
    print("%4.0f %4.0f %2d  B=%4.0f mT  I=%.2f A  v=%.2f cm/s  Q=%.2f ml/s  "
          "Q/W=%.2f  Rp%0.0f"
          % (r['h'], r['w'], r['k'], r['B'] * 1e3, r['I'], r['v'], r['Q'], r['QW'], r['cost']))

print("\n--- Baseline for comparison (Lane A: h12 w16 k2, 48 tiles) ---")
b = solve(12, 16, 6, 2)
if b:
    print("     B=%4.0f mT  I=%.2f A  v=%.2f cm/s  Q=%.2f ml/s  Q/W=%.2f  Rp%0.0f"
          % (b['B'] * 1e3, b['I'], b['v'], b['Q'], b['QW'], b['cost']))
