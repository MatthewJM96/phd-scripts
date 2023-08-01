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
        self.__groups = []
        self.__realisations = {}
        self.__grouped_realisation_counts = []
        self.__ungrouped_params = []
        self.__index = 0
        self.__count = 0
        self.__dirty = False
        self.__iterating = False

    def include(
        self, param: str, values: Union[int, str, float, List[Union[int, str, float]]]
    ):
        """
        Adds the listed values as realisations of the named parameter to provide run
        combinations for.
        """

        if self.__iterating:
            raise RuntimeError("Cannot change includes while iterating parameter pack.")

        if not isinstance(values, list):
            values = [values]

        if param not in self.__parameters["include"]:
            self.__parameters["include"][param] = []

        self.__parameters["include"][param].extend(values)
        self.__dirty = True

    def exclude(
        self, param: str, values: Union[int, str, float, List[Union[int, str, float]]]
    ):
        """
        Adds the listed values as realisations of the named parameter to explicitly not
        provide run combinations for. This is useful if e.g. a big range of includes is
        desired, but with some specific values removed from that range.
        """

        if self.__iterating:
            raise RuntimeError("Cannot change excludes while iterating parameter pack.")

        if not isinstance(values, list):
            values = [values]

        if param not in self.__parameters["exclude"]:
            self.__parameters["exclude"][param] = []

        self.__parameters["exclude"][param].extend(values)
        self.__dirty = True

    def group(self, params: List[str]):
        """
        Builds a parameter group, extending an existing group if there is any overlap.
        Parameter groups work such that all value ranges of the parameters are stepped
        through simultaneously, up to the shortest range of the parameters in the group.

        For example, given a group of three parameters:
            x = [ 1, 2, 3, 4 ]
            y = [ 5, 6, 7 ]
            z = [ 8, 9, 10, 11 ]
        the only combinations that get ran would be:
            ( 1, 5, 8 )
            ( 2, 6, 9 )
            ( 3, 7, 10 )
        with the final values of x and z discarded.
        """

        if self.__iterating:
            raise RuntimeError("Cannot change groups while iterating parameter pack.")

        if len(params) == 0:
            raise ValueError("Params list to group cannot be empty.")

        # Check to see if this new group is actually an extension of an existing group.
        for group in self.__groups:
            if len([param for param in params if param not in set(group)]) != len(
                params
            ):
                group.extend(params)
                return

        # Not extending an existing group, add a new one.
        self.__groups.append(params)

    def __repr__(self):
        return repr(self.__parameters)

    def __len__(self):
        self.__calculate_realisations()

        return self.__count

    def __cmp__(self, dict_):
        return self.__cmp__(self.__parameters, dict_)

    def __calculate_combination_count(self) -> None:
        """
        Given a set of realisations, determines the number of combinations of them
        accounting for parameter groupings.
        """

        if len(self.__realisations) == 0:
            self.__count = 0
            return

        self.__count = 1
        self.__grouped_realisation_counts = []

        # Go through each group first, finding shortest value count held by a parameter
        # in it.

        for group in self.__groups:
            # First param in group must exist in realisations for the group to have any
            # effect.
            if group[0] not in self.__realistions.keys():
                self.__count = 0
                return

            # First param exists, start with it as grouped param with least
            # realisations.
            shortest = len(self.__realistions[group[0]])

            # For each subsequent param, see if it exists, and if it doesn't then see if
            # it is a param with less realisations than previously encountered params.
            for param in group[1:]:
                if param not in self.__realisations:
                    self.__count = 0
                    return

                if shortest > len(self.__realistions[param]):
                    shortest = len(self.__realistions[param])

            # Mark this count for iterating later.

            self.__grouped_realisation_counts.append(shortest)

            # Number of realisation combinations increases as product against number of
            # shortest realisations held by a param in this group.
            self.__count *= shortest

        # Go through all ungrouped params now.

        for param in self.__ungrouped_params:
            if param not in self.__realisations:
                self.__count = 0
                return

            if isinstance(self.__realisations[param], list):
                self.__count *= len(self.__realisations[param])

    def __calculate_realisations(self) -> None:
        """
        Collapses include and exclude conditions on each parameter and stores that final
        list, with a count made of combinations of all actual parameter values.
        """

        if not self.__dirty:
            return

        self.__realisations = {}

        # Figure out which parameters are ungrouped.

        self.__ungrouped_params = []
        for param in self.__realisations.keys():
            found_in_group = False
            for group in self.__groups:
                if param in group:
                    found_in_group = True
                    break
            if not found_in_group:
                self.__ungrouped_params.append(param)

        # Collapse include and exclude values of each parameter.

        for param, vals in self.__parameters["include"].items():
            if param in self.__parameters["exclude"]:
                exclude_vals = self.__parameters["exclude"][param]
                self.__realisations[param] = [x for x in vals if x not in exclude_vals]
            else:
                self.__realisations[param] = vals

            # Unset realisation if no values remained after exclusion.
            if len(self.__realisations[param]) == 0:
                del self.__realisations[param]

        # Accounting for groupings, calculate number of combinations of realisations
        # possible.

        self.__calculate_combination_count()

        # Done!

        self.__dirty = False

    def __iter__(self):
        self.__iterating = True
        self.__index = 0
        self.__calculate_realisations()

        return self

    def __next__(self):
        if self.__index == self.__count:
            self.__iterating = False
            raise StopIteration

        param_set = {}

        idx = self.__index
        prod_idx = 1

        # Handle grouped parameters.

        for group_idx in range(len(self.__groups)):
            group = self.__groups[group_idx]
            count = self.__grouped_realisation_counts[group_idx]

            if count == 1:
                for param in group:
                    if isinstance(self.__realisations[param], list):
                        param_set[param] = self.__realisations[param][0]
                    else:
                        param_set[param] = self.__realisations[param]
                continue

            if prod_idx == 1:
                param_idx = idx % count
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
                param_idx = floor(float(idx) / float(prod_idx)) % count

            for param in group:
                param_set[param] = self.__realisations[param][param_idx]

            prod_idx *= count

        # Handle ungrouped parameters.

        for param in self.__ungrouped_params:
            realisations = self.__realisations[param]

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
