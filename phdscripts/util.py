"""
Utility functions.
"""

import re
from typing import Union


def to_float(num: Union[str, int, float]) -> float:
    """
    Handles float conversion where the string format may be in other formats such as
    the Fortran format.
    """

    if isinstance(num, (int, float)):
        return float(num)

    if re.fullmatch(r"[0-9]+\.?d[0-9]+", num) is not None:
        return num.replace("d", "e")
    else:
        try:
            return float(num)
        except Exception:
            raise ValueError(f"String: {num} is not convertible to float.")
