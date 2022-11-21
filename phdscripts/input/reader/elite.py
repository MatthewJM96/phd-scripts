from os.path import isfile
from typing import Dict, List, Tuple


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


def extract_from_elite_input(
    elite_filepath: str,
    per_flux_params: Dict[str, str],
    per_point_params: Dict[str, str],
) -> Tuple[bool, Dict[str, List[float]]]:
    """
    Extracts the named parameters from an elite input file. Renaming parameters with
    canonical names provided. Keys of param dictionaries are parameter names as in elite
    file, while values are the canonical parameter names used in the returned
    dictionary.
    """

    if not isfile(elite_filepath):
        print("    File does not exist!")
        return False, {}

    elite_lines = []
    with open(elite_filepath, "r") as elite_file:
        elite_lines = elite_file.readlines()

    if elite_lines is None or (len(elite_lines) == 1 and elite_lines[0] == ""):
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

    params: Dict[str, List[float]] = {}

    for param, canonical in per_flux_params.items():
        success, values = __extract_per_flux_profile(
            elite_lines, param, flux_surface_count
        )

        if not success:
            print(f"    Could not parse parameter, {param}.")
            return False, {}

        params[canonical] = values

    for param, canonical in per_point_params.items():
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

        params[canonical] = values

    return True, params


SCENE_PER_FLUX_PARAMS = {
    "psi": "psi",
    "ffprime": "ffprime",
    "q": "q",
    "ne": "ne",
    "Te": "Te",
    "f(psi)": "f",
}
SCENE_PER_POINT_PARAMS = {"R": "R", "Z": "Z"}
HELENA_PER_FLUX_PARAMS = {
    "Psi:": "psi",
    "ffp:": "ffprime",
    "q:": "q",
    "ne:": "ne",
    "Te:": "Te",
    "fpol:": "f",
}
HELENA_PER_POINT_PARAMS = {"R:": "R", "z:": "Z"}


def extract_from_scene_elite_input(
    elite_filepath: str,
) -> Tuple[bool, Dict[str, List[float]]]:
    """
    Extracts a set of parameters from an elite input matching the format generated by
    scene. The parameters extracted a sufficient for building a jorek-starwall namelist.
    """
    return extract_from_elite_input(
        elite_filepath, SCENE_PER_FLUX_PARAMS, SCENE_PER_POINT_PARAMS
    )


def extract_from_helena_elite_input(
    elite_filepath: str,
) -> Tuple[bool, Dict[str, List[float]]]:
    """
    Extracts a set of parameters from an elite input matching the format generated by
    helena. The parameters extracted a sufficient for building a jorek-starwall
    namelist.
    """
    return extract_from_elite_input(
        elite_filepath, HELENA_PER_FLUX_PARAMS, HELENA_PER_POINT_PARAMS
    )
