import math
from typing import List, Tuple


def extrude_normal(
    points: List[Tuple[float, float]], distance: float
) -> List[Tuple[float, float]]:
    """
    Estimate normal vector of a point as the normal to the average gradient of that
    between a point and its neighbours. Extrude the list of points by the given distance
    based on these estimated normal vectors.
    """

    extruded_points: List[Tuple[float, float]] = []
    for i in range(len(points)):
        prior_point = points[i - 1]
        point = points[i]
        next_point = points[i + 1] if i + 1 < len(points) else points[0]

        prior_vec = (prior_point[0] - point[0], prior_point[1] - point[1])
        next_vec = (point[0] - next_point[0], point[1] - next_point[1])

        prior_len = math.sqrt(prior_vec[0] * prior_vec[0] + prior_vec[1] * prior_vec[1])
        next_len = math.sqrt(next_vec[0] * next_vec[0] + next_vec[1] * next_vec[1])

        prior_grad = (prior_vec[0] / prior_len, prior_vec[1] / prior_len)
        next_grad = (next_vec[0] / next_len, next_vec[1] / next_len)

        grad = (
            (prior_grad[0] + next_grad[0]) / 2.0,
            (prior_grad[1] + next_grad[1]) / 2.0,
        )

        grad_len = math.sqrt(grad[0] * grad[0] + grad[1] * grad[1])

        grad_normalised = (grad[0] / grad_len, grad[1] / grad_len)

        normal = (-grad_normalised[1], grad_normalised[0])

        extrusion = (normal[0] * distance, normal[1] * distance)

        extruded_points.append((point[0] + extrusion[0], point[1] + extrusion[1]))

    return extruded_points
