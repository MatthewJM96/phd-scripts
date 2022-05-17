"""
Parameter pack handling iterating over every permutation of the packed parameters.
"""

from math import floor
from typing import Any


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
        prod_idx = 1

        for param, realisations in self.__parameters.items():
            if not isinstance(realisations, list):
                param_set[param] = realisations
                continue

            if len(realisations) == 1:
                param_set[param] = realisations[0]
                continue

            if prod_idx == 1:
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
                param_idx = floor(float(idx) / float(prod_idx)) % len(realisations)

            param_set[param] = realisations[param_idx]

            prod_idx *= len(realisations)

        self.__index += 1

        return param_set

    def __str__(self):
        return str(repr(self.__parameters))
