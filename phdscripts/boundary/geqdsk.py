from typing import Callable, List, Tuple, Union

from phdscripts.data import G_EQDSK

from .extrude import extrude


def get_psi_for_boundary(
    geqdsk: G_EQDSK, boundary: List[Tuple[float, float]]
) -> Tuple[bool, List[float]]:
    """
    Obtains psi values for a given set of points in a G EQDSK equilibrium.
    """

    psis = []
    for point in boundary:
        if geqdsk.holds_point(point):
            return False, []

        psis.append(geqdsk.psi_at(point))

    return True, psis


def get_normalised_psi_for_boundary(
    geqdsk: G_EQDSK, boundary: List[Tuple[float, float]]
) -> Tuple[bool, List[float]]:
    """
    Obtains psi values for a given set of points in a G EQDSK equilibrium.
    """

    psis = []
    for point in boundary:
        if geqdsk.holds_point(point):
            return False, []

        psis.append(geqdsk.psi_normalised_at(point))

    return True, psis


def get_psi_for_extruded_boundary(
    geqdsk: G_EQDSK,
    boundary: List[Tuple[float, float]],
    extrusion: float,
    extrude_method: Union[str, Callable],
) -> Tuple[bool, List[Tuple[float, float, float]]]:
    """
    Obtains psi values for a given set of points in a G EQDSK equilibrium.
    """

    if len(boundary) == 0:
        return False, []

    extruded_points = extrude(extrude_method, boundary, extrusion)
    if len(extruded_points) == 0:
        print("Invalid extrusion method:", extrude_method)
        return False, []

    RZpsis = []
    for point in extruded_points:
        if geqdsk.holds_point(point):
            return False, []

        RZpsis.append((point[0], point[1], geqdsk.psi_at(point)))

    return True, RZpsis


def get_normalised_psi_for_extruded_boundary(
    geqdsk: G_EQDSK,
    boundary: List[Tuple[float, float]],
    extrusion: float,
    extrude_method: Union[str, Callable],
) -> Tuple[bool, List[Tuple[float, float, float]]]:
    """
    Obtains psi values for a given set of points in a G EQDSK equilibrium.
    """

    if len(boundary) == 0:
        return False, []

    extruded_points = extrude(extrude_method, boundary, extrusion)
    if len(extruded_points) == 0:
        print("Invalid extrusion method:", extrude_method)
        return False, []

    RZpsis = []
    for point in extruded_points:
        if geqdsk.holds_point(point):
            return False, []

        RZpsis.append((point[0], point[1], geqdsk.psi_normalised_at(point)))

    return True, RZpsis
