from typing import List, Tuple


def lerp(
    points: List[Tuple[float, float]], lower_idx: int, upper_idx: int, target_x: float
) -> float:
    """
    Calculates the linearly interpolated Y value for a given X target lying between a
    lower and upper bound.
    """

    lower = points[lower_idx]
    upper = points[upper_idx]

    grad = (upper[1] - lower[1]) / (upper[0] - lower[0])

    return lower[1] + grad * (target_x - lower[0])
