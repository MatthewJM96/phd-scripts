from os.path import join
from typing import Dict, List

from phdscripts.validate import validate_required_keys

REQUIRED_PARAMETERS = set(
    {"psi", "ffprime", "q", "n", "T", "f", "R", "Z", "central_density"}
)


def write_jorek_profile(profile: List[List[float]], filepath: str) -> bool:
    for idx in range(1, len(profile)):
        if len(profile[idx]) != len(profile[0]):
            return False

    with open(filepath, "w") as profile_file:
        for idx in range(len(profile[0])):
            for component in profile:
                profile_file.write(f"{component[idx]} ")
            profile_file.write("\n")

    return True


def write_jorek_files(
    parameters: Dict[str, List[float]],
    target_directory: str,
    jorek_filepath: str = "jorek_namelist",
    density_filepath: str = "density.txt",
    temperature_filepath: str = "temperature.txt",
    ffprime_filepath: str = "ffprime.txt",
    rz_boundary_filepath: str = "rz_boundary.txt",
) -> bool:
    """
    Writes a JOREK namelist file based on the provided values for the various parameters
    obtained from an Elite input file. Of course no requirement is placed on these
    parameters of actually coming from an Elite input file, but they must follow Elite
    conventions and normalisations.
    """

    if not validate_required_keys(REQUIRED_PARAMETERS, set(parameters.keys()), 1):
        return False

    psi = parameters["psi"]

    r_boundary = parameters["R"]
    z_boundary = parameters["Z"]
    if len(r_boundary) != len(z_boundary):
        print("    Number of obtained R and Z boundary values are different.")
        return False

    n_boundary = len(r_boundary)
    r_geo = (min(r_boundary) + max(r_boundary)) / 2.0
    z_geo = (min(z_boundary) + max(z_boundary)) / 2.0

    # Write profiles to their files.
    #   Density
    success = write_jorek_profile(
        [psi, parameters["n"]], join(target_directory, density_filepath)
    )
    #   Temperature
    success = success and write_jorek_profile(
        [psi, parameters["T"]], join(target_directory, temperature_filepath)
    )
    #   FFprime
    success = success and write_jorek_profile(
        [psi, parameters["ffprime"]], join(target_directory, ffprime_filepath)
    )
    #   R-Z
    success = success and write_jorek_profile(
        [r_boundary, z_boundary, [psi[-1]] * len(r_boundary)],
        join(target_directory, rz_boundary_filepath),
    )
    if not success:
        print("    Could not write one of the profiles.")
        return False

    contents = (
        "&in1\n"
        "  restart = .f.\n"
        "  regrid  = .f.\n"
        "\n"
        "  tstep_n   = 5.\n"
        "  nstep_n   = 0\n"
        "\n"
        "  !tstep_n   = 5.\n"
        "  !nstep_n   = 100\n"
        "\n"
        "  freeboundary = .t.\n"
        "  wall_resistivity_fact = 1.\n"
        "\n"
        "  linear_run = .t.\n"
        "\n"
        "  nout = 4\n"
        "\n"
        "  fbnd(1)   = 2.\n"
        "  fbnd(2:4) = 0.\n"
        "  mf        = 0\n"
        "\n"
        f"  n_boundary = {n_boundary}\n"
        f'  R_Z_psi_bnd_file = "{rz_boundary_filepath}"\n'
        "\n"
        f"  R_geo = {r_geo}\n"
        f"  Z_geo = {z_geo}\n"
        "\n"
        "  amin = 1.0\n"
        "\n"
        f"  F0 = {parameters['f'][0]}\n"
        "\n"
        f"  central_density = {parameters['central_density']}\n"
        f'  rho_file = "{density_filepath}"\n'
        f'  T_file   = "{temperature_filepath}"\n'
        f'  ffprime_file = "{ffprime_filepath}"\n'
        "\n"
        "  fix_axis_nodes = .t.\n"
        "  axis_srch_radius = 2.0\n"
        "\n"
        "  n_radial = 60 !240 !210 !130\n"
        "  n_pol    = 60 !205 !180 !110\n"
        "\n"
        "  n_flux   = 35 !120 !90 !55\n"
        "  n_tht    = 55 !160 !125 !80\n"
        "\n"
        "  visco_T_dependent = .f.\n"
        "\n"
        "  eta   = 1.d-8\n"
        "  visco = 1.d-10\n"
        "  visco_par = 1.d-10\n"
        "  eta_num = 0.d0\n"
        "  visco_num = 0.d0\n"
        "\n"
        "  D_par  = 0.d0\n"
        "  D_perp = 1.d-10\n"
        "  ZK_par  = 0.d0\n"
        "  ZK_perp = 1.d-10\n"
        "\n"
        "  heatsource     = 0.d0\n"
        "  particlesource = 0.d0\n"
        "/\n"
    )

    with open(join(target_directory, jorek_filepath), "w") as jorek_file:
        jorek_file.write(contents)

    return True
