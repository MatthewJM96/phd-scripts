from math import cosh, tanh
from typing import List, Tuple


def calculate_jorek_ffprime(
    ff_bnd: float,
    ff_axis: float,
    ff_coef: List[float],
    psi_bnd: float,
    psi_axis: float,
    num: int,
) -> List[Tuple[float, float]]:
    ffprime = []

    for idx in range(num):
        delta_psi = psi_bnd - psi_axis

        psi = psi_axis + float(idx) * delta_psi / float(num - 1)
        psi_n = (psi - psi_axis) / delta_psi

        no_delta_psi = 1.0
        if ff_coef[8] == 1.0:
            no_delta_psi = delta_psi

        d_pert = (
            ff_coef[5]
            / cosh((psi_n - ff_coef[6]) / ff_coef[7]) ** 2
            / (2.0 * ff_coef[7])
            / delta_psi
            * no_delta_psi
        )

        prof0 = (ff_axis - ff_bnd) * (
            1.0 + ff_coef[0] * psi_n + ff_coef[1] * psi_n**2 + ff_coef[2] * psi_n**3
        )

        prof0 = prof0 + d_pert

        sig_F = ff_coef[3]
        psi_barrier = ff_coef[4]

        psi_star = (psi_n - psi_barrier) / sig_F
        psi_star = min(max(psi_star, -40.0), 40.0)

        tanh1 = tanh(psi_star)

        atn = 0.50 - 0.50 * tanh1

        ffprime.append((psi_n, ff_bnd + prof0 * atn))

    return ffprime
