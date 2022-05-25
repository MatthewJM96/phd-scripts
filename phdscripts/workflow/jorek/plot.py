"""
Contains the general workflow for Jorek runs.
"""

from os.path import isdir
from os.path import join as join_path
from typing import Optional

from .. import Workflow, WorkflowSettings

PLOT_JOB_SCRIPT = "plot.job.run"
PLOT_JOB_OUT = "plot.job.out"
PLOT_JOB_ERR = "plot.job.err"

JOREK_INPUT = "input"


# TODO(Matthew): Make this composable with general JOREK workflow so as to let a bunch
#                of plots be generated as simulations complete rather than waiting
#                for all simulations to complete and then running this.
class PlotJorekWorkflow(Workflow):
    """
    Workflow for fixed-boundary Jorek runs.
    """

    def __init__(self, run_id: str, settings: WorkflowSettings, jorek_input: str):
        super().__init__(run_id, settings)

        self._jorek_input = jorek_input

    def run(self, run_after: Optional[str] = None) -> str:
        self.settings.scheduler.array_batch_jobs(
            self._job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
            run_after,
        )

    def _job_script(self) -> str:
        return join_path(self._root_dir(), PLOT_JOB_SCRIPT)

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
# Setup environment.
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

# Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {self._param_set_register()})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

# Enter working directory.
cd {self._root_dir()}/${{param_set_name}}

# Link in utils.
# TODO(Matthew): This path is explicit, would we like it generally not to be?
ln -s ~/tools/jorek.develop/util/ .

# Plot graphs.
# TODO(Matthew): Allow what gets plotted to be programmatically chosen?
./util/plot_live_data.sh -q energies -ps
./util/plot_live_data.sh -q growth_rates -ps
            """,
            job_name=f"{self.run_id}_plot_jorek",
            partition="skl_fua_prod",
            time="00:10:00",
            nodes=1,
            ntasks_per_node=48,
            output=f"{self._root_dir()}/%x.%a.{PLOT_JOB_OUT}",
            error=f"{self._root_dir()}/%x.%a.{PLOT_JOB_ERR}",
            account="FUA36_UKAEA_ML",
        )

    def _build_working_directory(self, name: str, _: dict) -> None:
        if not isdir(self._working_dir(name)):
            raise ValueError(f"No existing directory for param set with name: {name}")
