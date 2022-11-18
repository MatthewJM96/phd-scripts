from os.path import join
from typing import Dict, List


def write_jorek_files(
    parameters: Dict[str, List[float]],
    target_directory: str,
    helena_filepath: str = "fort.10",
) -> bool:
    """
    Writes a JOREK namelist file based on the provided values for the various parameters
    obtained from an Elite input file. Of course no requirement is placed on these
    parameters of actually coming from an Elite input file, but they must follow Elite
    conventions and normalisations.
    """

    REQUIRED_PARAMETERS = set(
        {
            "pressure",
            "ffprime",
            "n",
            "T",
            "ellipticity",
            "triangularity",
            "quadrangularity",
            "mharm",
            "ishape",
            "imesh",
            "ias",
            "igam",
            "ipai",
            "idete",
            "eps",
            "b",
            "xiab",
            "rvac",
            "bvac",
            "zn0",
            "nr",
            "np",
            "nrmap",
            "npmap",
            "nchi",
            "niter",
            "amix",
            "npr1",
            "npr2",
            "npl1",
        }
    )
    keys = set(parameters.keys())
    if REQUIRED_PARAMETERS > keys:
        print(
            (
                "    Parameters provided do not at least include the required"
                "parameters.\n"
                f"        Parameters provided were: {keys}\n"
                f"        Parameters required are: {REQUIRED_PARAMETERS}\n"
            )
        )
        return False

    if (
        (len(parameters["pressure"]) != len(parameters["ffprime"]))
        or (len(parameters["pressure"]) != len(parameters["n"]))
        or (len(parameters["pressure"]) != len(parameters["T"]))
    ):
        print("Profile parameters are not all the same length.")
        return False

    profile = ""
    for idx in range(len(parameters["pressure"])):
        profile += f"DPR({idx:3}) = {parameters['pressure'][idx]:7.2f}, "
        profile += f"DF2({idx:3}) = {2 * parameters['ffprime'][idx]:7.2f}, "
        profile += f"TEPROF({idx:3}) = {parameters['T'][idx]:7.2f}, "
        profile += f"TIPROF({idx:3}) = {parameters['T'][idx]:7.2f}, "
        profile += f"NEPROF({idx:3}) = {parameters['n'][idx]:7.2f}, "
        profile += f"NIPROF({idx:3}) = {parameters['n'][idx]:7.2f}, \n"

    contents = (
        "Equilbirum Data for HELENA\n"
        "PPF SCENE\n"
        "\n"
        "&SHAPE\n"
        f"  ELLIP  = {parameters['ellipticity']},\n"
        f"  TRIA   = {parameters['triangularity']},\n"
        f"  QUAD   = {parameters['quadrangularity']},\n"
        f"  MHARM  = {parameters['mharm']},\n"
        f"  ISHAPE = {parameters['ishape']},\n"
        f"  IMESH  = {parameters['imesh']},\n"
        f"  IAS    = {parameters['ias']},\n"
        "&END\n"
        "&PROFILE\n"
        f"  IGAM = {parameters['igam']}\n"
        f"  IPAI = {parameters['ipai']}\n"
        f"  NPTS = {parameters['num_points']}\n"
        f"{profile}"
        "&END\n"
        "&PHYS\n"
        f"  IDETE = {parameters['idete']}\n"
        f"  EPS   = {parameters['eps']}\n"
        f"  B     = {parameters['b0']}\n"
        f"  XIAB  = {parameters['xiab']}\n"
        f"  RVAC  = {parameters['rvac']}\n"
        f"  BVAC  = {parameters['bvac']}\n"
        f"  ZN0   = {parameters['zn0']}\n"
        "&END\n"
        "&NUM\n"
        f"  NR    = {parameters['nr']}\n"
        f"  NP    = {parameters['np']}\n"
        f"  NRMAP = {parameters['nrmap']}\n"
        f"  NPMAP = {parameters['npmap']}\n"
        f"  NCHI  = {parameters['nchi']}\n"
        f"  NITER = {parameters['niter']}\n"
        f"  AMIX  = {parameters['amix']}\n"
        "&END\n"
        "&PRI\n"
        f"  NPR1 = {parameters['npr1']}\n"
        f"  NPR2 = {parameters['npr2']}\n"
        "&END\n"
        "&PLOT\n"
        f"  NPL1 = {parameters['npl1']}\n"
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
