from typing import List, Tuple


def __linear_extrapolate(
    point_1: Tuple[float, float], point_2: Tuple[float, float], target: float
):
    grad = (point_1[1] - point_2[1]) / (point_1[0] - point_2[0])

    return point_2[1] + grad * (target - point_2[0])


def linear_extrapolate(points: List[Tuple[float, float]], target_x: float) -> float:
    """
    Calculates the linearly extrapolated Y value for a given X target.
    """

    if points[0][0] > target_x:
        return __linear_extrapolate(points[1], points[0], target_x)
    elif points[-1][0] < target_x:
        return __linear_extrapolate(points[-2], points[-1], target_x)
