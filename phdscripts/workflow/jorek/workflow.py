"""
Contains the general workflow for Jorek runs.
"""

from distutils.dir_util import copy_tree
from os.path import join as join_path
from typing import Optional
from uuid import uuid4

from .. import Workflow, WorkflowSettings
from .input_file import (
    update_starwall_input_file,
    write_fresh_jorek_input_files,
    write_resuming_jorek_input_files,
)
from .job_script import write_job_script

JOREK_JOB_SCRIPT = "jorek_%s.job.run"
STARWALL_JOB_SCRIPT = "starwall.job.run"

JOREK_JOB_OUT = "jorek_%s.job.out"
STARWALL_JOB_OUT = "starwall.job.out"

JOREK_JOB_ERR = "jorek_%s.job.err"
STARWALL_JOB_ERR = "starwall.job.err"

JOREK_INPUT = "input_jorek_%s"
STARWALL_INPUT = "input_starwall"

JOREK_RZPSI_INPUT = "rz_boundary.txt"
JOREK_EXTRUDE_FROM_INPUT = "extrude_from_boundary.txt"


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

        self.template_dir = template_dir
        self.jorek_exec = jorek_exec
        self.resume = resume
        self.timestep = timestep
        self.timestep_count = timestep_count
        self.jorek_params = jorek_params
        self.starwall_exec = starwall_exec
        self.starwall_params = starwall_params

    def run(self, run_after: Optional[str] = None) -> str:
        """
        Schedules jobs required to complete this workflow. Returns the ID of the
        last-scheduled jobs so as to allow other workflows to follow on from this
        workflow.
        """
        if not self.resume and self.starwall_exec is not None:
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
            if self.resume
            else self._jorek_run_job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
            array_dependency=starwall_id if starwall_id is not None else run_after,
        )

    def _input_jorek(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_INPUT)

    def _input_starwall(self, name: str) -> str:
        return join_path(self._working_dir(name), STARWALL_INPUT)

    def _input_jorek_rz_psi(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_RZPSI_INPUT)

    def _input_jorek_extrude_from(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_EXTRUDE_FROM_INPUT)

    def _canonical_param_set_name(self, _: dict) -> str:
        return uuid4()

    def _jorek_job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_JOB_SCRIPT)

    def _starwall_job_script(self) -> str:
        return join_path(self._root_dir(), STARWALL_JOB_SCRIPT)

    def _write_job_scripts(self) -> None:
        if not self.resume and self.starwall_exec is not None:
            ########################
            # JOREK Initialisation #
            ########################
            write_job_script(
                self.machine,
                "jorek",
                self.run_id,
                self.settings.scheduler,
                self._jorek_job_script() % "init",
                self._param_set_register(),
                self._root_dir(),
                self.jorek_exec,
                JOREK_INPUT % "init",
                JOREK_JOB_OUT % "init",
                JOREK_JOB_ERR % "init",
                "jorek_init",
                "00:10:00",
            )

            ############
            # STARWALL #
            ############
            write_job_script(
                self.machine,
                "starwall",
                self.run_id,
                self.settings.scheduler,
                self._starwall_job_script(),
                self._param_set_register(),
                self._root_dir(),
                self.starwall_exec,
                STARWALL_INPUT,
                STARWALL_JOB_OUT,
                STARWALL_JOB_ERR,
                "starwall",
                "02:00:00",
            )

        ####################
        # JOREK Run/Resume #
        ####################
        write_job_script(
            self.machine,
            "jorek",
            self.run_id,
            self.settings.scheduler,
            self._jorek_job_script() % "resume"
            if self.resume
            else self._jorek_job_script() % "run",
            self._param_set_register(),
            self._root_dir(),
            self.jorek_exec,
            JOREK_INPUT % "resume" if self.resume else JOREK_INPUT % "run",
            JOREK_JOB_OUT % "resume" if self.resume else JOREK_JOB_OUT % "run",
            JOREK_JOB_ERR % "resume" if self.resume else JOREK_JOB_ERR % "run",
            "jorek_resume" if self.resume else "jorek_run",
            "04:00:00",
        )

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        copy_tree(self.template_dir, self._working_dir(name), preserve_symlinks=True)

        self._write_jorek_input_files(name, self._param_namespace("jorek", param_set))
        if not self.resume and self.starwall_exec is not None:
            update_starwall_input_file(
                self._input_starwall(name),
                self._input_jorek_extrude_from(name),
                self._input_jorek_rz_psi(name),
                {
                    **self._param_namespace("starwall", param_set),
                    **self._starwall_params,
                },
            )

    def _write_jorek_input_files(self, name: str, param_set: dict) -> None:
        params = {**self._jorek_params, **param_set}
        if self._timestep is not None:
            params = {**params, "tstep_n": self._timestep}
        if self._timestep_count is not None:
            params = {**params, "nstep_n": self._timestep_count}

        if self.resume:
            write_resuming_jorek_input_files(self._input_jorek(name), params)
        else:
            write_fresh_jorek_input_files(self._input_jorek(name), params)
