from os.path import isfile
from re import findall
from typing import List, Tuple

from phdscripts.data import G_EQDSK

FORTRAN_INTEGERS_AND_FLOATS_PATTERN = r"\s?([-]?[0-9]+(\.[0-9]+)?(E[+-][0-9]+)?)"


def __parse_header(header: str) -> Tuple[bool, str, int, int]:
    """
    Parses the header string of a G EQDSK.
    """

    vals = header[51:].split()

    if len(vals) != 3:
        return False, "", 0, 0

    try:
        return True, header[:50], int(vals[1]), int(vals[2])
    except Exception:
        return False, "", 0, 0


def __parse_domain(
    raw_values: List[str],
) -> Tuple[bool, Tuple[float, float], Tuple[float, float]]:
    try:
        return (
            True,
            (float(raw_values[0]), float(raw_values[1])),
            (float(raw_values[3]), float(raw_values[4])),
        )
    except Exception:
        return False, (), ()


def __parse_axes(
    raw_values: List[str],
) -> Tuple[bool, float, float, float, float, float]:
    try:
        return (
            True,
            float(raw_values[2]),
            float(raw_values[9]),
            float(raw_values[5]),
            float(raw_values[6]),
            float(raw_values[7]),
        )
    except Exception:
        return False, 0.0, 0.0, 0.0, 0.0, 0.0


def __parse_current_and_psi_bnd(raw_values: List[str]) -> Tuple[bool, float, float]:
    try:
        return True, float(raw_values[8]), float(raw_values[10])
    except Exception:
        return False, 0.0, 0.0


def __parse_profile(
    raw_values: List[str], length: int, offset: int
) -> Tuple[bool, List[float]]:
    profile = []

    try:
        for val in raw_values[offset : offset + length]:
            profile.append(float(val))
    except Exception:
        return False, []

    return True, profile


def __parse_f_poloidal(raw_values: List[str], nr: int) -> Tuple[bool, List[float]]:
    return __parse_profile(raw_values, nr, 20)


def __parse_pressure(raw_values: List[str], nr: int) -> Tuple[bool, List[float]]:
    return __parse_profile(raw_values, nr, 20 + nr)


def __parse_ffprime(raw_values: List[str], nr: int) -> Tuple[bool, List[float]]:
    return __parse_profile(raw_values, nr, 20 + 2 * nr)


def __parse_pprime(raw_values: List[str], nr: int) -> Tuple[bool, List[float]]:
    return __parse_profile(raw_values, nr, 20 + 3 * nr)


def __parse_psi_grid(
    raw_values: List[str], nr: int, nz: int
) -> Tuple[bool, List[float]]:
    return __parse_profile(raw_values, nr * nz, 20 + 4 * nr)


def __parse_q(raw_values: List[str], nr: int, nz: int) -> Tuple[bool, List[float]]:
    return __parse_profile(raw_values, nr, 20 + 4 * nr + nr * nz)


def __parse_num_bnd_lim(
    raw_values: List[str], nr: int, nz: int
) -> Tuple[bool, int, int]:
    offset = 20 + 5 * nr + nr * nz

    try:
        return True, int(raw_values[offset]), int(raw_values[offset + 1])
    except Exception:
        return False, 0, 0


def __parse_boundary(
    raw_values: List[str], nr: int, nz: int, nbnd: int
) -> Tuple[bool, List[float]]:
    success, profile = __parse_profile(raw_values, nbnd * 2, 20 + 5 * nr + nr * nz + 2)
    if not success:
        return False, []

    return True, [(profile[i], profile[i + 1]) for i in range(0, nbnd * 2, 2)]


def __parse_limiter_surface(
    raw_values: List[str], nr: int, nz: int, nbnd: int, nlim: int
) -> Tuple[bool, List[float]]:
    success, profile = __parse_profile(
        raw_values, nlim * 2, 20 + 5 * nr + nr * nz + 2 + 2 * nbnd
    )
    if not success:
        return False, []

    return True, [(profile[i], profile[i + 1]) for i in range(0, nbnd * 2, 2)]


def __parse_geqdsk(contents: List[str]) -> Tuple[bool, G_EQDSK]:
    success, case_name, nr, nz = __parse_header(contents[0])
    if not success:
        print("Could not parse header of G EQDSK file.")
        return False, G_EQDSK()

    # Have to split lines using regex as Fortran doesn't put spaces between floats when
    # the second float is negative!
    raw_values = []
    for line in contents[1:]:
        raw_values.extend(
            [x[0] for x in findall(FORTRAN_INTEGERS_AND_FLOATS_PATTERN, line)]
        )

    success, dimensions, origin = __parse_domain(raw_values)
    if not success:
        print("Could not parse domain of G EQDSK file.")
        return False, G_EQDSK()

    success, R_geo, B_geo, R_mag, Z_mag, psi_mag = __parse_axes(raw_values)
    if not success:
        print("Could not parse axes of G EQDSK file.")
        return False, G_EQDSK()

    success, psi_bnd, current = __parse_current_and_psi_bnd(raw_values)
    if not success:
        print("Could not parse current and psi boundary of G EQDSK file.")
        return False, G_EQDSK()

    success, f_poloidal = __parse_f_poloidal(raw_values, nr)
    if not success:
        print("Could not parse Fpol of G EQDSK file.")
        return False, G_EQDSK()

    success, pressure = __parse_pressure(raw_values, nr)
    if not success:
        print("Could not parse pressure of G EQDSK file.")
        return False, G_EQDSK()

    success, ffprime = __parse_ffprime(raw_values, nr)
    if not success:
        print("Could not parse FF' of G EQDSK file.")
        return False, G_EQDSK()

    success, pprime = __parse_pprime(raw_values, nr)
    if not success:
        print("Could not parse P' of G EQDSK file.")
        return False, G_EQDSK()

    success, psi_grid = __parse_psi_grid(raw_values, nr, nz)
    if not success:
        print("Could not parse psi grid of G EQDSK file.")
        return False, G_EQDSK()

    success, q = __parse_q(raw_values, nr, nz)
    if not success:
        print("Could not parse q of G EQDSK file.")
        return False, G_EQDSK()

    success, nbnd, nlim = __parse_num_bnd_lim(raw_values, nr, nz)
    if not success:
        print("Could not parse boundary and limiter point counts of G EQDSK file.")
        return False, G_EQDSK()

    success, boundary = __parse_boundary(raw_values, nr, nz, nbnd)
    if not success:
        print("Could not parse boundary of G EQDSK file.")
        return False, G_EQDSK()

    success, limiter_surface = __parse_limiter_surface(raw_values, nr, nz, nbnd, nlim)
    if not success:
        print("Could not parse limiter surface of G EQDSK file.")
        return False, G_EQDSK()

    geqdsk = G_EQDSK()
    geqdsk["case"] = case_name
    geqdsk["resolution"] = (nr, nz)
    geqdsk["dimensions"] = dimensions
    geqdsk["origin"] = origin
    geqdsk["R_geo"] = R_geo
    geqdsk["B_geo"] = B_geo
    geqdsk["R_mag"] = R_mag
    geqdsk["Z_mag"] = Z_mag
    geqdsk["psi_mag"] = psi_mag
    geqdsk["psi_bnd"] = psi_bnd
    geqdsk["current"] = current
    geqdsk["fpol"] = f_poloidal
    geqdsk["pressure"] = pressure
    geqdsk["ffprime"] = ffprime
    geqdsk["pprime"] = pprime
    geqdsk["psi_grid"] = psi_grid
    geqdsk["boundary"] = boundary
    geqdsk["limiter_surface"] = limiter_surface

    return True, geqdsk


def read_geqdsk(filepath: str) -> Tuple[bool, G_EQDSK]:
    if not isfile(filepath):
        print("Could not find geqdsk file:", filepath)
        return False, G_EQDSK()

    with open(filepath, "r") as f:
        return __parse_geqdsk(f.readlines())
