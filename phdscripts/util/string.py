"""
Utility functions for operating on strings.
"""

import re
from typing import List

_DECIMAL_NUMBER_PATTERN = r"-?[0-9]+[.[0-9]*]?"
_FORTRAN_NUMBER_PATTERN = r"-?[0-9]+[.d\-?[0-9]*]?"
_CAPTURED_STANDARD_NUMBER_PATTERN = r"(-?[0-9]+).?e(-?[0-9]+)"
_PARAM_START = r"(?:^|[^_a-zA-Z])"


def convert_standard_to_fortran_number(target: str) -> str:
    """
    Replaces a standard notation number with an equivalent Fortran-compatible number
    representation.
    """
    return re.sub(_CAPTURED_STANDARD_NUMBER_PATTERN, r"\1.d\2", target)


def has_fortran_number(pattern: str, target: str) -> bool:
    pattern = pattern.replace("@", _FORTRAN_NUMBER_PATTERN, 1)

    return re.search(pattern, target) is not None


def has_parameterised_fortran_number(
    param_name: str, target: str, intermediate: str = " *= *"
) -> bool:
    escaped_param_name = re.escape(param_name)

    return has_fortran_number(rf"{escaped_param_name}{intermediate}@", target)


def replace_decimal_number(pattern: str, sub: str, target: str) -> str:
    """
    Replace a decimal number found within a given pattern.
    """

    pattern = "(" + pattern.replace("@", f"){_DECIMAL_NUMBER_PATTERN}(", 1) + ")"

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


def replace_parameterised_decimal_number(
    param_name: str, sub: str, target: str, intermediate: str = " *= *"
) -> str:
    escaped_param_name = re.escape(param_name)

    return replace_decimal_number(
        rf"{_PARAM_START}{escaped_param_name}{intermediate}\K@",
        sub,
        target,
    )


def replace_parameterised_decimal_number_in_list(
    param_name: str,
    index: int,
    sub: str,
    target: str,
    intermediate: str = " *= *",
    list_separator: str = ", *",
    list_begin: str = "",
) -> str:
    escaped_param_name = re.escape(param_name)

    pattern = rf"{_PARAM_START}{escaped_param_name}{intermediate}{list_begin}"
    for _ in range(index):
        pattern += rf"{_DECIMAL_NUMBER_PATTERN}{list_separator}"
    pattern += r"\K@"

    return replace_decimal_number(
        pattern,
        sub,
        target,
    )


def replace_decimal_number_in_list(
    index: str,
    sub: str,
    target: str,
    intermediate: str = " *= *",
    list_separator: str = ", *",
    list_begin: str = "",
) -> str:
    return replace_parameterised_decimal_number_in_list(
        "", index, sub, target, intermediate, list_separator, list_begin
    )


def replace_fortran_number(pattern: str, sub: str, target: str) -> str:
    """
    Replaces a fortran number found within the given pattern.
    """
    # Place capture group around everything but the location to find a fortran number,
    # at which point place the regex pattern.
    pattern = pattern.replace("@", _FORTRAN_NUMBER_PATTERN, 1)

    return re.sub(
        pattern,
        sub,
        target,
    )


def replace_fortran_numbers(pattern: str, subs: List[str], target: str) -> str:
    for sub in subs:
        target = replace_fortran_number(pattern, sub, target)
        pattern = pattern.replace("@", sub, 1)

    return target


def replace_parameterised_fortran_number(
    param_name: str, sub: str, target: str, intermediate: str = " *= *"
) -> str:
    escaped_param_name = re.escape(param_name)

    return replace_fortran_number(
        rf"{_PARAM_START}{escaped_param_name}{intermediate}\K@",
        sub,
        target,
    )


def replace_parameterised_fortran_number_in_list(
    param_name: str,
    index: int,
    sub: str,
    target: str,
    intermediate: str = " *= *",
    list_separator: str = ", *",
    list_begin: str = "",
) -> str:
    escaped_param_name = re.escape(param_name)

    pattern = rf"{_PARAM_START}{escaped_param_name}{intermediate}{list_begin}"
    for _ in range(index):
        pattern += rf"{_FORTRAN_NUMBER_PATTERN}{list_separator}"
    pattern += r"\K@"

    return replace_fortran_number(
        pattern,
        sub,
        target,
    )


def replace_fortran_number_in_list(
    index: str,
    sub: str,
    target: str,
    intermediate: str = " *= *",
    list_separator: str = ", *",
    list_begin: str = "",
) -> str:
    return replace_parameterised_fortran_number_in_list(
        "", index, sub, target, intermediate, list_separator, list_begin
    )
