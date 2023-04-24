from glob import glob
from os import chdir, curdir
from os.path import getctime
from re import findall
from subprocess import run
from tempfile import NamedTemporaryFile

REAL_PATTERN = r"[0-9]+.[0-9]+E[+-][0-9][0-9]"
FLUXSURFACE_RESULTS_PATTERN = r"(" + REAL_PATTERN + r")\s+(" + REAL_PATTERN + r")"


def find_flux_surface(
    jorek_postproc_binary: str,
    jorek_directory: str,
    jorek_output_filename: str,
    jorek_namelist_filename: str,
    psi: float,
):
    """
    Obtains RZ points lying on a specified flux surface.
    """

    # Create and run fluxsurface script in jorek2_postproc using a temporary file.
    previous_dir = curdir
    chdir(jorek_directory)

    with NamedTemporaryFile("w") as f:
        f.write(
            f"""namelist {jorek_namelist_filename}
jorek-units
for step 0 do
    fluxsurface {psi}
done
        """
        )

        run(f"{jorek_postproc_binary} < {f.name}".split())

    chdir(previous_dir)

    # Retrieve results of running the script.
    list_of_files = glob(f"{jorek_directory}/postproc/fluxsurface_at_*")
    latest_file = max(list_of_files, key=getctime)

    with open(latest_file, "r") as f:
        results = f.read()

    # Parse results of running the script.
    results = findall(FLUXSURFACE_RESULTS_PATTERN, results)

    return [(x[0], x[1]) for x in results]
