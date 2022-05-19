"""
Parameter pack handling iterating over every permutation of the packed parameters.
"""

from math import floor
from typing import List, Union


class ParameterPack:
    """
    Parameter pack handling iterating over every permutation of the packed parameters.
    Note that this is NOT thread-safe (not that anything in Python is...)!
    """

    def __init__(self):
        self.__parameters = {"include": {}, "exclude": {}}
        self.__actual_parameters = {}
        self.__index = 0
        self.__count = 0
        self.__dirty = False

    def include(
        self, param: str, values: Union[int, str, float, List[Union[int, str, float]]]
    ):
        if not isinstance(values, list):
            values = [values]

        if param not in self.__parameters["include"]:
            self.__parameters["include"][param] = []

        self.__parameters["include"][param].extend(values)
        self.__dirty = True

    def exclude(
        self, param: str, values: Union[int, str, float, List[Union[int, str, float]]]
    ):
        if not isinstance(values, list):
            values = [values]

        if param not in self.__parameters["exclude"]:
            self.__parameters["exclude"][param] = []

        self.__parameters["exclude"][param].extend(values)
        self.__dirty = True

    def __repr__(self):
        return repr(self.__parameters)

    def __len__(self):
        self.__calculate_acutal_parameters()

        return self.__count

    def __cmp__(self, dict_):
        return self.__cmp__(self.__parameters, dict_)

    def __calculate_acutal_parameters(self) -> None:
        if not self.__dirty:
            return

        self.__actual_parameters = {}
        for param, vals in self.__parameters["include"]:
            if param in self.__parameters["exclude"]:
                exclude_vals = self.__parameters["exclude"][param]
                self.__actual_parameters[param] = [
                    x for x in vals if x not in exclude_vals
                ]
            else:
                self.__actual_parameters[param] = vals

        if len(self.__actual_parameters) == 0:
            self.__count = 0
        else:
            self.__count = 1
            for vals in self.__acutal_parameters.values():
                if isinstance(vals, list):
                    self.__count *= len(vals)

        self.__dirty = False

    def __iter__(self):
        self.__index = 0
        self.__calculate_acutal_parameters()

        return self

    def __next__(self):
        if self.__index == self.__count:
            raise StopIteration

        param_set = {}

        idx = self.__index
        prod_idx = 1

        for param, realisations in self.__acutal_parameters.items():
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
