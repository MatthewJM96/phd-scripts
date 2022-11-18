from os.path import join
from typing import Dict, List, Tuple

from phdscripts.boundary import decomp_fourier_2d, extrude_normal, extrude_scale


def write_starwall_files(
    parameters: Dict[str, List[float]],
    modes: Tuple[int, int],
    wall_distance: float,
    extrude_method: str,
    target_directory: str,
    starwall_filepath: str = "starwall_namelist",
) -> bool:
    """
    Writes a STARWALL namelist file based on the provided values for the various
    parameters obtained from an Elite input file. Of course no requirement is placed on
    these parameters of actually coming from an Elite input file, but they must follow
    Elite conventions and normalisations.
    """

    REQUIRED_PARAMETERS = set({"R", "Z"})
    keys = set(parameters.keys())
    if REQUIRED_PARAMETERS > keys:
        print(
            (
                "    Parameters provided do not at least include the required"
                "parameters.\n"
                f"        Parameters provided were: {keys}\n"
                f"        Parameters required are: {REQUIRED_PARAMETERS}\n"
            )
        )
        return False

    if len(parameters["R"]) != len(parameters["Z"]):
        print("    Number of obtained R and Z boundary values are different.")
        return False

    points: List[Tuple[float, float]] = []
    for idx in range(len(parameters["R"])):
        points.append((parameters["R"][idx], parameters["Z"][idx]))

    extruded_points = points
    if wall_distance != 0.0:
        if extrude_method == "scale":
            extruded_points = extrude_scale(points, wall_distance)
        elif extrude_method == "normal":
            extruded_points = extrude_normal(points, wall_distance)
        else:
            print(
                (
                    f"    Wall extrusion method was not recognised: {extrude_method}.\n"
                    "        Methods accepted are:\n"
                    "            - scale\n"
                    "            - normal\n"
                )
            )
            return False

    fourier_coeffs = decomp_fourier_2d(extruded_points, modes)

    n_w_str = ""
    m_w_str = ""
    rc_w_str = ""
    rs_w_str = ""
    zc_w_str = ""
    zs_w_str = ""
    for mode, coeffs in fourier_coeffs.items():
        n_w_str += "0 "
        m_w_str += f"{mode} "
        rc_w_str += f"{coeffs[0]} "
        rs_w_str += f"{coeffs[1]} "
        zc_w_str += f"{coeffs[2]} "
        zs_w_str += f"{coeffs[3]} "

    contents = (
        "&PARAMS\n"
        "  i_response = 2\n"
        "  n_harm     = 1\n"
        "  n_tor      = 1\n"
        "  nv         = 40\n"
        "  delta      = 0.001\n"
        "  n_points   = 14\n"
        "  nwall      = 1\n"
        "  iwall      = 1\n"
        "/\n"
        "\n"
        "&PARAMS_WALL\n"
        "  eta_thin_w = 1.d-4\n"
        "  nwu        = 32\n"
        "  nwv        = 32\n"
        f"  mn_w       = {len(fourier_coeffs.keys())}\n"
        f"  n_w        = {n_w_str}\n"
        f"  m_w        = {m_w_str}\n"
        f"  rc_w       = {rc_w_str}\n"
        f"  rs_w       = {rs_w_str}\n"
        f"  zc_w       = {zc_w_str}\n"
        f"  zs_w       = {zs_w_str}\n"
        "/\n"
    )

    with open(join(target_directory, starwall_filepath), "w") as starwall_file:
        starwall_file.write(contents)

    return True
