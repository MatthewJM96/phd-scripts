from os.path import exists
from typing import List, Tuple

from phdscripts.boundary import decomp_fourier_2d, extrude
from phdscripts.util import replace_fortran_parameter


def _read_extrude_from(filepath: str) -> List[Tuple[float, float]]:
    extrude_from = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            parts = line.split()
            extrude_from.append((float(parts[0]), float(parts[1])))
    return extrude_from


def _read_rz_psi(filepath: str) -> List[Tuple[float, float, float]]:
    rz_psi = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            parts = line.split()
            rz_psi.append((float(parts[0]), float(parts[1]), float(parts[2])))
    return rz_psi


def _calculate_wall_geometry(extrude_from_filepath: str, rz_psi_filepath: str, params: dict) -> None:
    """
    Calculate wall geometry in STARWALL parameterisation by taking one of two boundaries
    (extrude_from first, and the rz_psi boundary file of JOREK if the former does not
    exist), and extruding according to a parameterised wall distance.

    NOTE: this currently only supports axisymmetric cases and enforces reordering of
          poloidal modes in STARWALL's parameterisation to be monotonically increasing
          from lowest to highest mode.
    NOTE: this currently only supports numerical boundaries, and not the shaping
          parameters otherwise used by JOREK.
    """

    # Determine what wall scaling is desired.

    wall_distance = params["wall_distance"]
    method = "scale"

    if "wall_extrude_method" in params.keys():
        method = params["wall_extrude_method"]

    # Obtain lowest and highest poloidal modes if they have been provided, capping them
    # as needed, otherwise default to the most poloidal modes STARWALL supports.

    lowest_mode = 999
    highest_mode = -999
    if "m_w" in params.keys():
        for m in params["m_w"]:
            if m < 0 and m < lowest_mode:
                lowest_mode = m
            if m > 0 and m > highest_mode:
                highest_mode = m
    else:
        lowest_mode = -99
        highest_mode = 99

    lowest_mode = max(-99, lowest_mode)
    highest_mode = min(99, highest_mode)

    params["mn_w"] = abs(lowest_mode) + highest_mode + 1
    params["m_w"] = [x for x in range(lowest_mode, highest_mode + 1, 1)]
    params["n_w"] = [0 for _ in range(lowest_mode, highest_mode + 1, 1)]

    # Read extrude_from date file, or else rz_boundary.txt, or else JOREK namelist
    # geometry parameters.

    boundary = []

    if exists(extrude_from_filepath):
        boundary = _read_extrude_from(extrude_from_filepath)
    elif exists(rz_psi_filepath):
        # Drop psi information.
        boundary = [(x[0], x[1]) for x in _read_rz_psi(rz_psi_filepath)]
    else:
        print(
            (
                "Trying to prepare a case with extruded wall, but no boundary"
                " provided to extrude from."
            )
        )

    # Perform extrusion and decomposition into Fourier terms, storing those back into
    # the parameters dict.

    wall_boundary = extrude(method, boundary, wall_distance - 1.0)

    coeffs = decomp_fourier_2d(wall_boundary, (lowest_mode, highest_mode))

    params["rc_w"] = [ coeffs[idx][0] for idx in range(lowest_mode, highest_mode + 1, 1) ]
    params["rs_w"] = [ coeffs[idx][1] for idx in range(lowest_mode, highest_mode + 1, 1) ]
    params["zc_w"] = [ coeffs[idx][2] for idx in range(lowest_mode, highest_mode + 1, 1) ]
    params["zs_w"] = [ coeffs[idx][3] for idx in range(lowest_mode, highest_mode + 1, 1) ]


def update_starwall_input_file(starwall_filepath: str, extrude_from_filepath: str, rz_psi_filepath: str, params: dict) -> None:
    """
    Updates STARWALL input file with parameters provided to this function, in the
    case that a wall distance is supplied, extrusion is performed first.
    """

    if "wall_distance" in params.keys():
        _calculate_wall_geometry(extrude_from_filepath, rz_psi_filepath, params)

    with open(starwall_filepath, "r") as f:
        starwall_input = f.read()

    for param, value in params.items():
        # TODO(Matthew): this doesn't handle cases where a parameter has not been placed
        #                in the STARWALL input file already, we may want to handle that
        #                explicitly (i.e. closing "/" line).
        starwall_input = replace_fortran_parameter(value, param, starwall_input)

    with open(starwall_filepath, "w") as f:
        f.write(starwall_input)
