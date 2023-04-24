from typing import List, Tuple


def extrude_scale(
    points: List[Tuple[float, float]],
    distance: float,
    weighted_centre: bool = True,
    scale_pow: float = 1.0,
) -> List[Tuple[float, float]]:
    """
    Scale up shape defined by the given points. This preserves shape and so does not
    give a fixed distance from each point in the original boundary to the equivalent
    point in the new boundary.
    """

    centre = (0.0, 0.0)

    if weighted_centre:
        for point in points:
            centre = (centre[0] + point[0], centre[1] + point[1])

        count = float(len(points))
        centre = (centre[0] / count, centre[1] / count)
    else:
        R_min = 9999.0
        R_max = 0.0
        Z_min = 9999.0
        Z_max = 0.0
        for point in points:
            if point[0] < R_min:
                R_min = point[0]
            elif point[0] > R_max:
                R_max = point[0]
            if point[1] < Z_min:
                Z_min = point[1]
            elif point[1] > Z_max:
                Z_max = point[1]
        centre = ((R_min + R_max) / 2.0, (Z_min + Z_max) / 2.0)

    return extrude_scale_from_centre(points, distance, centre, scale_pow)


def extrude_scale_from_centre(
    points: List[Tuple[float, float]],
    distance: float,
    centre: Tuple[float, float],
    scale_pow: float = 1.0,
) -> List[Tuple[float, float]]:
    """
    Scale up shape defined by the given points and a specified centre point.
    """

    extruded_points: List[Tuple[float, float]] = []
    for point in points:
        print(point)
        origin_vec = (point[0] - centre[0], point[1] - centre[1])

        print(origin_vec)

        extruded_pt_x = centre[0] + origin_vec[0]
        if origin_vec[0] * distance >= 0.0:
            extruded_pt_x += pow(abs(origin_vec[0] * distance), scale_pow)
        else:
            extruded_pt_x -= pow(abs(origin_vec[0] * distance), scale_pow)

        extruded_pt_y = centre[1] + origin_vec[1]
        if origin_vec[1] * distance >= 0.0:
            extruded_pt_y += pow(abs(origin_vec[1] * distance), scale_pow)
        else:
            extruded_pt_y -= pow(abs(origin_vec[1] * distance), scale_pow)

        extruded_points.append((extruded_pt_x, extruded_pt_y))

        print(extruded_points[-1])

    return extruded_points
