"""
Logic for building a parameter pack, on which a parameter scan can be performed.
"""

from os.path import isfile
from typing import List, Optional

from numpy import arange
from yaml import full_load

from ..util import to_float
from .parameter_pack import ParameterPack


def __parse_int_range_param(val: dict) -> List[int]:
    if not val.keys() >= {"start", "end"}:
        raise ValueError(f"IntRange object invalid:\n{val}")

    start = int(val["start"])
    end = int(val["end"])
    step = 1

    if "step" in val:
        step = int(val["step"])

    return list(range(start, end, step))


def __parse_float_range_param(val: dict) -> List[float]:
    if not val.keys() >= {"start", "end"}:
        raise ValueError(f"FloatRange object invalid:\n{val}")

    start = to_float(val["start"])
    end = to_float(val["end"])
    step = 1.0

    if "step" in val:
        step = to_float(val["step"])

    return list(arange(start, end, step))


def __parse_power_range_param(val: dict) -> List[float]:
    if not val.keys() >= {"start", "end", "exponentiated"}:
        raise ValueError(f"PowerRange object invalid:\n{val}")

    start = to_float(val["start"])
    end = to_float(val["end"])
    exponentiated = to_float(val["exponentiated"])
    coeff = 1.0
    step = 1.0

    if "coeff" in val:
        coeff = to_float(val["coefficient"])

    if "step" in val:
        step = to_float(val["step"])

    orders = list(arange(start, end, step))

    return [coeff * pow(exponentiated, order) for order in orders]


def __parse_oom_range_param(val: dict) -> List[float]:
    return __parse_power_range_param({**val, "exponentiated": 10.0})


def __parse_dict_param(val: dict):
    if "type" in val:
        if val["type"] == "IntRange":
            return __parse_int_range_param(val)
        elif val["type"] == "FloatRange":
            return __parse_float_range_param(val)
        elif val["type"] == "PowerRange":
            return __parse_power_range_param(val)
        elif val["type"] == "OrderOfMagnitudeRange":
            return __parse_oom_range_param(val)

    raise ValueError(f"Do not recognise parameter object:\n{val}")


def build_parameter_pack(
    filepath: Optional[str] = None, cli_args: Optional[dict] = None
) -> ParameterPack:
    raw_params = {}

    if filepath is not None and isfile(filepath):
        with open(filepath, "r") as f:
            raw_params = full_load(f)

    if cli_args is not None:
        raw_params.update(cli_args)

    params = ParameterPack()
    # TODO(Matthew): Support for excluding!
    for key, val in raw_params.items():
        if isinstance(val, dict):
            params.include(key, __parse_dict_param(val))
        else:
            params.include(key, val)

    return params
