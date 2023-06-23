from typing import Callable, List, Tuple, Union

from phdscripts.data import G_EQDSK

from .extrude_normal import extrude_normal
from .extrude_scale import extrude_scale


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

    if type(extrude_method) is str:
        if extrude_method == "scale":
            extruded_points = extrude_scale(boundary, extrusion)
        elif extrude_method == "normal":
            extruded_points = extrude_normal(boundary, extrusion)
        else:
            print("Invalid extrusion method:", extrude_method)
            return False, []
    else:
        extruded_points = extrude_method(boundary, extrusion)

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

    if type(extrude_method) is str:
        if extrude_method == "scale":
            extruded_points = extrude_scale(boundary, extrusion)
        elif extrude_method == "normal":
            extruded_points = extrude_normal(boundary, extrusion)
        else:
            print("Invalid extrusion method:", extrude_method)
            return False, []
    else:
        extruded_points = extrude_method(boundary, extrusion)

    RZpsis = []
    for point in extruded_points:
        if geqdsk.holds_point(point):
            return False, []

        RZpsis.append((point[0], point[1], geqdsk.psi_normalised_at(point)))

    return True, RZpsis
