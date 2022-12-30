from typing import Callable, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_profiles(
    profiles: Dict[str, List[Tuple[float, float]]],
    plot_method: Callable = plt.plot,
    xaxis_name: Optional[str] = None,
    yaxis_name: Optional[str] = None,
    fig: Optional[Figure] = None,
    output_file: Optional[str] = None,
    show: bool = False,
    aspect: str = "equal",
):
    plt.figure(fig)

    if xaxis_name:
        plt.xlabel(xaxis_name)

    if yaxis_name:
        plt.ylabel(yaxis_name)

    for prof_name, prof_values in profiles.items():
        ret = plot_method(
            [value[0] for value in prof_values], [value[1] for value in prof_values]
        )

        if type(ret) is List:
            (line,) = ret
        else:
            line = ret

        line.set_label(prof_name)

    if output_file or show:
        plt.legend()

    if output_file:
        plt.savefig(output_file, transparent=True)

    if show:
        plt.gca().set_aspect(aspect, adjustable="box")
        plt.show()
