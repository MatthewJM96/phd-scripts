import math
from typing import List, Tuple


def create_freidberg_cerfon_boundary(
    num_points: int,
    R_centre: float,
    aspect_ratio: float,
    elongation: float,
    triangularity: float,
) -> List[Tuple[float, float]]:
    """
    Create a boundary shape according to the Friedberg-Cerfon paper:
        https://aip.scitation.org/doi/pdf/10.1063/1.3328818
    """

    points: List[Tuple[float, float]] = []
    for i in range(num_points):
        theta = float(i) * 2.0 * math.pi / float(num_points)

        points.append(
            (
                R_centre
                + aspect_ratio
                * math.cos(theta + math.asin(triangularity) * math.sin(theta)),
                aspect_ratio * elongation * math.sin(theta),
            )
        )

    return points
