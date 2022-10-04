from typing import List, Tuple


def extrude_scale(
    points: List[Tuple[float, float]], distance: float
) -> List[Tuple[float, float]]:
    """
    Scale up shape defined by the given points. This preserves shape and so does not
    give a fixed distance from each point in the original boundary to the equivalent
    point in the new boundary.
    """

    centre = (0.0, 0.0)
    for point in points:
        centre = (centre[0] + point[0], centre[1] + point[1])

    count = float(len(points))
    centre = (centre[0] / count, centre[1] / count)

    extruded_points: List[Tuple[float, float]] = []
    for point in points:
        origin_vec = (point[0] - centre[0], point[1] - centre[1])

        extruded_points.append(
            (
                centre[0] + origin_vec[0] * (1.0 + distance),
                centre[1] + origin_vec[1] * (1.0 + distance),
            )
        )

    return extruded_points
