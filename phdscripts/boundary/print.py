from typing import List, Tuple


def print_starwall_wall_file(points: List[Tuple[float, float]], filename: str):
    with open(filename, "w") as f:
        f.write(f"{len(points)}\n")
        for point in points:
            f.write(f"{point[0]} {point[1]}\n")
