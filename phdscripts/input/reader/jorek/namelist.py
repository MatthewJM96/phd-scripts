from typing import Dict

from f90nml import read as read_namelist


def read_jorek_namelist(filepath: str) -> Dict:
    try:
        return read_namelist(filepath)["in1"]
    except Exception:
        return {}
