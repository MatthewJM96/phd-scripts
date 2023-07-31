"""
Contains a staged workflow for Jorek runs, which reuses equilibrium and STARWALL runs
across time evolution runs of compatible parameterisations.

Currently, JOREK parameters on which equilibrim and STARWALL are grouped are:
    - plasma resistivity and viscosity parameters
        - eta, eta_ohmic, eta_T_dependent, T_max_eta, T_max_eta_ohm,
            visco, visco_T_dependent, visco_par, eta_num, visco_num, visco_par_num
    - wall resistivity
        - wall_resistivity_fact, wall_resistivity
    - particle and heat diffusion terms
        - D_perp, D_par, D_perp_imp, D_par_imp, ZK_perp, ZK_par, ZK_par_max,
            ZK_i_perp, ZK_e_perp, ZK_i_par, ZK_e_par, D_neutral_x, D_neutral_y,
            D_neutral_p, ZKpar_T_dependent, D_perp_num, Zk_perp_num, Dn_perp_num,
            Zk_i_perp_num, Zk_e_perp_num, use_sc, D_perp_sc_num, D_par_sc_num,
            Dn_pol_sc_num, Dn_p_sc_num, ZK_perp_sc_num, ZK_par_sc_num, ZK_i_perp_sc_num,
            ZK_i_par_sc_num, ZK_e_perp_sc_num, ZK_e_par_sc_num, ZK_prof_neg, ZK_par_neg,
            ZK_prof_neg_thresh, ZK_par_neg_thresh, ZK_e_prof_neg, ZK_e_par_neg,
            ZK_e_prof_neg_thresh, ZK_e_par_neg_thresh, ZK_i_prof_neg, ZK_i_par_neg,
            ZK_i_prof_neg_thresh, ZK_i_par_neg_thresh, D_imp_extra_R, D_imp_extra_Z,
            D_imp_extra_p, D_imp_extra_neg, D_imp_extra_neg_thresh
"""

from shutil import copytree, copy2, copystat
from functools import partial
from os import symlink
from os.path import isdir, join as join_path
from typing import Callable, Dict, Optional
from uuid import uuid4

from .. import Workflow, WorkflowSettings
from .input_file import (
    update_starwall_input_file,
    write_fresh_jorek_input_files,
    write_resuming_jorek_input_files,
)
from .job_script import write_job_script
from .starwall_invariants import STARWALL_INVARIANTS


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


class _JorekStagedTimeEvolWorkflow(Workflow):
    """
    Workflow for time evolution part of a staged workflow.
    """

    def __init__(
        self,
        run_id: str,
        settings: WorkflowSettings,
        template_dir: str,
        jorek_exec: str,
        timestep: Optional[int] = None,
        timestep_count: Optional[int] = None,
        jorek_params: dict = {},
    ):
        super().__init__(run_id, settings)

        self.template_dir = template_dir
        self.jorek_exec = jorek_exec
        self.timestep = timestep
        self.timestep_count = timestep_count
        self.jorek_params = jorek_params

    def run(self, run_after: Optional[str] = None) -> str:
        """
        Schedules jobs required to complete this workflow. Returns the ID of the
        last-scheduled jobs so as to allow other workflows to follow on from this
        workflow.
        """

        # JOREK Run
        return self.settings.scheduler.array_batch_jobs(
            self._jorek_job_script() % "resume",
            self._job_instances,
            self.settings.parallel_jobs,
            array_dependency=run_after,
            blocking=True,
        )

    def _input_jorek(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_INPUT)

    def _register_param_set(self, _: dict) -> str:
        # No registration needed, just return an ID to serve as name of the param set.
        return uuid4().hex

    def _jorek_job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_JOB_SCRIPT)

    def _write_job_scripts(self) -> None:
        ####################
        # JOREK Run/Resume #
        ####################
        write_job_script(
            self.machine,
            "jorek",
            self.run_id,
            self.settings.scheduler,
            self._jorek_job_script() % "resume",
            self._param_set_register(),
            self._root_dir(),
            self.jorek_exec,
            JOREK_INPUT % "resume",
            JOREK_JOB_OUT % "resume",
            JOREK_JOB_ERR % "resume",
            "jorek_resume",
            "04:00:00",
        )

    def __copy_except_starwall_response(src: str, dest: str) -> None:
        """
        Same as copy2 except for STARWALL's response file it creates a symlink.
        """

        if src[-21:] == "starwall-response.dat":
            symlink(src, dest)
            copystat(src, dest, follow_symlinks=False)
        else:
            copy2(src, dest)

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        copytree(
            self.template_dir,
            self._working_dir(name),
            symlinks=True,
            copy_function=self.__copy_except_starwall_response,
        )

        params = {**self._jorek_params, **self._param_namespace("jorek", param_set)}
        if self._timestep is not None:
            params = {**params, "tstep_n": self._timestep}
        if self._timestep_count is not None:
            params = {**params, "nstep_n": self._timestep_count}

        write_resuming_jorek_input_files(self._input_jorek(name), params)


class StarwallInvariantClass:
    """
    Stores details about a STARWALL invariant class.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._param_sets = []
        self._subworkflow = None

    def append_param_set(self, param_set: dict):
        self._param_sets.append(param_set)

    def setup(self, init_workflow: Callable[[None], _JorekStagedTimeEvolWorkflow]):
        # We only need to specify the template directory here, everything else is the
        # same for all invariant classes.
        self._subworkflow: _JorekStagedTimeEvolWorkflow = init_workflow(
            template_dir=self._working_dir(self.name)
        )

        self._subworkflow.setup(self._param_sets)

    def run(self, run_after: Optional[str] = None):
        if self._subworkflow is None:
            return

        self._subworkflow.run(run_after)


class JorekStagedWorkflow(Workflow):
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
        self._starwall_invariant_classes: Dict[str, StarwallInvariantClass] = {}

    def run(self, run_after: Optional[str] = None) -> str:
        """
        Schedules jobs required to complete this workflow. Returns the ID of the
        last-scheduled jobs so as to allow other workflows to follow on from this
        workflow.
        """
        if not self.resume and self.starwall_exec is not None:
            # JOREK Initialisation
            jorek_init_id = self.settings.scheduler.array_batch_jobs(
                self._jorek_job_script() % "init",
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

        for starwall_invariant_class in self._starwall_invariant_classes.values():
            starwall_invariant_class.run(starwall_id)

    def _starwall_variant_params(self, param_set: dict) -> dict:
        """
        Separates out JOREK parameters on which STARWALL response varies.
        """

        jorek_params = self._param_namespace("jorek", param_set)

        return {
            k: v for k, v in jorek_params.enumerate() if k not in STARWALL_INVARIANTS
        }

    def _starwall_invariant_params(self, param_set: dict) -> dict:
        """
        Separates out JOREK parameters on which STARWALL response does not vary.
        """

        jorek_params = self._param_namespace("jorek", param_set)

        return {k: v for k, v in jorek_params.enumerate() if k in STARWALL_INVARIANTS}

    def _input_jorek(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_INPUT)

    def _input_starwall(self, name: str) -> str:
        return join_path(self._working_dir(name), STARWALL_INPUT)

    def _input_jorek_rz_psi(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_RZPSI_INPUT)

    def _input_jorek_extrude_from(self, name: str) -> str:
        return join_path(self._working_dir(name), JOREK_EXTRUDE_FROM_INPUT)

    def _register_param_set(self, param_set: dict) -> str:
        """
        Each param set has a shared canonical name with all other parmaeter sets that
        vary from it in parameters considered to be STARWALL invariants. We here look
        for if a name has already been assigned for the class of param sets this current
        param set belongs, and if not names a new one.
        """

        variant_params = self._starwall_variant_params(param_set)

        if str(variant_params) not in self._starwall_invariant_classes:
            self._starwall_invariant_classes[
                str(variant_params)
            ] = StarwallInvariantClass(uuid4().hex)

        starwall_invariant_class = self._starwall_invariant_classes[str(variant_params)]

        starwall_invariant_class.append_param_set(param_set)

        return starwall_invariant_class.name

    def _complete_setup(self) -> None:
        """
        Now that we have registered every parameter set, separating them into their
        STARWALL-invariant classes, set up corresponding workflows
        """

        for starwall_invariant_class in self._starwall_invariant_classes.values():
            starwall_invariant_class.setup(
                partial(
                    _JorekStagedTimeEvolWorkflow,
                    run_id=join_path(self.run_id, "time_evol"),
                    settings=self.settings,
                    jorek_exec=self.jorek_exec,
                    timestep=self.timestep,
                    timestep_count=self.timestep_count,
                    jorek_params=self.jorek_params,
                )
            )

    def _jorek_job_script(self) -> str:
        return join_path(self._root_dir(), JOREK_JOB_SCRIPT)

    def _starwall_job_script(self) -> str:
        return join_path(self._root_dir(), STARWALL_JOB_SCRIPT)

    def _write_job_scripts(self) -> None:
        if self.resume:
            return

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

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        # Only need to build a working directory for the first parameter set for any
        # STARWALL-invariant class of parameterisations.
        if isdir(self._working_dir(name)):
            return

        copytree(self.template_dir, self._working_dir(name), symlinks=True)

        self._write_jorek_input_files(name, self._param_namespace("jorek", param_set))
        if not self.resume and self.starwall_exec is not None:
            update_starwall_input_file(
                self._input_starwall(name),
                self._input_jorek_extrude_from(name),
                self._input_jorek_rz_psi(name),
                {
                    **self._starwall_params,
                    **self._param_namespace("starwall", param_set),
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
