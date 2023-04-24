from os.path import isfile
from typing import Dict, List, Tuple, Union

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


def read_jorek_input_profiles(
    filepath: str,
) -> Dict[str, Union[float, List[Tuple[float, float]]]]:
    """
    Extracts the inpout profiles used by JOREK in a run. This is useful if any profile
    was specified using JOREK's functional form.
    """

    if not isfile(filepath):
        print(f"JOREK input profiles file does not exist:\n    {filepath}")
        return False, {}

    lines = []
    with open(filepath, "r") as input_profiles_file:
        lines = input_profiles_file.readlines()

    if lines is None or (len(lines) == 1 and lines[0] == ""):
        print(f"JOREK input profiles file at:\n    {filepath}\nis empty!")
        return False, {}

    if lines[0].strip() != EXPECTED_INPUT_PROFILE_HEADER:
        print("JOREK input profile format has changed, cannot parse.")
        return False, {}

    lines = lines[1:]

    profiles = __decompose_input_profiles(lines)

    __truncate_profiles_to_psi(profiles)

    return profiles
