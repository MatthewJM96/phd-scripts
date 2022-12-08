import math
from typing import List, Tuple


def create_miller_boundary(
    num_points: int,
    R_centre: float,
    aspect_ratio: float,
    elongation: float,
    triangularity: float,
    quadrangularity: float = 0.0,
) -> List[Tuple[float, float]]:
    """
    Create a boundary shape using Miller parameterisation.
    """

    points: List[Tuple[float, float]] = []
    for i in range(num_points):
        theta = float(i) * 2.0 * math.pi / float(num_points)

        points.append(
            (
                R_centre
                + aspect_ratio
                * math.cos(
                    theta
                    + triangularity * math.sin(theta)
                    + quadrangularity * math.sin(2.0 * theta)
                ),
                aspect_ratio * elongation * math.sin(theta),
            )
        )

    return points
