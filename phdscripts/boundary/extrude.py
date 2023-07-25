from typing import Callable, List, Tuple, Union

from .extrude_normal import extrude_normal
from .extrude_scale import extrude_scale


def extrude(
    extrude_method: Union[str, Callable],
    points: List[Tuple[float, float]],
    distance: float,
    *args,
    **kwargs
) -> List[Tuple[float, float]]:
    if type(extrude_method) is str:
        if extrude_method == "scale":
            return extrude_scale(points, distance, *args, **kwargs)
        elif extrude_method == "normal":
            return extrude_normal(points, distance, *args, **kwargs)
        else:
            print("Invalid extrusion method:", extrude_method)
            return []
    elif type(extrude_method) is callable:
        return extrude_method(points, distance, *args, **kwargs)

    return []
