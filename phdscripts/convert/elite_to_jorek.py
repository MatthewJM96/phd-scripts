from os.path import isfile
from typing import Dict, List, Tuple


def __read_flux_metadata(lines: List[str]) -> Tuple[bool, int, int]:
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
    lines: List[str], param: str, flux_surface_point_count: int
) -> Tuple[bool, List[float]]:
    values: List[float] = []

    found_start = False
    for line in lines:
        # If we have found the start of the values for this parameter,
        # then handle ingestion.
        if found_start:
            # If we have ingested all the values, break.
            if len(values) == flux_surface_point_count:
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

    # If we don't have flux_surface_point_count number of
    # values, then te input file was ill-formatted, return
    # failure.
    if len(values) != flux_surface_point_count:
        return (False, values)

    return (True, values)


def __extract_per_point_profile(
    lines: List[str],
    param: str,
    flux_surface_target: int,
    flux_surface_count: int,
    flux_surface_point_count: int,
) -> Tuple[bool, List[float]]:
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
            # If we have ingested all the values, break.
            if len(values) == flux_surface_point_count:
                break
            # If we have flux cursor equal to flux target, then we can
            # retrieve the value for the point on the target flux surface.
            if flux_cursor == flux_surface_target:
                values.append(point_values[flux_cursor - 1])
            # If we have hit end of flux surfaces for this point, wrap flux
            # cursor.
            if flux_cursor == flux_surface_count:
                flux_cursor = 0
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
        return (False, values)

    return (True, values)


def convert_elite_to_jorek(elite_filepath: str, jorek_filepath: str) -> None:
    if not isfile(elite_filepath):
        print(("Could not find an elite input file at:\n" f"    {elite_filepath}"))
        return

    elite_lines = []
    with open(elite_filepath, "r") as elite_file:
        elite_lines = elite_file.readlines()

    if elite_lines is None or elite_lines == "":
        print(f"Elite input file at:\n    {elite_filepath}\nis empty!")
        return

    # Read number of flux surfaces and number of points on each flux surface.
    success, flux_surface_count, flux_surface_point_count = __read_flux_metadata(
        elite_lines
    )
    if not success:
        print(
            (
                "Could not read flux metadata from elite input file at:\n"
                f"    {elite_filepath}\n"
                "Expect to see two integers on the second line giving number of\n"
                "flux surfaces and number of points on each flux surface\n"
                "respectively."
            )
        )

    PER_FLUX_PARAMS = ["psi", "ffprime", "q", "ne", "Te", "f(psi)"]
    PER_POINT_BOUNDARY_PARAMS = ["R", "Z"]

    params: Dict[str, List[float]] = {}

    for param in PER_FLUX_PARAMS:
        success, values = __extract_per_flux_profile(
            elite_lines, param, flux_surface_point_count
        )

        if not success:
            print(
                (
                    f"Could not parse parameter, {param}, in file:\n"
                    f"    {elite_filepath}"
                )
            )

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
