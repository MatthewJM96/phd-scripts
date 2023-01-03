from typing import List, Optional, Tuple


def linear_interpolate(
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


def linear_interpolate_lines(
    lines: List[Tuple[List[float], float]]
) -> Optional[List[Tuple[float, float]]]:
    """
    Calculates a linear interpolation of a collection of lines using arbitrarily
    normalised weights to determine each line's contribution.
    """

    # Assure all lines are of same length.
    first_line_length = len(lines[0][0])
    for line in lines:
        if len(line[0]) != first_line_length:
            return None

    # Calculate total weight.
    total_weight = 0.0
    for line in lines:
        total_weight += line[1]

    # Allocate new line
    new_line = [0.0] * first_line_length

    # Add contributions of all lines.
    for line in lines:
        for idx in range(first_line_length):
            new_line[idx] += line[0][idx] * line[1] / total_weight

    return new_line
