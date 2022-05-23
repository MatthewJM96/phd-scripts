"""
Utility functions for operating on strings.
"""

import re
from typing import List

__DECIMAL_NUMBER_PATTERN = r"[0-9]+[.[0-9]*]?"
__FORTRAN_NUMBER_PATTERN = r"-?[0-9]+[.d\-?[0-9]*]?"
__CAPTURED_STANDARD_NUMBER_PATTERN = r"(-?[0-9]+).?e(-?[0-9]+)"


def convert_standard_to_fortran_number(target: str) -> str:
    """
    Replaces a standard notation number with an equivalent Fortran-compatible number
    representation.
    """
    return re.sub(__CAPTURED_STANDARD_NUMBER_PATTERN, r"\1.d\2", target)


def has_fortran_number(pattern: str, target: str) -> bool:
    pattern = pattern.replace("@", __FORTRAN_NUMBER_PATTERN, 1)

    return re.search(pattern, target) is not None


def replace_decimal_number(pattern: str, sub: str, target: str) -> str:
    """
    Replace a decimal number found within a given pattern.
    """

    pattern = "(" + pattern.replace("@", f"){__DECIMAL_NUMBER_PATTERN}(", 1) + ")"

    return re.sub(
        pattern,
        f"\1{sub}\2",
        target,
    )


def replace_decimal_numbers(pattern: str, subs: List[str], target: str) -> str:
    for sub in subs:
        target = replace_decimal_number(pattern, sub, target)
        pattern = pattern.replace("@", sub, 1)

    return target


def replace_fortran_number(pattern: str, sub: str, target: str) -> str:
    """
    Replaces a fortran number found within the given pattern.
    """
    # Place capture group around everything but the location to find a fortran number,
    # at which point place the regex pattern.
    pattern = "(" + pattern.replace("@", f"){__FORTRAN_NUMBER_PATTERN}(", 1) + ")"

    return re.sub(
        pattern,
        f"\1{sub}\2",
        target,
    )


def replace_fortran_numbers(pattern: str, subs: List[str], target: str) -> str:
    for sub in subs:
        target = replace_fortran_number(pattern, sub, target)
        pattern = pattern.replace("@", sub, 1)

    return target
