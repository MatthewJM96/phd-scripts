from typing import Callable, List, Tuple

from phdscripts.math import lerp


def convert_profile_points(
    profile: List[Tuple[float, float]],
    target_xs: List[float],
    interp: Callable[[Tuple[float, float], Tuple[float, float], float], float] = lerp,
) -> List[Tuple[float, float]]:
    new_profile = []

    for target_x in target_xs:
        lower = None
        upper = None
        found_exact = False

        for entry in profile:
            if entry[0] == target_x:
                new_profile.append(entry)
                found_exact = True
                break
            if entry[0] < target_x:
                lower = entry
            else:
                upper = entry
                break

        if found_exact:
            continue

        if lower is None or upper is None:
            print(f"Target x, {target_x}, could not be interpolated.")
            continue

        new_profile.append((target_x, interp(lower, upper, target_x)))

    return new_profile
