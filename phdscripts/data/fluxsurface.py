from glob import glob
from math import atan2, pi, sqrt
from os import chdir, curdir, remove
from os.path import getctime, isfile, join
from re import findall
from subprocess import run
from typing import List, Tuple, Union
from uuid import uuid4

from phdscripts.input.reader import read_jorek_output, read_jorek_profile

REAL_PATTERN = r"-?[0-9]+.[0-9]+E[+-][0-9][0-9]"
FLUXSURFACE_RESULTS_PATTERN = r"(" + REAL_PATTERN + r")\s+(" + REAL_PATTERN + r")"


def find_flux_surface(
    jorek_postproc_binary: str,
    jorek_directory: str,
    jorek_namelist_filename: str,
    psi: float,
) -> Tuple[bool, List[Tuple[float, float]]]:
    """
    Obtains RZ points lying on a specified flux surface.
    """

    if not isfile(jorek_postproc_binary):
        print("JOREK postproc binary provided does not exist.")
        return False, []

    if not isfile(join(jorek_directory, jorek_namelist_filename)):
        print("JOREK namelist provided does not exist.")
        return False, []

    # Create and run fluxsurface script in jorek2_postproc using a temporary file.
    previous_dir = curdir
    chdir(jorek_directory)

    script_filename = "fluxsurface_script_" + uuid4().hex
    with open(script_filename, "w") as f:
        f.write(
            f"""namelist {jorek_namelist_filename}
jorek-units
for step 0 do
    fluxsurface {psi}
done
        """
        )

    run(f"{jorek_postproc_binary} < {script_filename}", shell=True, capture_output=True)

    remove(script_filename)
    chdir(previous_dir)

    # Retrieve results of running the script.
    list_of_files = glob(f"{jorek_directory}/postproc/fluxsurface_at_*")
    latest_file = max(list_of_files, key=getctime)

    with open(latest_file, "r") as f:
        results = f.read()

    # Parse results of running the script.
    results = findall(FLUXSURFACE_RESULTS_PATTERN, results)

    return True, [(float(x[0]), float(x[1])) for x in results]


def __theta(point: Tuple[float, float], magnetic_axis: Tuple[float, float]) -> float:
    """
    Calculates the theta angle from the inboard side of a tokamak for a given RZ
    coordinate with magnetic axis as the origin.
    """
    return atan2(point[1] - magnetic_axis[1], point[0] - magnetic_axis[0]) + pi


def __find_closest_points_to_theta(
    points: List[Tuple[float, float]], theta: float, magnetic_axis: Tuple[float, float]
) -> Tuple[int, int]:
    """
    Finds the two closest points to the given theta with respect to the given magnetic
    axis.
    """

    closest_theta_below = -99.0
    closest_theta_above = +99.0

    closest_theta_below_index = None
    closest_theta_above_index = None

    last_point_theta = None
    mirror_indices = None

    for idx in range(len(points)):
        point_theta = __theta(points[idx], magnetic_axis)

        if last_point_theta is not None and abs(point_theta - last_point_theta) > pi:
            if point_theta > last_point_theta:
                mirror_indices = (idx - 1, idx)
            else:
                mirror_indices = (idx, idx - 1)

        if point_theta - theta < 0.0 and point_theta - theta > closest_theta_below:
            closest_theta_below = point_theta
            closest_theta_below_index = idx
        elif point_theta - theta > 0.0 and point_theta - theta < closest_theta_above:
            closest_theta_above = point_theta
            closest_theta_above_index = idx

        last_point_theta = point_theta

    if closest_theta_below_index is None:
        point_theta = -(2 * pi - __theta(points[mirror_indices[1]], magnetic_axis))
        print("point ", point_theta)
        if point_theta - theta < 0.0 and point_theta - theta > closest_theta_below:
            closest_theta_below = point_theta
            closest_theta_below_index = idx

    if closest_theta_above_index is None:
        point_theta = 2 * pi + __theta(points[mirror_indices[0]], magnetic_axis)
        if point_theta - theta > 0.0 and point_theta - theta < closest_theta_above:
            closest_theta_above = point_theta
            closest_theta_above_index = idx

    return closest_theta_below_index, closest_theta_above_index


def __interp_closest_points(
    points: List[Tuple[float, float]], theta: float, magnetic_axis: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Creates an interpolated point between the two closest points to a given theta.
    """

    below, above = __find_closest_points_to_theta(points, theta, magnetic_axis)

    below_theta = __theta(points[below], magnetic_axis)
    above_theta = __theta(points[above], magnetic_axis)

    below_fact = 1.0 - (theta - below_theta) / (below_theta + above_theta)
    above_fact = 1.0 - (above_theta - theta) / (below_theta + above_theta)

    return (
        below_fact * points[below][0] + above_fact * points[above][0],
        below_fact * points[below][1] + above_fact * points[above][1],
    )


def __adjust_boundary_to_match_flux_surface(
    magnetic_axis: Tuple[float, float],
    boundary: List[Tuple[float, float]],
    actual_flux_surface: List[Tuple[float, float]],
    target_flux_surface: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """
    Takes the actual flux surface in a JOREK run with the given JOREK boundary, and
    computes a candidate boundary that will move the flux surface towards the target
    flux surface.
    """

    new_boundary = []
    for bnd_point in boundary:
        theta = __theta(bnd_point, magnetic_axis)

        actual_flux_at_theta = __interp_closest_points(
            actual_flux_surface, theta, magnetic_axis
        )
        target_flux_at_theta = __interp_closest_points(
            target_flux_surface, theta, magnetic_axis
        )

        actual_flux_mag_axis_dist = sqrt(
            (actual_flux_at_theta[0] - magnetic_axis[0]) ** 2.0
            + (actual_flux_at_theta[1] - magnetic_axis[1]) ** 2.0
        )
        target_flux_mag_axis_dist = sqrt(
            (target_flux_at_theta[0] - magnetic_axis[0]) ** 2.0
            + (target_flux_at_theta[1] - magnetic_axis[1]) ** 2.0
        )

        boundary_blowout = target_flux_mag_axis_dist / actual_flux_mag_axis_dist

        new_boundary.append(
            (
                (bnd_point[0] - magnetic_axis[0]) * boundary_blowout,
                (bnd_point[1] - magnetic_axis[1]) * boundary_blowout,
            )
        )

    return new_boundary


def adjust_boundary_to_match_flux_surface(
    psi: float,
    target_flux_surface: Union[str, List[Tuple[float, float]]],
    jorek_postproc_binary: str,
    jorek_directory: str,
    jorek_output_filename: str,
    jorek_namelist_filename: str = "jorek_namelist",
    jorek_boundary_filename: str = "rz_boundary.txt",
) -> Tuple[bool, List[Tuple[float, float]]]:
    """
    Takes the actual flux surface in a JOREK run with the given JOREK boundary, and
    computes a candidate boundary that will move the flux surface towards the target
    flux surface.
    """

    if psi < 0.0 or psi > 1.0:
        print("Flux surface psi must be normalised.")
        return False, []

    success, actual_flux_surface = find_flux_surface(
        jorek_postproc_binary, jorek_directory, jorek_namelist_filename, psi
    )
    if not success:
        print("Could not obtain actual flux surface.")
        return False, []

    output_filepath = join(jorek_directory, jorek_output_filename)
    success, output = read_jorek_output(output_filepath)
    if not success:
        print(f"Could not read JOREK output file: {output_filepath}")
        return False, []

    if "magnetic_axis" not in output.keys():
        print("Could not extract needed information (mag axis) from JOREK std output.")
        return False, []

    magnetic_axis = (
        float(output["magnetic_axis"]["R"]),
        float(output["magnetic_axis"]["Z"]),
    )

    boundary_filepath = join(jorek_directory, jorek_boundary_filename)
    success, boundary = read_jorek_profile(boundary_filepath)
    if not success:
        print(f"Could not read JOREK boundary file: {boundary_filepath}")
        return False, []

    if isinstance(target_flux_surface, str):
        flux_surface_file = target_flux_surface
        success, target_flux_surface = read_jorek_profile(flux_surface_file)
        if not success:
            print(
                f"Could not read target flux surface boundary file: {flux_surface_file}"
            )
            return False, []

    return True, __adjust_boundary_to_match_flux_surface(
        magnetic_axis, boundary, actual_flux_surface, target_flux_surface
    )
