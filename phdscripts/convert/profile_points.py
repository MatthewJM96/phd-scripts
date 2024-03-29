from typing import Callable, List, Tuple

from phdscripts.math import linear_interpolate


def convert_profile_points(
    profile: List[Tuple[float, float]],
    target_xs: List[float],
    interp: Callable[
        [List[Tuple[float, float]], int, int, float], float
    ] = linear_interpolate,
    extrap: Callable[[List[Tuple[float, float]], float], float] = None,
) -> List[Tuple[float, float]]:
    new_profile = []

    for target_x in target_xs:
        lower = None
        upper = None
        found_exact = False

        for idx in range(len(profile)):
            if profile[idx][0] == target_x:
                new_profile.append(profile[idx])
                found_exact = True
                break
            if profile[idx][0] < target_x:
                lower = idx
            else:
                upper = idx
                break

        if found_exact:
            continue

        if lower is None or upper is None:
            if extrap is not None:
                new_profile.append((target_x, extrap(profile, target_x)))
            else:
                print(f"Target x, {target_x}, could not be interpolated.")

            continue

        new_profile.append((target_x, interp(profile, lower, upper, target_x)))

    return new_profile
