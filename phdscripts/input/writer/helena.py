from os.path import join
from typing import Dict, List

from phdscripts.physical_constants import MU_0
from phdscripts.validate import validate_required_keys

DEFAULT_HELENA_PARAMETERS = {
    "MHARM": 128,
    "ISHAPE": 1,
    "IMESH": 1,
    "IAS": 0,
    "IGAM": 7,
    "IPAI": 7,
    "IDETE": 10,
    "NR": 101,
    "NP": 125,
    "NRMAP": 201,
    "NPMAP": 257,
    "NCHI": 257,
    "NITER": 500,
    "AMIX": 0.9,
    "NPR1": 1,
    "NPR2": 1,
    "NPL1": 1,
}

REQUIRED_HELENA_PARAMETERS = set(
    {
        #        "temperature",
        #        "denisty",
        "minor_radius",
        "major_radius",
        "density_on_axis",
    }
)

DEFAULT_HELENA_PARAMETERS_ISHAPE_1 = {"ELLIP": 0.0, "TRIA": 0.0, "QUAD": 0.0}

REQUIRED_HELENA_PARAMETERS_IPAI_7 = set({"pprime"})

DEFAULT_HELENA_PARAMETERS_IPAI_11 = {"EPI": 1.0, "FPI": 1.0}

REQUIRED_HELENA_PARAMETERS_IPAI_11 = set({"pprime"})

REQUIRED_HELENA_PARAMETERS_IGAM_7 = set({"ffprime"})


def __apply_defaults_and_validate(parameters: Dict[str, List[float]]) -> bool:
    param_keys = set(parameters.keys())

    if not validate_required_keys(REQUIRED_HELENA_PARAMETERS, param_keys, 1):
        return False

    parameters.update({**DEFAULT_HELENA_PARAMETERS, **parameters})

    if parameters["ISHAPE"] == 1:
        parameters.update({**DEFAULT_HELENA_PARAMETERS_ISHAPE_1, **parameters})

    if parameters["IPAI"] == 7:
        if not validate_required_keys(REQUIRED_HELENA_PARAMETERS_IPAI_7, param_keys, 1):
            return False
    elif parameters["IPAI"] == 11:
        if not validate_required_keys(
            REQUIRED_HELENA_PARAMETERS_IPAI_11, param_keys, 1
        ):
            return False
        parameters.update({**DEFAULT_HELENA_PARAMETERS_IPAI_11, **parameters})

    if parameters["IGAM"] == 7:
        if not validate_required_keys(REQUIRED_HELENA_PARAMETERS_IGAM_7, param_keys, 1):
            return False

    if (
        (len(parameters["pprime"]) != len(parameters["ffprime"]))
        or (
            "density" in parameters.keys()
            and len(parameters["pprime"]) != len(parameters["density"])
        )
        or (
            "temperature" in parameters.keys()
            and len(parameters["pprime"]) != len(parameters["temperature"])
        )
    ):
        print("    Profile parameters are not all the same length.")
        return False

    return True


def write_helena_input(
    parameters: Dict[str, List[float]],
    target_directory: str,
    helena_filepath: str = "fort.10",
    tagline: str = None,
) -> bool:
    """
    Writes a HELENA namelist file based on the provided parameters.
    """

    if not __apply_defaults_and_validate(parameters):
        return False

    aspect_ratio = parameters["minor_radius"] / parameters["major_radius"]
    gs_ratio = (
        parameters["pprime"][0]
        * (parameters["major_radius"] ** 2.0)
        / parameters["ffprime"][0]
    )
    normalised_total_current = (
        MU_0
        * abs(parameters["current"])
        / (parameters["minor_radius"] * parameters["magnetic_field_on_geometric_axis"])
    )

    # Normalise profiles.
    # normalise_profile(parameters["pprime"])
    # normalise_profile(parameters["ffprime"])

    normalised_ffprime = [x / parameters["ffprime"][0] for x in parameters["ffprime"]]

    num_profile_points = len(parameters["pprime"])
    profile = ""
    for idx in range(num_profile_points):
        profile += f"  DPR({idx+1:3}) = {parameters['pprime'][idx]:10.6f}, "
        profile += f"DF2({idx+1:3}) = {normalised_ffprime[idx]:10.6f},"
        if "temperature" in parameters.keys():
            profile += f"TEPROF({idx+1:3}) = {parameters['temperature'][idx]:10.6f}, "
            profile += f"TIPROF({idx+1:3}) = {parameters['temperature'][idx]:10.6f}, "
        if "density" in parameters.keys():
            profile += f"NEPROF({idx+1:3}) = {parameters['density'][idx]:10.6f}, "
            profile += f"NIPROF({idx+1:3}) = {parameters['density'][idx]:10.6f},"
        profile += "\n"

    tagline_formatted = "\n"
    if tagline:
        tagline_formatted = f"  {tagline}\n\n"

    contents = (
        "Equilbirum Data for HELENA\n"
        f"{tagline_formatted}"
        "&SHAPE\n"
        f"  ELLIP  = {parameters['ELLIP']},\n"
        f"  TRIA   = {parameters['TRIA']},\n"
        f"  QUAD   = {parameters['QUAD']},\n"
        f"  MHARM  = {parameters['MHARM']},\n"
        f"  ISHAPE = {parameters['ISHAPE']},\n"
        f"  IMESH  = {parameters['IMESH']},\n"
        f"  IAS    = {parameters['IAS']},\n"
        "&END\n"
        "&PROFILE\n"
        f"  IGAM = {parameters['IGAM']}\n"
        f"  IPAI = {parameters['IPAI']}\n"
        f"  NPTS = {num_profile_points}\n"
        f"{profile}"
        "&END\n"
        "&PHYS\n"
        f"  IDETE = {parameters['IDETE']}\n"
        f"  EPS   = {aspect_ratio}\n"
        f"  B     = {gs_ratio}\n"
        f"  XIAB  = {normalised_total_current}\n"
        f"  RVAC  = {parameters['major_radius']}\n"
        f"  BVAC  = {parameters['magnetic_field_on_geometric_axis']}\n"
        f"  ZN0   = {parameters['density_on_geometric_axis']}\n"
        "&END\n"
        "&NUM\n"
        f"  NR    = {parameters['NR']}\n"
        f"  NP    = {parameters['NP']}\n"
        f"  NRMAP = {parameters['NRMAP']}\n"
        f"  NPMAP = {parameters['NPMAP']}\n"
        f"  NCHI  = {parameters['NCHI']}\n"
        f"  NITER = {parameters['NITER']}\n"
        f"  AMIX  = {parameters['AMIX']}\n"
        "&END\n"
        "&PRI\n"
        f"  NPR1 = {parameters['NPR1']}\n"
        f"  NPR2 = {parameters['NPR2']}\n"
        "&END\n"
        "&PLOT\n"
        f"  NPL1 = {parameters['NPL1']}\n"
        "&END\n"
        "&BALL\n"
        # Empty
        "&END\n"
        "&MERC\n"
        # Empty
        "&END\n"
    )

    with open(join(target_directory, helena_filepath), "w") as helena_file:
        helena_file.write(contents)

    return True
