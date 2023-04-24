import re
from os.path import isfile
from typing import Dict, Tuple

MAGNETIC_AXIS_PATTERN = (
    r"magnetic axis\s*:\s+[0-9]+\s+"
    r"(-?[0-9]+.[0-9]+)\s+(-?[0-9]+.[0-9]+)\s+(-?[0-9]+.[0-9]+)"
)
LIMITER_POINT_PATTERN = (
    r"R_lim\s*=\s+(-?[0-9]+.[0-9]+)\s*\n\s*"
    r"Z_lim\s*=\s+(-?[0-9]+.[0-9]+)\s*\n\s*"
    r"Psi_lim\s*=\s+(-?[0-9]+.[0-9]+)"
)
GEOMETRIC_AXIS_PATTERN = (
    r"Rgeo\s*:\s+(-?[0-9]+.[0-9]+)\s*m\s*\n\s*Bgeo\s*:\s+(-?[0-9]+.[0-9]+)"
)
INTEGRALS_PATTERN = (
    r"current\s*:\s+(-?[0-9]+.[0-9]+)\s*MA\s*\n\s*"
    r"beta_p\s*:\s+(-?[0-9]+.[0-9]+)\s*\n\s*"
    r"beta_t\s*:\s+(-?[0-9]+.[0-9]+)\s*\n\s*"
    r"beta_n\s*:\s+(-?[0-9]+.[0-9]+)\s*\[\%\]\s*\n\s*"
    r"Area\s*:\s+(-?[0-9]+.[0-9]+)\s*m\^2\s*\n\s*"
    r"Volume\s*:\s+(-?[0-9]+.[0-9]+)"
)


def read_jorek_output(filepath: str) -> Tuple[bool, Dict]:
    """
    Extracts the standard output of a JOREK run.
    """

    if not isfile(filepath):
        print(f"JOREK stdout file does not exist:\n    {filepath}")
        return False, {}

    with open(filepath, "r") as f:
        output = f.read()

    results = {}

    mag_axis_matches = re.findall(MAGNETIC_AXIS_PATTERN, output)
    if len(mag_axis_matches) != 0:
        results["magnetic_axis"] = {
            "R": mag_axis_matches[-1][0],
            "Z": mag_axis_matches[-1][1],
            "psi": mag_axis_matches[-1][2],
        }

    lim_matches = re.findall(LIMITER_POINT_PATTERN, output)
    if len(lim_matches) != 0:
        results["limiter_point"] = {
            "R": lim_matches[-1][0],
            "Z": lim_matches[-1][1],
            "psi": lim_matches[-1][2],
        }

    geo_matches = re.findall(GEOMETRIC_AXIS_PATTERN, output)
    if len(geo_matches) != 0:
        results["geometric_centre"] = {
            "R": geo_matches[-1][0],
            "Z": 0.0,
            "B": geo_matches[-1][1],
        }

    integrals_matches = re.findall(INTEGRALS_PATTERN, output)
    if len(integrals_matches) != 0:
        results["integrals"] = {
            "current": integrals_matches[-1][0],
            "beta_poloidal": integrals_matches[-1][1],
            "beta_toroidal": integrals_matches[-1][2],
            "beta_normalised": integrals_matches[-1][3],
            "area": integrals_matches[-1][4],
            "volume": integrals_matches[-1][5],
        }

    return True, results
