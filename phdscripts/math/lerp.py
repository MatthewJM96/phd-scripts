from typing import Tuple


def lerp(
    lower: Tuple[float, float], upper: Tuple[float, float], target_x: float
) -> float:
    """
    Calculates the linearly interpolated Y value for a given X target lying between a
    lower and upper bound.
    """

    grad = (upper[1] - lower[1]) / (upper[0] - lower[0])

    return lower[1] + grad * (target_x - lower[0])
