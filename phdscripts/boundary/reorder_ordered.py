from typing import List, Tuple


def reorder_ordered_boundary(
    boundary: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """
    Reorders some arbitrary winding direction and starting point of ordered boundary to
    be wound counter-clockwise and starting at the outboard side.
    """

    # Find the two minima in Z.

    Z_minima_found = 0
    Z_minimum_idx_1 = 0
    Z_minimum_idx_2 = 0

    current_idx = 0

    last_point_2 = boundary[-1]
    last_point = boundary[0]
    for point in boundary[1:]:
        if (last_point_2[1] < 0.0 and point[1] > 0.0) or (
            last_point_2[1] > 0.0 and point[1] < 0.0
        ):
            if Z_minima_found == 0:
                Z_minimum_idx_1 = current_idx
                Z_minima_found += 1
            elif Z_minima_found == 1:
                Z_minimum_idx_2 = current_idx
                Z_minima_found += 1
                break
            else:
                print("Tried to find a third minimum!")

        last_point_2 = last_point
        last_point = point
        current_idx += 1

    # We want the minimum with largest R.

    Z_minimum_idx = 0
    if boundary[Z_minimum_idx_1][0] > boundary[Z_minimum_idx_2][0]:
        Z_minimum_idx = Z_minimum_idx_1
    else:
        Z_minimum_idx = Z_minimum_idx_2

    # Now we figure which way to wind and construct our new list.

    new_boundary: List[Tuple[float, float]] = [] * len(boundary)

    if boundary[Z_minimum_idx + 1][1] > 0:
        # We have counter-clockwise winding occurring forwards in the list of points.
        new_boundary.extend(boundary[Z_minimum_idx:])
        new_boundary.extend(boundary[0:Z_minimum_idx])
    else:
        # We have counter-clockwise winding occurring backwards in the list of points.
        for offset in range(Z_minimum_idx + 1):
            new_boundary.append(boundary[Z_minimum_idx - offset])

        for offset in range(len(boundary) - Z_minimum_idx):
            new_boundary.append(boundary[len(boundary) - offset - 1])

    return new_boundary
