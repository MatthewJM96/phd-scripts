from os.path import isfile
from typing import Callable, Dict, List, Tuple, Union

EXPECTED_INPUT_PROFILE_HEADER = (
    '%"psin"       "FF\'"    "dFF\'/dpsin"    "rho"    "drho/dpsin"   "T"'
    '      "dT/dpsin"    "S_rho"     "S_T"        "D_perp"    "ZK_perp"'
)


def __decompose_input_profiles(
    lines: List[str],
) -> Dict[str, Union[float, List[Tuple[float, float]]]]:
    profiles = {
        "ffprime": [],
        "dffprime/dpsi": [],
        "rho": [],
        "drho/dpsi": [],
        "T": [],
        "dT/dpsi": [],
    }

    for line in lines:
        values = line.strip().split()

        profiles["ffprime"].append((float(values[0]), float(values[1])))
        profiles["dffprime/dpsi"].append((float(values[0]), float(values[2])))
        profiles["rho"].append((float(values[0]), float(values[3])))
        profiles["drho/dpsi"].append((float(values[0]), float(values[4])))
        profiles["T"].append((float(values[0]), float(values[5])))
        profiles["dT/dpsi"].append((float(values[0]), float(values[6])))

    return profiles


def __truncate_profiles_to_psi(
    profiles: Dict[str, Union[float, List[Tuple[float, float]]]], truncate_at=1.0
):
    for profile in profiles.values():
        for entry in reversed(profile):
            if entry[0] <= truncate_at:
                break

            profile.pop()


def read_input_profiles(
    filepath: str,
) -> Dict[str, Union[float, List[Tuple[float, float]]]]:
    """
    Extracts the inpout profiles used by JOREK in a run. This is useful if any profile
    was specified using JOREK's functional form.
    """

    if not isfile(filepath):
        print(f"JOREK input profile does not exist:\n    {filepath}")
        return False, {}

    lines = []
    with open(filepath, "r") as input_profiles_file:
        lines = input_profiles_file.readlines()

    if lines is None or (len(lines) == 1 and lines[0] == ""):
        print(f"JOREK input profile file at:\n    {filepath}\nis empty!")
        return False, {}

    if lines[0].strip() != EXPECTED_INPUT_PROFILE_HEADER:
        print("JOREK input profile format has changed, cannot parse.")
        return False, {}

    lines = lines[1:]

    profiles = __decompose_input_profiles(lines)

    __truncate_profiles_to_psi(profiles)

    return profiles


def __extract_params(
    names: List[Union[str, Tuple[str, Callable]]],
    lines: List[str],
    extracted_params: Dict[str, Union[float, List[Tuple[float, float]]]],
) -> bool:
    line = lines.pop(0)
    values = line.strip().split()

    if len(values) != len(names):
        return False

    try:
        for name_idx in range(len(names)):
            if type(names[name_idx]) is tuple:
                extracted_params[names[name_idx][0]] = names[name_idx][1](
                    values[name_idx]
                )
            else:
                extracted_params[names[name_idx]] = float(values[name_idx])
    except ValueError:
        return False

    return True


def __extract_profile_params(
    names: List[Union[str, Tuple[str, Callable]]],
    lines: List[str],
    extracted_params: Dict[str, Union[float, List[Tuple[float, float]]]],
) -> bool:
    profile_length = {}
    if not __extract_params([("length", int)], lines, profile_length):
        return False

    profile_length = profile_length["length"]

    for name_idx in range(len(names)):
        if type(names[name_idx]) is tuple:
            extracted_params[names[name_idx][0]] = [None] * profile_length
        else:
            extracted_params[names[name_idx]] = [None] * profile_length

    for profile_idx in range(profile_length):
        line = lines.pop(0)
        values = line.strip().split()

        if len(values) != len(names):
            return False

        try:
            for name_idx in range(len(names)):
                if type(names[name_idx]) is tuple:
                    extracted_params[names[name_idx][0]][profile_idx] = names[name_idx][
                        1
                    ](values[name_idx])
                else:
                    extracted_params[names[name_idx]][profile_idx] = float(
                        values[name_idx]
                    )
        except ValueError:
            return False

    return True


def __extract_equilibrium_axis_params(
    lines: List[str],
    extracted_params: Dict[str, Union[float, List[Tuple[float, float]]]],
) -> bool:
    # Extract magnetic axis coords and F0.
    if not __extract_params(
        ["R_magnetic_axis", "Z_magnetic_axis", "F0"], lines, extracted_params
    ):
        return False

    # Extract psi boundary and psi axis.
    if not __extract_params(["psi_boundary", "psi_axis"], lines, extracted_params):
        return False

    return True


def __extract_equilibrium_boundary(
    lines: List[str],
    extracted_params: Dict[str, Union[float, List[Tuple[float, float]]]],
) -> bool:
    # Extract boundary points.
    if not __extract_profile_params(["R", "Z"], lines, extracted_params):
        return False

    return True


def __extract_equilibrium_geometry_and_magnetics(
    lines: List[str],
    extracted_params: Dict[str, Union[float, List[Tuple[float, float]]]],
) -> bool:
    # Extract minor and major radius, and magnetic field on geometric axis.
    if not __extract_params(
        ["minor_radius", "major_radius", "magnetic_field_on_geometric_axis"],
        lines,
        extracted_params,
    ):
        return False

    # Extract current, beta poloidal, and beta toroidal.
    if not __extract_params(
        ["current", "beta_poloidal", "beta_toroidal"], lines, extracted_params
    ):
        return False

    # Extract beta normalised.
    if not __extract_params(["beta_normalised"], lines, extracted_params):
        return False

    return True


def __extract_equilibrium_profiles(
    lines: List[str],
    extracted_params: Dict[str, Union[float, List[Tuple[float, float]]]],
) -> bool:
    # Extract profiles.
    if not __extract_profile_params(
        ["psi", "pprime", "zjzprime", "q"], lines, extracted_params
    ):
        return False

    return True


def read_equilibrium_file(
    filepath: str,
) -> Dict[str, Union[float, List[Tuple[float, float]]]]:
    """
    Extracts the values stored in the equilibrium file generated by JOREK.
    """

    if not isfile(filepath):
        print(f"JOREK equilibrium file does not exist:\n    {filepath}")
        return False, {}

    lines = []
    with open(filepath, "r") as equilibrium_file:
        lines = equilibrium_file.readlines()

    if lines is None or (len(lines) == 1 and lines[0] == ""):
        print(f"JOREK equilibrium file at:\n    {filepath}\nis empty!")
        return False, {}

    extracted_params = {}

    if not __extract_equilibrium_axis_params(lines, extracted_params):
        return {}

    if not __extract_equilibrium_boundary(lines, extracted_params):
        return {}

    if not __extract_equilibrium_geometry_and_magnetics(lines, extracted_params):
        return {}

    if not __extract_equilibrium_profiles(lines, extracted_params):
        return {}

    return extracted_params
