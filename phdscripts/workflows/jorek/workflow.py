"""
Contains the general workflow for Jorek runs.
"""

import re
from distutils.dir_util import copy_tree
from os.path import join as join_path

from .. import JOB_ERR_FILENAME, JOB_OUT_FILENAME, Workflow, WorkflowSettings

JOREK_INIT_INPUT = "input_jorek_init"
JOREK_RUN_INPUT = "input_jorek_run"
STARWALL_INPUT = "input_starwall"


class JorekWorkflow(Workflow):
    """
    General workflow for Jorek runs. Must be injected with specific logic for working
    directory building, and job script writing.
    """

    def __init__(
        self,
        run_id: str,
        settings: WorkflowSettings,
        template_dir: str,
        jorek_exec: str,
        starwall_exec: str,
    ):
        super().__init__(run_id, settings)

        self._template_dir = template_dir
        self._jorek_exec = jorek_exec
        self._starwall_exec = starwall_exec

    def _input_jorek_init(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_INIT_INPUT)

    def _input_starwall(self, name: str) -> str:
        return join_path(self._working_dir(name), STARWALL_INPUT)

    def _input_jorek_run(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_RUN_INPUT)

    def _canonical_param_set_name(self, param_set: dict) -> str:
        # TODO(Matthew): Do we prefer to use something like uuid? This might make
        #                rather ridiculous directory names. Could provide a script
        #                that lists (with filtering/sorting) the runs and will move
        #                command line to the apporpriate directory by index choice.

        canonical_param_set_name = ""

        for name, value in param_set.items():
            canonical_param_set_name += name + "_" + str(value) + "___"

        return canonical_param_set_name

    def _build_job_script(self) -> str:
        # TODO(Matthew): Move this out of here, this is Marconi specific and we would
        #                rather have this injected by the caller.
        #                  As a case in point: this assumes free boundary with two
        #                  steps.
        return f"""
#!/bin/bash

#SBATCH --job-name={self.run_id}
#SBATCH --partition=skl_fua_prod
##SBATCH --qos=skl_qos_fualprod
#SBATCH --time=02:00:00

#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --mem 177GB

#SBATCH --output={JOB_OUT_FILENAME}
#SBATCH --error={JOB_ERR_FILENAME}

#SBATCH -A FUA36_UKAEA_ML

##SBATCH --mail-type=FAIL
##SBATCH --mail-user=<e-mail address>

### Set environment
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

export OMP_NUM_THREADS=8
export I_MPI_PIN_MODE=lib

export KMP_AFFINITY=compact,verbose # These three lines were suggested by Tamas Feher
export I_MPI_PIN_DOMAIN=auto        # and have been useful for decreasing computation
export KMP_HW_SUBSET=1t             # time on KNL

# Obtain working directory name from reigster.
param_set=$(                                                                      \\
    awk '{{if(NR==$SLURM_ARRAY_TASK_ID) print $0}}' {self._param_set_register()} \\
)
param_set_parts=$(IFS=',' read -ra ADDR <<< "$param_set")
param_set_name=${{param_set_parts[0]}}

mpirun -n 2                                                      \\
    {self._jorek_exec} < ${{param_set_name}}/{JOREK_INIT_INPUT} \\
        | tee log.jorek_init

mpirun -n 1                                                     \\
    {self._starwall_exec} ${{param_set_name}}/{STARWALL_INPUT} \\
        | tee log.starwall

mpirun -n 2                                                     \\
    {self._jorek_exec} < ${{param_set_name}}/{JOREK_RUN_INPUT} \\
        | tee log.jorek_run
        """

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        copy_tree(self._template_dir, self._working_dir(name), preserve_symlinks=True)

        self._update_jorek_input_files(name, param_set)
        self._update_starwall_input_file(name, param_set)

    def _update_jorek_input_files(self, name: str, param_set: dict) -> None:
        self._update_jorek_input_file(self._input_jorek_init(name), param_set)
        self._update_jorek_input_file(self._input_jorek_run(name), param_set)

    def _update_jorek_input_file(self, filepath: str, param_set: dict) -> None:
        with open(filepath, "r") as f:
            jorek_input = f.read()

        for param, value in param_set.items():
            if param == "wall_distance":
                continue

            # Convert standard notation to Fortran's notation.
            value_str = str(value)
            value_str = re.sub(r"([0-9]+).d([0-9]+)", r"\1.e\2")

            if re.match(rf"{param} *= *-?[0-9]+[.d?[0-9]*]?", jorek_input) is not None:
                re.sub(
                    rf"{param} *= *-?[0-9]+[.d?[0-9]*]?",
                    f"{param} = {value_str}",
                    jorek_input,
                )
            else:
                jorek_input += f"\n{param} = {value_str}"

    def _update_starwall_input_file(self, name: str, param_set: dict) -> None:
        with open(self._input_starwall(name), "r") as f:
            starwall_input = f.read()

        starwall_input = re.sub(
            r"(rc_w *= *[0-9]+[.[0-9]*]?, *)[0-9]+[.[0-9]*]?",
            rf"\1 {param_set['wall_distance']}",
            starwall_input,
        )
        starwall_input = re.sub(
            r"(zs_w *= *[0-9]+[.[0-9]*]?, *)[0-9]+[.[0-9]*]?",
            rf"\1 {param_set['wall_distance']}",
            starwall_input,
        )

        with open(self._input_starwall(name), "w") as f:
            f.write(starwall_input)
