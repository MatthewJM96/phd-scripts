from functools import partial
from typing import Callable, Dict, List, Optional, Tuple

from phdscripts.input.reader import (
    extract_from_elite_input,
    extract_from_helena_elite_input,
    extract_from_scene_elite_input,
)
from phdscripts.input.writer import write_jorek_files, write_starwall_files
from phdscripts.physical_constants import EV_TO_JOULES, MU_0


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
    # TODO(Matthew): does JOREK treat density as density of electorns and ions
    #                collectively as it does for temperature? This seems unlikely, but
    #                worth checking.
    # central_density = 2.0 * parameters["ne"][0] / 1.0e20
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


def __convert_elite_to_jorek(
    elite_filepath: str,
    extractor: Callable,
    target_directory: str,
    jorek_filepath: str = "jorek_namelist",
    density_filepath: str = "density.txt",
    temperature_filepath: str = "temperature.txt",
    ffprime_filepath: str = "ffprime.txt",
    rz_boundary_filepath: str = "rz_boundary.txt",
    starwall_filepath: Optional[str] = None,
    starwall_modes: Tuple[int, int] = (-1, 1),
    wall_distance: float = 0.0,
    extrude_method: str = "scale",
) -> None:
    print(("Parsing Elite input file:\n" f"    {elite_filepath}\n"))

    success, elite_params = extractor(elite_filepath)
    if not success:
        print("Failed to parse the file, reason above.")
        return

    print(("Succesfully parsed Elite input.\n" "\nNormalising parameters for JOREK.\n"))

    # Get normalised psi values along flux surfaces.
    elite_params["psi"] = __psi(elite_params)

    # Get ffprime, JOREK requires these to be negated.
    success, elite_params["ffprime"] = __ffprime(elite_params)
    if not success:
        print("    FFprime values provided not converted succsesfully.")
        return False

    # Get q-profile, JOREK requires these to be negated.
    success, elite_params["q"] = __q_profile(elite_params)
    if not success:
        print("    q-profile values provided not converted succsesfully.")

    # Get central density and density profile.
    success, elite_params["central_density"], elite_params["n"] = __density(
        elite_params
    )
    if not success:
        print("    Density values provided not converted succsesfully.")
        return False

    # Get temperatures.
    success, elite_params["T"] = __temperature(
        elite_params, elite_params["central_density"]
    )
    if not success:
        print("    Temperature values provided not converted succsesfully.")
        return False

    print(
        (
            "Succesfully normalised Elite input.\n"
            "\nWriting JOREK namelist to:\n"
            f"    {jorek_filepath}\n"
        )
    )

    success = write_jorek_files(
        elite_params,
        target_directory,
        jorek_filepath,
        density_filepath,
        temperature_filepath,
        ffprime_filepath,
        rz_boundary_filepath,
    )
    if not success:
        print("Failed to write JOREK namelist, reason above.")
        return

    print("Successfully written JOREK namelist.")

    if starwall_filepath is not None:
        print("Writing STARWALL namelist.")

        success = write_starwall_files(
            elite_params,
            starwall_modes,
            wall_distance,
            extrude_method,
            target_directory,
            starwall_filepath,
        )

        print("Successfully written STARWALL namelist.")


def convert_elite_to_jorek(
    elite_filepath: str,
    per_flux_params: Dict[str, str],
    per_point_params: Dict[str, str],
    target_directory: str,
    jorek_filepath: str = "jorek_namelist",
    density_filepath: str = "density.txt",
    temperature_filepath: str = "temperature.txt",
    ffprime_filepath: str = "ffprime.txt",
    rz_boundary_filepath: str = "rz_boundary.txt",
    starwall_filepath: Optional[str] = None,
    starwall_modes: Tuple[int, int] = (-1, 1),
    wall_distance: float = 0.0,
    extrude_method: str = "scale",
) -> None:
    __convert_elite_to_jorek(
        elite_filepath,
        partial(
            extract_from_elite_input,
            per_flux_params=per_flux_params,
            per_point_params=per_point_params,
        ),
        target_directory,
        jorek_filepath,
        density_filepath,
        temperature_filepath,
        ffprime_filepath,
        rz_boundary_filepath,
        starwall_filepath,
        starwall_modes,
        wall_distance,
        extrude_method,
    )


def convert_helena_elite_to_jorek(
    elite_filepath: str,
    target_directory: str,
    jorek_filepath: str = "jorek_namelist",
    density_filepath: str = "density.txt",
    temperature_filepath: str = "temperature.txt",
    ffprime_filepath: str = "ffprime.txt",
    rz_boundary_filepath: str = "rz_boundary.txt",
    starwall_filepath: Optional[str] = None,
    starwall_modes: Tuple[int, int] = (-1, 1),
    wall_distance: float = 0.0,
    extrude_method: str = "scale",
) -> None:
    __convert_elite_to_jorek(
        elite_filepath,
        extract_from_helena_elite_input,
        target_directory,
        jorek_filepath,
        density_filepath,
        temperature_filepath,
        ffprime_filepath,
        rz_boundary_filepath,
        starwall_filepath,
        starwall_modes,
        wall_distance,
        extrude_method,
    )


def convert_scene_elite_to_jorek(
    elite_filepath: str,
    target_directory: str,
    jorek_filepath: str = "jorek_namelist",
    density_filepath: str = "density.txt",
    temperature_filepath: str = "temperature.txt",
    ffprime_filepath: str = "ffprime.txt",
    rz_boundary_filepath: str = "rz_boundary.txt",
    starwall_filepath: Optional[str] = None,
    starwall_modes: Tuple[int, int] = (-1, 1),
    wall_distance: float = 0.0,
    extrude_method: str = "scale",
) -> None:
    __convert_elite_to_jorek(
        elite_filepath,
        extract_from_scene_elite_input,
        target_directory,
        jorek_filepath,
        density_filepath,
        temperature_filepath,
        ffprime_filepath,
        rz_boundary_filepath,
        starwall_filepath,
        starwall_modes,
        wall_distance,
        extrude_method,
    )
