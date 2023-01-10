from typing import List, Tuple

import matplotlib.pyplot as plt


def scatter_2d(
    values: List[Tuple[float, float]],
    aspect: str = "equal",
    show: bool = False,
    output_file: str = None,
):
    plt.scatter([value[0] for value in values], [value[1] for value in values])

    if output_file:
        plt.savefig(output_file, transparent=True)

    if show:
        plt.gca().set_aspect(aspect, adjustable="box")
        plt.show()
