"""Yoke thickness, v2: flux splits into the two side walls, so each wall and each
lug carries a fraction of the pole flux. Series reluctance, hard saturation.

Split factors per pole: plate carries full flux near the pole, but the segment
feeding one wall carries 1/2; each lug pair carries 1/4.
"""
import math

MU0 = 4e-7 * math.pi
BR, MU_R_MAG, L_MAG = 1.43, 1.05, 0.010
A_POLE = 0.120 * 0.040
L_GAP, L_PLATE, L_WALL, L_CAP = 0.017, 0.028, 0.022, 0.001
W_WALL = 0.150
BS, MU_R_STEEL = 1.9, 3000.0
A_LUG = 0.024 * 0.008 - 2 * math.pi * 0.0017 ** 2


def h_steel(B):
    if B <= 0:
        return 0.0
    hs = BS / (MU_R_STEEL * MU0)
    if B < BS:
        return hs * math.atanh(B / BS)
    return hs * math.atanh(0.999) + (B - BS) / MU0


def gap_field(t_mm):
    t = t_mm / 1000.0
    a_plate, a_wall = 0.120 * t, W_WALL * t

    def resid(phi):
        b_m = phi / A_POLE
        mmf_mag = -(b_m - BR) / (MU0 * MU_R_MAG) * L_MAG
        drop = (phi / A_POLE) / MU0 * L_GAP
        drop += h_steel(phi / (2 * a_plate)) * L_PLATE * 2      # plate to one wall
        drop += h_steel(phi / (2 * a_wall)) * L_WALL * 2        # wall carries half
        drop += h_steel(phi / (4 * A_LUG)) * 2 * t              # 4 lug pairs
        drop += h_steel(phi / A_POLE) * L_CAP * 2
        return mmf_mag - drop

    lo, hi = 1e-10, BR * A_POLE * 1.05
    for _ in range(300):
        mid = (lo + hi) / 2
        if resid(mid) > 0:
            lo = mid
        else:
            hi = mid
    phi = (lo + hi) / 2
    return phi / A_POLE, phi / (4 * A_LUG), phi / (2 * a_plate)


K, W, ZM, FLANGE_W, L = 0.44, 112.0, 22.0, 24.0, 150.0
print("t mm  B_gap   B_lug  B_plate  blank_w  mass/half")
for t in (1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0):
    bg, blug, bplate = gap_field(t)
    ba = (t + K * t) * math.pi / 2
    blank_w = W + 2 * ((ZM - ba) + (FLANGE_W - ba))
    print("%5.1f %5.0f mT %5.2f T %6.2f T  %7.1f   %5.0f g"
          % (t, bg * 1000, blug, bplate, blank_w, L * blank_w * t * 7.85e-3))
