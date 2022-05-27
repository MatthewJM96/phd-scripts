"""
Contains the general workflow for Jorek runs.
"""

from distutils.dir_util import copy_tree
from os.path import join as join_path
from typing import Optional

from phdscripts.util import (
    convert_standard_to_fortran_number,
    has_parameterised_fortran_bool,
    has_parameterised_fortran_number,
    replace_parameterised_decimal_number_in_list,
    replace_parameterised_fortran_bool,
    replace_parameterised_fortran_number,
)

from .. import Workflow, WorkflowSettings
from .job_script import write_jorek_job_script, write_starwall_job_script

JOREK_INIT_JOB_SCRIPT = "jorek_init.job.run"
JOREK_RUN_JOB_SCRIPT = "jorek_run.job.run"
JOREK_RESUME_JOB_SCRIPT = "jorek_resume.job.run"
STARWALL_JOB_SCRIPT = "starwall.job.run"

JOREK_INIT_JOB_OUT = "jorek_init.job.out"
JOREK_RUN_JOB_OUT = "jorek_run.job.out"
JOREK_RESUME_JOB_OUT = "jorek_resume.job.out"
STARWALL_JOB_OUT = "starwall.job.out"

JOREK_INIT_JOB_ERR = "jorek_init.job.err"
JOREK_RUN_JOB_ERR = "jorek_run.job.err"
JOREK_RESUME_JOB_ERR = "jorek_resume.job.err"
STARWALL_JOB_ERR = "starwall.job.err"

JOREK_TEMPLATE_INPUT = "input_jorek_template"
JOREK_INIT_INPUT = "input_jorek_init"
JOREK_RUN_INPUT = "input_jorek_run"
JOREK_RESUME_INPUT = "input_jorek_resume"
STARWALL_INPUT = "input_starwall"


class JorekWorkflow(Workflow):
    """
    Workflow for free-boundary Jorek runs.
    """

    def __init__(
        self,
        run_id: str,
        settings: WorkflowSettings,
        template_dir: str,
        jorek_exec: str,
        resume: bool,
        timestep: Optional[int] = None,
        timestep_count: Optional[int] = None,
        jorek_params: dict = {},
        starwall_exec: Optional[str] = None,
        starwall_params: dict = {},
    ):
        super().__init__(run_id, settings)

        self._template_dir = template_dir
        self._jorek_exec = jorek_exec
        self._resume = resume
        self._timestep = timestep
        self._timestep_count = timestep_count
        self._jorek_params = jorek_params
        self._starwall_exec = starwall_exec
        self._starwall_params = starwall_params

    def run(self, run_after: Optional[str] = None) -> str:
        """
        Schedules jobs required to complete this workflow. Returns the ID of the
        last-scheduled jobs so as to allow other workflows to follow on from this
        workflow.
        """
        if not self._resume and self._starwall_exec is not None:
            # JOREK Initialisation
            jorek_init_id = self.settings.scheduler.array_batch_jobs(
                self._jorek_init_job_script(),
                self._job_instances,
                self.settings.parallel_jobs,
                array_dependency=run_after,
            )
            # STARWALL
            starwall_id = self.settings.scheduler.array_batch_jobs(
                self._starwall_job_script(),
                self._job_instances,
                self.settings.parallel_jobs,
                array_dependency=jorek_init_id,
            )
        else:
            # No dependency to chain JOREK run onto.
            starwall_id = None

        # JOREK Run
        return self.settings.scheduler.array_batch_jobs(
            self._jorek_resume_job_script()
            if self._resume
            else self._jorek_run_job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
            array_dependency=starwall_id if starwall_id is not None else run_after,
        )

    def _input_jorek(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_TEMPLATE_INPUT)

    def _input_jorek_init(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_INIT_INPUT)

    def _input_starwall(self, name: str) -> str:
        return join_path(self._working_dir(name), STARWALL_INPUT)

    def _input_jorek_run(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_RUN_INPUT)

    def _input_jorek_resume(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_RESUME_INPUT)

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

    def _jorek_resume_job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_RESUME_JOB_SCRIPT)

    def _starwall_job_script(self) -> str:
        return join_path(self._root_dir(), STARWALL_JOB_SCRIPT)

    def _write_job_scripts(self) -> None:
        # TODO(Matthew): Move this out of here, this is Marconi specific and we would
        #                rather have this injected by the caller.
        #                  As a case in point: this assumes free boundary with two
        #                  steps, and being ran as an array job via SLURM.

        if not self._resume and self._starwall_exec is not None:
            ########################
            # JOREK Initialisation #
            ########################
            write_jorek_job_script(
                self.run_id,
                self.settings.scheduler,
                self._jorek_init_job_script(),
                self._param_set_register(),
                self._root_dir(),
                self._jorek_exec,
                JOREK_INIT_INPUT,
                JOREK_INIT_JOB_OUT,
                JOREK_INIT_JOB_ERR,
                "jorek_init",
                "00:10:00",
            )

            ############
            # STARWALL #
            ############
            write_starwall_job_script(
                self.run_id,
                self.settings.scheduler,
                self._starwall_job_script(),
                self._param_set_register(),
                self._root_dir(),
                self._starwall_exec,
                STARWALL_INPUT,
                STARWALL_JOB_OUT,
                STARWALL_JOB_ERR,
                "starwall",
                "00:40:00",
            )

        ####################
        # JOREK Run/Resume #
        ####################
        write_jorek_job_script(
            self.run_id,
            self.settings.scheduler,
            self._jorek_resume_job_script()
            if self._resume
            else self._jorek_run_job_script(),
            self._param_set_register(),
            self._root_dir(),
            self._jorek_exec,
            JOREK_RESUME_INPUT if self._resume else JOREK_RUN_INPUT,
            JOREK_RESUME_JOB_OUT if self._resume else JOREK_RUN_JOB_OUT,
            JOREK_RESUME_JOB_ERR if self._resume else JOREK_RUN_JOB_ERR,
            "jorek_resume" if self._resume else "jorek_run",
            "02:00:00",
        )

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        copy_tree(self._template_dir, self._working_dir(name), preserve_symlinks=True)

        self._write_jorek_input_files(name, param_set)
        if not self._resume and self._starwall_exec is not None:
            self._update_starwall_input_file(name, param_set)

    def _write_jorek_input_files(self, name: str, param_set: dict) -> None:
        params = {**param_set, **self._jorek_params}
        if not self._resume:
            self._write_jorek_input_file(
                name,
                self._input_jorek_init(name),
                {**params, "tstep_n": 1.0, "nstep_n": 0},
            )

            run_params = params
            if self._timestep is not None:
                run_params = {**run_params, "tstep_n": self._timestep}
            if self._timestep_count is not None:
                run_params = {**run_params, "nstep_n": self._timestep_count}

            self._write_jorek_input_file(name, self._input_jorek_run(name), run_params)
        else:
            resume_params = params
            if self._timestep is not None:
                resume_params = {**resume_params, "tstep_n": self._timestep}
            if self._timestep_count is not None:
                resume_params = {**resume_params, "nstep_n": self._timestep_count}

            self._write_jorek_input_file(
                name,
                self._input_jorek_resume(name),
                {**resume_params, "restart": True},
            )

    def _write_jorek_input_file(
        self, name: str, output_filepath: str, param_set: dict
    ) -> None:
        with open(self._input_jorek(name), "r") as f:
            jorek_input = f.read()

        for param, value in param_set.items():
            if param == "wall_distance":
                continue

            # TODO(Matthew): handle non-number cases! (e.g. bool flags)

            if isinstance(value, bool):
                if has_parameterised_fortran_bool(param, jorek_input):
                    jorek_input = replace_parameterised_fortran_bool(
                        param, value, jorek_input
                    )
            elif isinstance(value, (float, int)):
                if has_parameterised_fortran_number(param, jorek_input):
                    jorek_input = replace_parameterised_fortran_number(
                        param, value, jorek_input
                    )
                else:
                    # TODO(Matthew): this actually breaks for now as there is a
                    #                structure to JOREK inputs that we need to handle
                    #                (i.e. closing "/" line).
                    jorek_input += (
                        f"\n{param} = "
                        f"{convert_standard_to_fortran_number(str(value))}"
                    )

        with open(output_filepath, "w") as f:
            f.write(jorek_input)

    def _update_starwall_input_file(self, name: str, param_set: dict) -> None:
        with open(self._input_starwall(name), "r") as f:
            starwall_input = f.read()

        # TODO(Matthew): support other parameters than wall distance.

        starwall_input = replace_parameterised_decimal_number_in_list(
            "rc_w", 1, str(param_set["wall_distance"]), starwall_input
        )
        starwall_input = replace_parameterised_decimal_number_in_list(
            "zs_w", 1, str(param_set["wall_distance"]), starwall_input
        )

        with open(self._input_starwall(name), "w") as f:
            f.write(starwall_input)
