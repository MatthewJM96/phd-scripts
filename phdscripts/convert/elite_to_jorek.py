from os.path import basename, isfile
from typing import Dict, List, Optional, Tuple

from phdscripts.boundary import decomp_fourier, extrude_normal, extrude_scale
from phdscripts.physical_constants import EV_TO_JOULES, MU_0


def __read_flux_metadata(lines: List[str]) -> Tuple[bool, int, int]:
    """
    Reads the flux metadata from the given Elite input lines. This metadata is assumed
    to be two integers, the first the number of flux surfaces and the second the number
    of points on each flux surface.
    """

    metadata = lines[1].split()

    # If metadata line wasn't made of two non-whitespace things,
    # it is definitely formatted wrong.
    if len(metadata) != 2:
        return (False, 0, 0)

    metadata[0] = metadata[0].strip()
    metadata[1] = metadata[1].strip()

    # If the two elements aren't each simple integers, then
    # metadata is formatted wrong.
    if not metadata[0].isdigit() or not metadata[1].isdigit():
        return (False, 0, 0)

    return (True, int(metadata[0]), int(metadata[1]))


def __extract_per_flux_profile(
    lines: List[str], param: str, flux_surface_count: int
) -> Tuple[bool, List[float]]:
    """
    Extracts the named parameter from the provided Elite input lines. The assumption is
    that the Elite input file has the parameter provided as a block where each value in
    the block is the value of that parameter on a given flux surface.
    """

    values: List[float] = []

    found_start = False
    for line in lines:
        # If we have found the start of the values for this parameter,
        # then handle ingestion.
        if found_start:
            # If we have ingested all the values, break.
            if len(values) == flux_surface_count:
                break
            # Get values on this line.
            values_str = line.split()
            for value_str in values_str:
                # For each value on line, try to convert to a float, if we
                # can't then input file is ill-formatted.
                try:
                    values.append(float(value_str.strip()))
                except ValueError:
                    return (False, [])
        # If we haven't yet found the start of the values for this parameter,
        # check if we have encountered the start.
        elif line.strip() == param:
            found_start = True

    # If we don't have flux_surface_count number of
    # values, then te input file was ill-formatted, return
    # failure.
    if len(values) != flux_surface_count:
        return False, values

    return True, values


def __extract_per_point_profile(
    lines: List[str],
    param: str,
    flux_surface_target: int,
    flux_surface_count: int,
    flux_surface_point_count: int,
) -> Tuple[bool, List[float]]:
    """
    Extracts the named parameter from the provided Elite input lines. The assumption is
    that the Elite input file has the parameter provided in blocks where each block is
    given as a point in terms of some parameter (usually poloidal angle) and each value
    in a block is the value of that point on one of the flux surfaces.
    """

    values: List[float] = []

    flux_cursor = 0
    point_values: List[float] = [None] * flux_surface_count

    # In this function, we iterate over lines to get values, where the values
    # are stored in blocks all for the same point (say in terms of poloidal
    # angle), where there are flux_surface_count number of values in each block.
    #   Each value in these blocks corresponds to one of the flux surfaces, with
    #   values going in order from central flux to edge flux surfaces.
    found_start = False
    for line in lines:
        # If we have found the start of the values for this parameter,
        # then handle ingestion.
        if found_start:
            # If we have flux cursor equal to flux target, then we can
            # retrieve the value for the point on the target flux surface.
            if flux_cursor >= flux_surface_target:
                values.append(point_values[flux_cursor - 1])
            # If we have hit end of flux surfaces for this point, wrap flux
            # cursor.
            if flux_cursor == flux_surface_count:
                flux_cursor -= flux_surface_target
            # If we have ingested all the values, break.
            if len(values) == flux_surface_point_count:
                break
            # Get values on this line.
            values_str = line.split()
            for value_str in values_str:
                # For each value on line, try to convert to a float, if we
                # can't then input file is ill-formatted.
                try:
                    point_values[flux_cursor] = float(value_str.strip())
                except ValueError:
                    return (False, [])
                # Increment flux cursor.
                flux_cursor += 1
        # If we haven't yet found the start of the values for this parameter,
        # check if we have encountered the start.
        elif line.strip() == param:
            found_start = True

    # If we don't have flux_surface_point_count number of
    # values, then te input file was ill-formatted, return
    # failure.
    if len(values) != flux_surface_point_count:
        return False, values

    return True, values


def __parse_elite_input(elite_filepath: str) -> Tuple[bool, Dict[str, List[float]]]:
    """
    Parses the named elite inpuit, extracting the parameters needed to construct a
    JOREK namelist from.
    """

    if not isfile(elite_filepath):
        print("    File does not exist!")
        return False, {}

    elite_lines = []
    with open(elite_filepath, "r") as elite_file:
        elite_lines = elite_file.readlines()

    if elite_lines is None or elite_lines == "":
        print(f"Elite input file at:\n    {elite_filepath}\nis empty!")
        return False, {}

    # Read number of flux surfaces and number of points on each flux surface.
    success, flux_surface_count, flux_surface_point_count = __read_flux_metadata(
        elite_lines
    )
    if not success:
        print(
            (
                "    Could not read flux metadata from elite input.\n"
                "        Expect to see two integers on the second line giving number\n"
                "        of flux surfaces and number of points on each flux surface\n"
                "        respectively."
            )
        )
        return False, {}

    PER_FLUX_PARAMS = ["psi", "ffprime", "q", "ne", "Te", "f(psi)"]
    PER_POINT_BOUNDARY_PARAMS = ["R", "Z"]

    params: Dict[str, List[float]] = {}

    for param in PER_FLUX_PARAMS:
        success, values = __extract_per_flux_profile(
            elite_lines, param, flux_surface_count
        )

        if not success:
            print(f"    Could not parse parameter, {param}.")
            return False, {}

        params[param] = values

    for param in PER_POINT_BOUNDARY_PARAMS:
        # Only want the boundary information for these parameters, and they have
        # per point, per flux surface values so need special parsing.
        success, values = __extract_per_point_profile(
            elite_lines,
            param,
            flux_surface_count,
            flux_surface_count,
            flux_surface_point_count,
        )

        if not success:
            print(f"    Could not parse parameter, {param}.")
            return False, {}

        params[param] = values

    return True, params


def __normalise_psi(psis: List[float]) -> List[float]:
    """
    Normalises the given flux surface values, it is assumed that these values are sorted
    with psis[0] being on-axis flux and psis[-1] being edge flux.
    """

    normalised_psi: List[float] = []

    psi_axis = psis[0]
    psi_edge = psis[-1]
    for psi in psis:
        normalised_psi.append((psi - psi_axis) / (psi_edge - psi_axis))

    return normalised_psi


def __psi(parameters: Dict[str, List[float]]) -> List[float]:
    """
    Obtain normalised psi values from Elite input.

    Really just here to have a consistent API.
    """

    return __normalise_psi(parameters["psi"])


def __F0(parameters: Dict[str, List[float]]) -> List[float]:
    """
    Obtain F value on-axis.
    """

    return parameters["f(psi)"][0]


def __ffprime(parameters: Dict[str, List[float]]) -> Tuple[bool, List[float]]:
    """
    Obtain negated ffprime values from Elite input.
    """

    expected_value_count = len(parameters["psi"])
    if expected_value_count != len(parameters["ffprime"]):
        return False, []

    return True, [-val for val in parameters["ffprime"]]


def __q_profile(parameters: Dict[str, List[float]]) -> Tuple[bool, List[float]]:
    """
    Obtain negated q-profile values from Elite input.
    """

    expected_value_count = len(parameters["psi"])
    if expected_value_count != len(parameters["q"]):
        return False, []

    return True, [-val for val in parameters["q"]]


def __density(parameters: Dict[str, List[float]]) -> Tuple[bool, float, List[float]]:
    """
    Obtain central density and normalised density values from Elite input.
    """

    expected_value_count = len(parameters["psi"])
    if expected_value_count != len(parameters["ne"]):
        return False, 0.0, []

    # JOREK parameterises density as a profile normalised against on-axis density and
    # takes a central density value as on-axis density divided by 1e20.
    central_density = parameters["ne"][0] / 1.0e20

    return (
        True,
        central_density,
        [val / parameters["ne"][0] for val in parameters["ne"]],
    )


def __temperature(
    parameters: Dict[str, List[float]], central_density: float
) -> Tuple[bool, List[float]]:
    """
    Obtain normalised temperature values from Elite input.
    """

    expected_value_count = len(parameters["psi"])
    if expected_value_count != len(parameters["Te"]):
        return False, []

    # JOREK wants temperature normalised.
    temp_norm_factor = 2.0 * central_density * 1.0e20 * MU_0 * EV_TO_JOULES

    return True, [val * temp_norm_factor for val in parameters["Te"]]


def __write_profile(profile: List[List[float]], filepath: str) -> bool:
    for idx in range(1, len(profile)):
        if len(profile[idx]) != len(profile[0]):
            return False

    with open(filepath, "w") as profile_file:
        for idx in range(len(profile[0])):
            for component in profile:
                profile_file.write(f"{component[idx]} ")
            profile_file.write("\n")

    return True


def __write_jorek_namelist(
    jorek_filepath: str,
    density_filepath: str,
    temperature_filepath: str,
    ffprime_filepath: str,
    rz_boundary_filepath: str,
    parameters: Dict[str, List[float]],
) -> bool:
    """
    Writes a JOREK namelist file based on the provided values for the various parameters
    obtained from an Elite input file. Of course no requirement is placed on these
    parameters of actually coming from an Elite input file, but they must follow Elite
    conventions and normalisations.
    """

    REQUIRED_PARAMETERS = set({"psi", "ffprime", "q", "ne", "Te", "f(psi)", "R", "Z"})
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

    # Get normalised psi values along flux surfaces.
    psi = __psi(parameters)

    # Get F0.
    F0 = __F0(parameters)

    # Get ffprime, JOREK requires these to be negated.
    success, ffprime_profile = __ffprime(parameters)
    if not success:
        print("    FFprime values provided not converted succsesfully.")
        return False

    # For now we aren't using this, really only useful as a diagnostic.
    # # Get q-profile, JOREK requires these to be negated.
    # success, q_profile = __q_profile(parameters)
    # if not success:
    #     print("    q-profile values provided not converted succsesfully.")

    # Get central density and density profile.
    success, central_density, density_profile = __density(parameters)
    if not success:
        print("    Density values provided not converted succsesfully.")
        return False

    # Get temperatures.
    success, temperature_profile = __temperature(parameters, central_density)
    if not success:
        print("    Temperature values provided not converted succsesfully.")
        return False

    r_boundary = parameters["R"]
    z_boundary = parameters["Z"]
    if len(r_boundary) != len(z_boundary):
        print("    Number of obtained R and Z boundary values are different.")
        return False

    n_boundary = len(r_boundary)
    r_geo = (min(r_boundary) + max(r_boundary)) / 2.0
    z_geo = (min(z_boundary) + max(z_boundary)) / 2.0

    # Write profiles to their files.
    #   Density
    success = __write_profile([psi, density_profile], density_filepath)
    #   Temperature
    success = success and __write_profile(
        [psi, temperature_profile], temperature_filepath
    )
    #   FFprime
    success = success and __write_profile([psi, ffprime_profile], ffprime_filepath)
    #   R-Z
    success = success and __write_profile(
        [r_boundary, z_boundary, [psi[-1]] * len(r_boundary)], rz_boundary_filepath
    )
    if not success:
        print("    Could not write one of the profiles.")
        return False

    contents = (
        "&in1\n"
        "  restart = .f.\n"
        "  regrid  = .f.\n"
        "\n"
        "  tstep_n   = 5.\n"
        "  nstep_n   = 0\n"
        "\n"
        "  !tstep_n   = 5.\n"
        "  !nstep_n   = 100\n"
        "\n"
        "  freeboundary = .t.\n"
        "  wall_resistivity_fact = 1.\n"
        "\n"
        "  linear_run = .t.\n"
        "\n"
        "  nout = 4\n"
        "\n"
        "  fbnd(1)   = 2.\n"
        "  fbnd(2:4) = 0.\n"
        "  mf        = 0\n"
        "\n"
        f"  n_boundary = {n_boundary}\n"
        f'  R_Z_psi_bnd_file = "{basename(rz_boundary_filepath)}"\n'
        "\n"
        f"  R_geo = {r_geo}\n"
        f"  Z_geo = {z_geo}\n"
        "\n"
        "  amin = 1.0\n"
        "\n"
        f"  F0 = {F0}\n"
        "\n"
        f"  central_density = {central_density}\n"
        f'  rho_file = "{basename(density_filepath)}"\n'
        f'  T_file   = "{basename(temperature_filepath)}"\n'
        f'  ffprime_file = "{basename(ffprime_filepath)}"\n'
        "\n"
        "  fix_axis_nodes = .t.\n"
        "  axis_srch_radius = 2.0\n"
        "\n"
        "  n_radial = 60 !240 !210 !130\n"
        "  n_pol    = 60 !205 !180 !110\n"
        "\n"
        "  n_flux   = 35 !120 !90 !55\n"
        "  n_tht    = 55 !160 !125 !80\n"
        "\n"
        "  visco_T_dependent = .f.\n"
        "\n"
        "  eta   = 1.d-8\n"
        "  visco = 1.d-10\n"
        "  visco_par = 1.d-10\n"
        "  eta_num = 0.d0\n"
        "  visco_num = 0.d0\n"
        "\n"
        "  D_par  = 0.d0\n"
        "  D_perp = 1.d-10\n"
        "  ZK_par  = 0.d0\n"
        "  ZK_perp = 1.d-10\n"
        "\n"
        "  heatsource     = 0.d0\n"
        "  particlesource = 0.d0\n"
        "/\n"
    )

    with open(jorek_filepath, "w") as jorek_file:
        jorek_file.write(contents)

    return True


def __write_starwall_namelist(
    starwall_filepath: str,
    modes: Tuple[int, int],
    wall_distance: float,
    extrude_method: str,
    parameters: Dict[str, List[float]],
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

    fourier_coeffs = decomp_fourier(extruded_points, modes)

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

    with open(starwall_filepath, "w") as starwall_file:
        starwall_file.write(contents)

    return True


def convert_elite_to_jorek(
    elite_filepath: str,
    jorek_filepath: str,
    starwall_filepath: Optional[str] = None,
    starwall_modes: Tuple[int, int] = (-1, 1),
    wall_distance: float = 0.0,
    extrude_method: str = "scale",
    density_filepath: str = "density.txt",
    temperature_filepath: str = "temperature.txt",
    ffprime_filepath: str = "ffprime.txt",
    rz_boundary_filepath: str = "rz_boundary.txt",
) -> None:
    print(("Parsing Elite input file:\n" f"    {elite_filepath}\n"))

    success, elite_params = __parse_elite_input(elite_filepath)
    if not success:
        print("Failed to parse the file, reason above.")
        return

    print(
        (
            "Succesfully parsed Elite input.\n"
            "\nWriting JOREK namelist to:\n"
            f"    {jorek_filepath}\n"
        )
    )

    success = __write_jorek_namelist(
        jorek_filepath,
        density_filepath,
        temperature_filepath,
        ffprime_filepath,
        rz_boundary_filepath,
        elite_params,
    )
    if not success:
        print("Failed to write JOREK namelist, reason above.")
        return

    print("Successfully written JOREK namelist.")

    if starwall_filepath is not None:
        print("Writing STARWALL namelist.")

        success = __write_starwall_namelist(
            starwall_filepath,
            starwall_modes,
            wall_distance,
            extrude_method,
            elite_params,
        )

        print("Successfully written STARWALL namelist.")
