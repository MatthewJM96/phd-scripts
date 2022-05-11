"""
Logic for building a parameter pack, on which a parameter scan can be performed.
"""

from os.path import isfile
from typing import Any, List, Optional

from numpy import arange
from yaml import full_load

from .util import to_float


class ParameterPack:
    def __init__(self):
        self.__parameters = {}
        self.__index = 0
        self.__count = 0

    def __getitem__(self, key: str) -> Any:
        return self.__parameters[key]

    def __setitem__(self, key: str, val: Any):
        self.__parameters[key] = val

    def __repr__(self):
        return repr(self.__parameters)

    def __len__(self):
        return len(self.__parameters)

    def __delitem__(self, key):
        del self.__parameters[key]

    def __cmp__(self, dict_):
        return self.__cmp__(self.__parameters, dict_)

    def __contains__(self, item):
        return item in self.__parameters

    def __count_parameter_permutations(self):
        if len(self.__parameters) == 0:
            self.__count = 0
        else:
            self.__count = 1
            for realisations in self.__parameters.values():
                if isinstance(realisations, list):
                    self.__count *= len(realisations)

    def __iter__(self):
        self.__index = 0
        self.__count_parameter_permutations()

        return self

    def __next__(self):
        if self.__index == self.__count:
            raise StopIteration

        param_set = {}

        idx = self.__index
        cumul_idx = 0

        for param, realisations in self.__parameters.items():
            if not isinstance(realisations, list):
                param_set[param] = realisations
                continue

            if cumul_idx == 0:
                param_idx = idx % len(realisations)
            else:
                # This maths produces indexing that gives us an index structure across
                # parameters like:
                #       0 0 0 0 0
                #       1 0 0 0 0
                #       0 0 1 0 0
                #       1 0 1 0 0
                #       0 0 2 0 0
                #       1 0 2 0 0
                #       0 0 0 1 0
                #       1 0 0 1 0
                #       0 0 1 1 0
                #       1 0 1 1 0
                #       0 0 2 1 0
                #       1 0 2 1 0
                # etc. where in this case the first three parameters had 2, 1
                # and 3 realisations respectively.
                param_idx = int((idx - (idx % cumul_idx)) / cumul_idx) % len(
                    realisations
                )

            param_set[param] = realisations[param_idx]

            cumul_idx += len(realisations)

        self.__index += 1

        return param_set

    def __str__(self):
        return str(repr(self.__parameters))


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
    for key, val in raw_params.items():
        if isinstance(val, dict):
            params[key] = __parse_dict_param(val)
        else:
            params[key] = val

    return params
