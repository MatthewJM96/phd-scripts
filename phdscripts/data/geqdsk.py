from typing import Any, Optional, Tuple, Union

from scipy.interpolate import RectBivariateSpline


class G_EQDSK(dict):
    """
    Data structure storing the G EQDSK format.
    """

    def __init__(self):
        self.__preset_parameters()

    def __getattr__(self, name) -> Any:
        return self.__dict__.__getitem__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__.__setitem__(name, value)

    def __delattr__(self, name: str) -> None:
        self.__dict__.__delitem__(name)

    def __preset_parameters(self) -> None:
        self.__setattr__("case", "")
        self.__setattr__("resolution", (0, 0))
        self.__setattr__("dimensions", (0, 0))
        # Note that the grid's origin is define as left in R and central in Z.
        self.__setattr__("origin", (0, 0))
        self.__setattr__("grid_R", [])
        self.__setattr__("grid_Z", [])
        self.__setattr__("R_geo", 0)
        self.__setattr__("B_geo", 0)
        self.__setattr__("R_mag", 0)
        self.__setattr__("Z_mag", 0)
        self.__setattr__("psi_mag", 0)
        self.__setattr__("psi_bnd", 0)
        self.__setattr__("current", 0)
        self.__setattr__("fpol", [])
        self.__setattr__("pressure", [])
        self.__setattr__("ffprime", [])
        self.__setattr__("pprime", [])
        self.__setattr__("q", [])
        self.__setattr__("psi_grid", [[]])
        self.__setattr__("psi_n", [])
        self.__setattr__("boundary", [])
        self.__setattr__("limiter_surface", [])

    def psi_at(
        self, R: Union[float, Tuple[float, float]], Z: Optional[float] = None
    ) -> float:
        spline = RectBivariateSpline(self["grid_R"], self["grid_Z"], self["psi_grid"])

        if isinstance(R, float) and not isinstance(Z, float):
            return 99999.0
        elif not isinstance(R, float):
            Z = R[1]
            R = R[0]

        return spline(R, Z).tolist()[0][0]

    def psi_normalised_at(
        self, R: Union[float, Tuple[float, float]], Z: Optional[float] = None
    ) -> float:
        spline = RectBivariateSpline(self["grid_R"], self["grid_Z"], self["psi_grid"])

        if isinstance(R, float) and not isinstance(Z, float):
            return 99999.0
        elif not isinstance(R, float):
            Z = R[1]
            R = R[0]

        return (spline(R, Z).tolist()[0][0] - self["psi_mag"]) / (
            self["psi_bnd"] - self["psi_mag"]
        )

    def holds_point(self, point: Tuple[float, float]) -> bool:
        return (
            point[0] < self["origin"][0]
            or point[0] > self["origin"][0] + self["dimensions"][0]
            or point[1] < self["origin"][1] - self["dimensions"][1] / 2.0
            or point[1] > self["origin"][1] + self["dimensions"][1] / 2.0
        )
