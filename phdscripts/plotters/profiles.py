from typing import Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_profiles(
    profiles: Dict[
        str, Union[List[Tuple[float, float]], Tuple[List[Tuple[float, float]], str]]
    ],
    plot_method: Callable = plt.plot,
    xaxis_name: Optional[str] = None,
    yaxis_name: Optional[str] = None,
    fig: Optional[Figure] = None,
    output_file: Optional[str] = None,
    show: bool = False,
    aspect: str = "equal",
    hide_legend: bool = False,
):
    plt.figure(fig)

    if xaxis_name:
        plt.xlabel(xaxis_name)

    if yaxis_name:
        plt.ylabel(yaxis_name)

    for prof_name, prof_values in profiles.items():
        if type(prof_values) is list:
            ret = plot_method(
                [value[0] for value in prof_values], [value[1] for value in prof_values]
            )
        else:
            ret = plot_method(
                [value[0] for value in prof_values[0]],
                [value[1] for value in prof_values[0]],
                color=prof_values[1],
            )

        if type(ret) is list:
            line = ret[0]
        else:
            line = ret

        line.set_label(prof_name)

    if not hide_legend and (output_file or show):
        plt.legend()

    if output_file:
        plt.savefig(output_file, transparent=True)

    if show:
        plt.gca().set_aspect(aspect, adjustable="box")
        plt.show()
