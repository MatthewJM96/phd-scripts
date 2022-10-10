import math
from typing import Dict, List, Tuple


def decomp_fourier(
    points: List[Tuple[float, float]], modes: Tuple[int, int]
) -> Dict[int, Tuple[float, float, float, float]]:
    """
    Convert a boundary given as a list of points and convert it into a set of cosine and
    sine modes suitable for ingestion by STARWALL.

    For each mode, coefficients are given in order:
        ( R cos-mode, R sin-mode, Z cos-mode, Z sin-mode ).
    """

    coefficients: Dict[int, Tuple[float, float, float, float]] = {}

    N = float(len(points))
    freq = 1.0 / N

    for mode in range(modes[0], modes[1] + 1):
        coefficients[mode] = (0.0, 0.0, 0.0, 0.0)
        for idx in range(len(points)):
            arg = 2 * math.pi * freq * float(idx) * float(mode)

            coefficients[mode] = (
                coefficients[mode][0] + points[idx][0] * math.cos(arg),
                coefficients[mode][1] + points[idx][0] * math.sin(arg),
                coefficients[mode][2] + points[idx][1] * math.cos(arg),
                coefficients[mode][3] + points[idx][1] * math.sin(arg),
            )

    for mode, coeffs in coefficients.items():
        coefficients[mode] = (
            coeffs[0] / N,
            coeffs[1] / N,
            coeffs[2] / N,
            coeffs[3] / N,
        )

    return coefficients


def create_fourier_boundary(
    coefficients: Dict[int, Tuple[float, float, float, float]], N: int
) -> List[Tuple[float, float]]:
    points: List[Tuple[float, float]] = []

    freq = 1.0 / float(N)

    for idx in range(N):
        x = 0.0
        y = 0.0
        for mode, coeffs in coefficients.items():
            arg = 2 * math.pi * freq * float(idx) * float(mode)

            x += coeffs[0] * math.cos(arg) + coeffs[1] * math.sin(arg)
            y += coeffs[2] * math.cos(arg) + coeffs[3] * math.sin(arg)

        points.append((x, y))

    return points
