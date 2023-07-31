"""
Contains the general workflow for Mishka runs.
"""

from shutil import copytree
from os.path import join as join_path
from typing import Optional

from phdscripts.util import (  # replace_parameterised_decimal_number_in_list,
    convert_standard_to_fortran_number,
    has_parameterised_fortran_bool,
    has_parameterised_fortran_number,
    replace_parameterised_fortran_bool,
    replace_parameterised_fortran_number,
)

from .. import Workflow, WorkflowSettings
from .job_script import write_scene_job_script

MISHKA_JOB_SCRIPT = "scene.job.run"
MISHKA_JOB_OUT = "scene.job.out"
MISHKA_JOB_ERR = "scene.job.err"
MISHKA_TEMPLATE_INPUT = "fort.10"
MISHKA_INPUT = "fort.10"


class SceneWorkflow(Workflow):
    """
    Workflow for SCENE runs.
    """

    def __init__(
        self,
        run_id: str,
        settings: WorkflowSettings,
        template_dir: str,
        scene_exec: str,
        scene_params: dict = {},
    ):
        super().__init__(run_id, settings)

        self._template_dir = template_dir
        self._scene_exec = scene_exec
        self._scene_params = scene_params

    def run(self, run_after: Optional[str] = None) -> str:
        """
        Schedules jobs required to complete this workflow. Returns the ID of the
        last-scheduled jobs so as to allow other workflows to follow on from this
        workflow.
        """

        # Mishka
        return self.settings.scheduler.array_batch_jobs(
            self._scene_job_script(),
            self._job_instances,
            self.settings.parallel_jobs,
            array_dependency=run_after,
        )

    def _input_scene_template(self, name: str) -> str:
        return join_path(self._working_dir(name), MISHKA_TEMPLATE_INPUT)

    def _input_scene(self, name: str) -> str:
        return join_path(self._working_dir(name), MISHKA_INPUT)

    def _register_param_set(self, param_set: dict) -> str:
        # TODO(Matthew): Do we prefer to use something like uuid? This might make
        #                rather ridiculous directory names. Could provide a script
        #                that lists (with filtering/sorting) the runs and will move
        #                command line to the apporpriate directory by index choice.

        canonical_param_set_name = ""

        for name, value in param_set.items():
            canonical_param_set_name += name + "_" + str(value) + "___"

        return canonical_param_set_name

    def _scene_job_script(self) -> str:
        return join_path(self._root_dir(), MISHKA_JOB_SCRIPT)

    def _write_job_scripts(self) -> None:
        ##########
        # Mishka #
        ##########
        write_scene_job_script(
            self.settings.scheduler,
            self._scene_job_script(),
            self._param_set_register(),
            self._root_dir(),
            self._scene_exec,
            MISHKA_JOB_OUT,
            MISHKA_JOB_ERR,
        )

    def _build_working_directory(self, name: str, param_set: dict) -> None:
        copytree(self._template_dir, self._working_dir(name), symlinks=True)

        params = {**param_set, **self._scene_params}

        self._write_scene_input_file(name, self._input_scene(name), params)

    def _write_scene_input_file(
        self, name: str, output_filepath: str, param_set: dict
    ) -> None:
        with open(self._input_scene_template(name), "r") as f:
            scene_input = f.read()

        # TODO(Matthew): Handle species information at end of SCENE dat file.

        for param, value in param_set.items():
            if isinstance(value, bool):
                if has_parameterised_fortran_bool(param, scene_input):
                    scene_input = replace_parameterised_fortran_bool(
                        param, value, scene_input, intermediate=" *"
                    )
            elif isinstance(value, (float, int)):
                if has_parameterised_fortran_number(param, scene_input):
                    scene_input = replace_parameterised_fortran_number(
                        param, value, scene_input, intermediate=" *"
                    )
                else:
                    # TODO(Matthew): this actually breaks for now as there is a
                    #                structure to Mishka inputs that we need to handle
                    #                (i.e. closing "&END" line).
                    scene_input += (
                        f"\n{param} = "
                        f"{convert_standard_to_fortran_number(str(value))}"
                    )

        with open(output_filepath, "w") as f:
            f.write(scene_input)
