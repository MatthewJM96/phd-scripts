from typing import Any


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
        self.__setattr__("psi_grid", [])
        self.__setattr__("boundary", [])
        self.__setattr__("limiter_surface", [])
