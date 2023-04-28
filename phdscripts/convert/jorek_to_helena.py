from os.path import join

from phdscripts.convert import convert_profile_points
from phdscripts.data import BoundaryData
from phdscripts.input.reader import (
    read_jorek_equilibrium_file,
    read_jorek_input_profiles,
    read_jorek_namelist,
)
from phdscripts.input.writer import write_helena_input
from phdscripts.math import linear_extrapolate


def convert_jorek_to_helena(
    jorek_directory: str,
    target_directory: str,
    boundary: BoundaryData,
    helena_namelist_filename: str = "fort.10",
    helena_tagline: str = None,
    jorek_namelist_filename: str = "jorek_namelist",
    equilibrium_filename: str = "equilibrium.txt",
    input_profiles_filename: str = "input_profiles.dat",
) -> bool:
    # Only currently support Miller parameterisation.
    if not boundary.is_miller_parameterised():
        return False

    # Build filepaths.
    jorek_namelist_filepath = join(jorek_directory, jorek_namelist_filename)
    equilibrium_filepath = join(jorek_directory, equilibrium_filename)
    input_profiles_filepath = join(jorek_directory, input_profiles_filename)

    # Get various data from JOREK files.
    jorek_namelist_data = read_jorek_namelist(jorek_namelist_filepath)
    equilibrium_data = read_jorek_equilibrium_file(equilibrium_filepath)
    input_profiles = read_jorek_input_profiles(input_profiles_filepath)

    # Generate equidistant psis.
    profile_size = len(equilibrium_data["pprime"])
    psis = [float(x) / float(profile_size - 1) for x in range(profile_size)]

    # Convert psis of profiles to equidistant with same length as pprime.
    #   Easier to do this as pprime is on a root of not normalised psi, than convert
    #   pprime to match length of these.
    ffprime = convert_profile_points(
        input_profiles["ffprime"], psis, extrap=linear_extrapolate
    )
    temperature = convert_profile_points(
        input_profiles["T"], psis, extrap=linear_extrapolate
    )
    density = convert_profile_points(
        input_profiles["rho"], psis, extrap=linear_extrapolate
    )

    # Get boundary parameters.
    boundary_params = boundary.get_miller_parameterised()

    # Note that we need to unpack the tuples of psi/val for FF', temperature and
    # density.
    helena_parameters = {
        "IPAI": 11,
        "ELLIP": boundary_params.elongation,
        "TRIA": boundary_params.triangularity,
        "QUAD": boundary_params.quadrangularity,
        **equilibrium_data,
        "ffprime": [ffp[1] for ffp in ffprime],
        "temperature": [t[1] for t in temperature],
        "density": [n[1] for n in density],
        "density_on_geometric_axis": jorek_namelist_data["central_density"] * 10,
    }

    return write_helena_input(
        helena_parameters, target_directory, helena_namelist_filename, helena_tagline
    )
