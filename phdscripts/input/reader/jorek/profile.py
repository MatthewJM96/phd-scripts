from os.path import isfile
from typing import List, Tuple


def read_jorek_profile(filepath: str) -> List[Tuple[float, float]]:
    """
    Extracts the named inpout profiles used by JOREK in a run.
    """

    if not isfile(filepath):
        print(f"JOREK input profile does not exist:\n    {filepath}")
        return False, {}

    lines = []
    with open(filepath, "r") as input_profile_file:
        lines = input_profile_file.readlines()

    if lines is None or (len(lines) == 1 and lines[0] == ""):
        print(f"JOREK input profile file at:\n    {filepath}\nis empty!")
        return False, {}

    profile = []
    for line in lines:
        values = line.strip().split()
        try:
            profile.append((float(values[0]), float(values[1])))
        except ValueError:
            return []

    return profile
