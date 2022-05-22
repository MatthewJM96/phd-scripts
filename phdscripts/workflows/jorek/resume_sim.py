"""
Contains the general workflow for Jorek runs.
"""

import re
from os.path import isdir
from os.path import join as join_path

from .. import Workflow, WorkflowSettings

JOREK_CONTINUE_JOB_SCRIPT = "jorek_continue.job.run"
JOREK_CONTINUE_JOB_OUT = "jorek_continue.job.out"
JOREK_CONTINUE_JOB_ERR = "jorek_continue.job.err"

JOREK_CONTINUE_INPUT = "input_jorek_continue"


class PlotJorekWorkflow(Workflow):
    """
    Workflow for fixed-boundary Jorek runs.
    """

    def __init__(
        self, run_id: str, settings: WorkflowSettings, original_jorek_input: str
    ):
        super().__init__(run_id, settings)

        self.__original_jorek_input = original_jorek_input

    def run(self):
        self.settings.scheduler.array_batch_jobs(
            self._job_script(), self._job_instances, self.settings.parallel_jobs
        )

    def _job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_CONTINUE_JOB_SCRIPT)

    def _original_jorek_input(self, name: str) -> str:
        return join_path(self._working_dir(name), self.__original_jorek_input)

    def _jorek_input(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_CONTINUE_INPUT)

    def _canonical_param_set_name(self, param_set: dict) -> str:
        # TODO(Matthew): Do we prefer to use something like uuid? This might make
        #                rather ridiculous directory names. Could provide a script
        #                that lists (with filtering/sorting) the runs and will move
        #                command line to the apporpriate directory by index choice.

        canonical_param_set_name = ""

        for name, value in param_set.items():
            canonical_param_set_name += name + "_" + str(value) + "___"

        return canonical_param_set_name

    def _write_job_scripts(self) -> None:
        self.settings.scheduler.write_array_job_script(
            self._job_script(),
            f"""
### Set environment
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

export OMP_NUM_THREADS=8
export I_MPI_PIN_MODE=lib

export KMP_AFFINITY=compact,verbose # These three lines were suggested by Tamas Feher
export I_MPI_PIN_DOMAIN=auto        # and have been useful for decreasing computation
export KMP_HW_SUBSET=1t             # time on KNL

# Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {self._param_set_register()})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

cd {self._root_dir()}/${{param_set_name}}

mpirun -n 2                            \\
    {self._jorek_exec} < {JOREK_CONTINUE_INPUT} \\
        | tee log.jorek
            """,
            job_name=f"{self.run_id}_jorek_run",
            partition="skl_fua_prod",
            time="02:00:00",
            nodes=2,
            ntasks_per_node=1,
            mem="177GB",
            output=f"{self._root_dir()}/%x.%a.{JOREK_CONTINUE_JOB_OUT}",
            error=f"{self._root_dir()}/%x.%a.{JOREK_CONTINUE_JOB_ERR}",
            A="FUA36_UKAEA_ML",
        )

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        if not isdir(self._working_dir(name)):
            raise ValueError(f"No existing directory for param set with name: {name}")

        self._update_jorek_input_file(name, param_set)

    def _update_jorek_input_file(self, name: str, param_set: dict) -> None:
        with open(self._original_jorek_input(name), "r") as f:
            jorek_input = f.read()

        for param, value in param_set.items():
            if param == "wall_distance":
                continue

            # Convert standard notation to Fortran's notation.
            value_str = str(value)
            value_str = re.sub(r"([0-9]+).?e(-?[0-9]+)", r"\1.d\2", value_str)

            escaped_param = re.escape(param)
            if (
                re.search(rf"{escaped_param} *= *-?[0-9]+[.d?[0-9]*]?", jorek_input)
                is not None
            ):
                jorek_input = re.sub(
                    rf"{escaped_param} *= *-?[0-9]+[.d?[0-9]*]?",
                    f"{param} = {value_str}",
                    jorek_input,
                )
            else:
                # TODO(Matthew): this actually breaks for now as there is a structure
                #                to JOREK inputs that we need to handle (i.e. closing
                #                "/" line).
                jorek_input += f"\n{param} = {value_str}"

        re.sub(r"restart += +\.(f|false)\.", "restart = .t.", value_str)

        with open(self._jorek_input(name), "w") as f:
            f.write(jorek_input)
