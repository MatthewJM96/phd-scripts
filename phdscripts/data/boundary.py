from enum import IntEnum, auto
from typing import Dict, List, Tuple, Union


class BoundaryType(IntEnum):
    POINTS = auto()
    FOURIER_MODES = auto()
    MILLER_PARAMETERISED = auto()


class MillerParameters:
    def __init__(
        self, elongation: float, triangularity: float, quadrangularity: float = None
    ):
        self.elongation = elongation
        self.triangularity = triangularity
        self.quadrangularity = quadrangularity


class BoundaryData:
    def __init__(self):
        self.__type = None

    def set_points(self, rz_points: List[Tuple[float, float]]):
        self.__type = BoundaryType.POINTS
        self.__data = rz_points

    def set_fourier_modes(
        self,
        fourier_modes: Dict[
            int, Union[Tuple[float, float], Tuple[float, float, float, float]]
        ],
    ):
        self.__type = BoundaryType.FOURIER_MODES
        self.__data = fourier_modes

    def set_miller_parameters(self, parameters: MillerParameters):
        self.__type = BoundaryType.MILLER_PARAMETERISED
        self.__data = parameters

    def get_type(self) -> Union[BoundaryType, None]:
        return self.__type

    def get_data(
        self,
    ) -> Union[
        List[Tuple[float, float]],
        Dict[int, Union[Tuple[float, float], Tuple[float, float, float, float]]],
        MillerParameters,
        None,
    ]:
        return self.__data

    def is_boundary_points(self) -> bool:
        return self.__type == BoundaryType.POINTS

    def is_fourier_modes(self) -> bool:
        return self.__type == BoundaryType.FOURIER_MODES

    def is_miller_parameterised(self) -> bool:
        return self.__type == BoundaryType.MILLER_PARAMETERISED

    def get_boundary_points(self) -> Union[List[Tuple[float, float]], None]:
        if self.__type != BoundaryType.POINTS:
            return None

        return self.__data

    def get_fourier_modes(
        self,
    ) -> Union[
        Dict[int, Union[Tuple[float, float], Tuple[float, float, float, float]]], None
    ]:
        if self.__type != BoundaryType.FOURIER_MODES:
            return None

        return self.__data

    def get_miller_parameterised(self) -> Union[MillerParameters, None]:
        if self.__type != BoundaryType.MILLER_PARAMETERISED:
            return None

        return self.__data
