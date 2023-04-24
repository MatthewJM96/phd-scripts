from math import tanh
from os import makedirs
from os.path import join
from typing import List, Tuple

from phdscripts.input import read_jorek_profile, write_jorek_profile

COLD_EXTENSION_WIDTH = 0.01


def add_jorek_cold_boundary(
    source_directory: str,
    target_directory: str,
    extension: float,
    cold_temperature: float,
    cold_density: float,
    cold_ffprime: float,
    extension_width: float = COLD_EXTENSION_WIDTH,
    source_psi_lim: float = 1.0,
):
    success, temperature = read_jorek_profile(join(source_directory, "temperature.txt"))
    if not success:
        return

    success, density = read_jorek_profile(join(source_directory, "density.txt"))
    if not success:
        return

    success, ffprime = read_jorek_profile(join(source_directory, "ffprime.txt"))
    if not success:
        return

    temperature = __renorm_and_extend_profile(
        source_psi_lim, temperature, extension, cold_temperature
    )
    density = __renorm_and_extend_profile(
        source_psi_lim, density, extension, cold_density
    )
    ffprime = __renorm_and_extend_profile(
        source_psi_lim, ffprime, extension, cold_ffprime
    )

    temperature = __mix_in_cold_boundary(
        temperature, cold_temperature, 1.0 / extension, extension_width
    )
    density = __mix_in_cold_boundary(
        density, cold_density, 1.0 / extension, extension_width
    )
    ffprime = __mix_in_cold_boundary(
        ffprime, cold_ffprime, 1.0 / extension, extension_width
    )

    makedirs(target_directory)

    write_jorek_profile(temperature, join(target_directory, "temperature.txt"))
    write_jorek_profile(density, join(target_directory, "density.txt"))
    write_jorek_profile(ffprime, join(target_directory, "ffprime.txt"))


def __renorm_profile(
    source_psi_lim: float, profile: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    tmp = []
    for el in profile:
        tmp.append((el[0] / source_psi_lim, el[1]))
    return tmp


def __renorm_and_extend_profile(
    source_psi_lim: float,
    profile: List[Tuple[float, float]],
    extension: float,
    cold_value: float,
    extension_width: float,
) -> List[Tuple[float, float]]:
    profile = __renorm_profile(source_psi_lim, profile)

    # Search for first profile element whose physical value is greater than 1.0, and
    # truncate all of these from the list.
    i = None
    for idx in range(-1, -len(profile) - 1):
        if profile[idx][0] <= 1.0:
            i = idx
            break
    # Do the truncation.
    if i < -1:
        profile = profile[: i + 1]

    # Add the cold boundary roughly to profile (only reasonably beyond the hot-cold
    # transition).
    psi_diff = extension - 1.0
    psi_step = psi_diff / 10.0
    for i in range(1, 11):
        psi = 1.0 + float(i) * psi_step
        if psi > 1.0 + extension_width * 2.0 / extension:
            profile.append((psi, cold_value))

    return profile


def __mix_in_cold_boundary(
    profile: List[Tuple[float, float]],
    cold_value: float,
    extension_psi: float,
    extension_width: float,
    added_resolution: int = 10,
) -> List[Tuple[float, float]]:
    profile = sorted(profile)

    def cold_factor(psi):
        return (1.0 + tanh((psi - extension_psi) / extension_width)) / 2.0

    res = []
    for el in profile:
        res.append(
            (
                el[0],
                cold_factor(el[0]) * cold_value + (1.0 - cold_factor(el[0])) * el[1],
            )
        )

    for i in range(added_resolution + 1):
        psi = float(i) * extension_width * 2.0 / float(added_resolution) + extension_psi

        above = None
        below = None
        for i in range(len(profile)):
            if below is None or profile[below][0] <= psi:
                below = i
            elif above is None or profile[above][0] > psi:
                above = i

        val = None
        if profile[below][0] == psi:
            val = profile[below][1]
        else:
            below_fact = 1.0 - (psi - profile[below][0]) / (
                profile[above][0] - profile[below][0]
            )
            above_fact = 1.0 - (profile[above][0] - psi) / (
                profile[above][0] - profile[below][0]
            )
            val = below_fact * profile[below][1] + above_fact * profile[above][1]

        res.append(
            (psi, cold_factor(psi) * cold_value + (1.0 - cold_factor(psi)) * val)
        )

    return sorted(res)
