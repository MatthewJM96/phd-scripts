"""
Abstract definition of a workflow.
"""

import logging
from abc import ABC, abstractmethod
from os import makedirs
from os.path import isdir
from os.path import join as join_path
from re import fullmatch
from typing import Dict, Optional

from phdscripts.parameter_pack import ParameterPack
from phdscripts.scheduler import SchedulerDriver

PARAM_SET_REGISTER_FILENAME = "param_set_register"


class WorkflowSettings:
    def __init__(self, base_dir: str, parallel_jobs: int, scheduler: SchedulerDriver):
        self.base_dir = base_dir
        self.scheduler = scheduler
        self.parallel_jobs = parallel_jobs


class Workflow(ABC):
    """
    Abstract definition of a workflow.
    """

    def __init__(self, run_id: str, settings: WorkflowSettings):
        self.settings = settings

        if not self._are_settings_good():
            raise ValueError(
                (
                    f"Settings provided for run {run_id} are invalid.\n"
                    f"Settings are:\n{settings}"
                )
            )

        if not fullmatch(r"[0-9A-Za-z_]+", run_id):
            msg = (
                f"Provided run ID is invalid: {run_id}.\n"
                "Run ID must be alphanumeric."
            )

            logging.error(msg)
            raise ValueError(msg)

        self.run_id = run_id

    def setup(self, param_pack: ParameterPack):
        self._build_root_working_directory()

        self._write_job_scripts()

        param_sets: Dict[str, str] = {}

        self._job_instances = 0
        for param_set in param_pack:
            name = self._canonical_param_set_name(param_set)

            param_sets[name] = str(param_set)

            self._build_working_directory(name, param_set)
            self._job_instances += 1

        self._write_param_set_register(param_sets)

    @abstractmethod
    def run(self, run_after: Optional[str] = None) -> str:
        pass

    def _are_settings_good(self) -> bool:
        if isdir(self.settings.base_dir):
            logging.warn(
                f"Base directory of workflow already exists:\n{self.settings.base_dir}"
            )

        return True

    def _root_dir(self) -> str:
        return join_path(self.settings.base_dir, self.run_id)

    def _param_set_register(self) -> str:
        return join_path(self._root_dir(), PARAM_SET_REGISTER_FILENAME)

    def _working_dir(self, name: str) -> str:
        return join_path(self._root_dir(), name)

    def _build_root_working_directory(self) -> None:
        makedirs(self._root_dir(), exist_ok=True)

    def _write_param_set_register(self, param_sets: Dict[str, str]) -> None:
        param_set_register = ""
        for name, param_set in param_sets.items():
            param_set_register += name + ', "' + param_set + '"\n'

        with open(self._param_set_register(), "w") as f:
            f.write(param_set_register)

    @abstractmethod
    def _canonical_param_set_name(self, param_set: dict) -> str:
        pass

    @abstractmethod
    def _write_job_scripts(self) -> None:
        pass

    @abstractmethod
    def _build_working_directory(self, name: str, param_set: dict) -> None:
        pass
