"""
Contains the general workflow for Jorek runs.
"""

import re
from distutils.dir_util import copy_tree
from os.path import join as join_path

from .. import Workflow, WorkflowSettings

JOREK_INIT_JOB_SCRIPT = "jorek_init.job.run"
JOREK_RUN_JOB_SCRIPT = "jorek_run.job.run"
STARWALL_JOB_SCRIPT = "starwall.job.run"

JOREK_INIT_JOB_OUT = "jorek_init.job.out"
JOREK_RUN_JOB_OUT = "jorek_run.job.out"
STARWALL_JOB_OUT = "starwall.job.out"

JOREK_INIT_JOB_ERR = "jorek_init.job.err"
JOREK_RUN_JOB_ERR = "jorek_run.job.err"
STARWALL_JOB_ERR = "starwall.job.err"

JOREK_INIT_INPUT = "input_jorek_init"
JOREK_RUN_INPUT = "input_jorek_run"
STARWALL_INPUT = "input_starwall"


class JorekFreeBoundaryWorkflow(Workflow):
    """
    Workflow for free-boundary Jorek runs.
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

    def run(self):
        # JOREK Initialisation
        jorek_init_id = self.settings.scheduler.array_batch_jobs(
            self._jorek_init_job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
        )
        # STARWALL
        starwall_id = self.settings.scheduler.array_batch_jobs(
            self._starwall_job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
            array_dependency=jorek_init_id,
        )
        # JOREK Run
        self.settings.scheduler.array_batch_jobs(
            self._jorek_run_job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
            array_dependency=starwall_id,
        )

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

    def _jorek_init_job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_INIT_JOB_SCRIPT)

    def _jorek_run_job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_RUN_JOB_SCRIPT)

    def _starwall_job_script(self) -> str:
        return join_path(self._root_dir(), STARWALL_JOB_SCRIPT)

    def _write_job_scripts(self) -> None:
        # TODO(Matthew): Move this out of here, this is Marconi specific and we would
        #                rather have this injected by the caller.
        #                  As a case in point: this assumes free boundary with two
        #                  steps, and being ran as an array job via SLURM.

        ########################
        # JOREK Initialisation #
        ########################

        self.settings.scheduler.write_array_job_script(
            self._jorek_init_job_script(),
            f"""
### Set environment
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

export OMP_NUM_THREADS=8
export I_MPI_PIN_MODE=lib

# Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {self._param_set_register()})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

cd {self._root_dir()}/${{param_set_name}}

mpirun -n 2                                 \\
    {self._jorek_exec} < {JOREK_INIT_INPUT} \\
        | tee log.jorek_init
            """,
            job_name=f"{self.run_id}_jorek_init",
            partition="skl_fua_prod",
            time="00:10:00",
            nodes=2,
            ntasks_per_node=1,
            mem="177GB",
            output=f"{self._root_dir()}/%x.%a.{JOREK_INIT_JOB_OUT}",
            error=f"{self._root_dir()}/%x.%a.{JOREK_INIT_JOB_ERR}",
            account="FUA36_UKAEA_ML",
        )

        ############
        # STARWALL #
        ############

        self.settings.scheduler.write_array_job_script(
            self._starwall_job_script(),
            f"""
### Set environment
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

export OMP_NUM_THREADS=1
export I_MPI_PIN_MODE=lib

# Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {self._param_set_register()})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

cd {self._root_dir()}/${{param_set_name}}

mpirun {self._starwall_exec} {STARWALL_INPUT} \\
        | tee log.starwall
            """,
            job_name=f"{self.run_id}_jorek_init",
            partition="skl_fua_prod",
            time="00:30:00",
            nodes=1,
            ntasks_per_node=48,
            cpus_per_task=1,
            output=f"{self._root_dir()}/%x.%a.{STARWALL_JOB_OUT}",
            error=f"{self._root_dir()}/%x.%a.{STARWALL_JOB_ERR}",
            account="FUA36_UKAEA_ML",
        )

        #############
        # JOREK Run #
        #############

        self.settings.scheduler.write_array_job_script(
            self._jorek_run_job_script(),
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

mpirun -n 2                                \\
    {self._jorek_exec} < {JOREK_RUN_INPUT} \\
        | tee log.jorek_run
            """,
            job_name=f"{self.run_id}_jorek_run",
            partition="skl_fua_prod",
            time="02:00:00",
            nodes=2,
            ntasks_per_node=1,
            mem="177GB",
            output=f"{self._root_dir()}/%x.%a.{JOREK_RUN_JOB_OUT}",
            error=f"{self._root_dir()}/%x.%a.{JOREK_RUN_JOB_ERR}",
            account="FUA36_UKAEA_ML",
        )

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
            value_str = re.sub(r"([0-9]+).?e(-?[0-9]+)", r"\1.d\2", value_str)

            escaped_param = re.escape(param)
            if (
                re.search(rf"{escaped_param} *= *-?[0-9]+[.d\-?[0-9]*]?", jorek_input)
                is not None
            ):
                jorek_input = re.sub(
                    rf"{escaped_param} *= *-?[0-9]+[.d\-?[0-9]*]?",
                    f"{param} = {value_str}",
                    jorek_input,
                )
            else:
                # TODO(Matthew): this actually breaks for now as there is a structure
                #                to JOREK inputs that we need to handle (i.e. closing
                #                "/" line).
                jorek_input += f"\n{param} = {value_str}"

        with open(filepath, "w") as f:
            f.write(jorek_input)

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
