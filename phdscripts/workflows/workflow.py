"""
Abstract definition of a workflow.
"""

import logging
from abc import ABC, abstractmethod
from os import makedirs
from os.path import isdir
from os.path import join as join_path
from re import fullmatch
from typing import Dict

from phdscripts.parameter_pack import ParameterPack


class WorkflowSettings:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir


class Workflow(ABC):
    """
    Abstract definition of a workflow.
    """

    def __init__(self, run_id: str, settings: WorkflowSettings):
        if not self.__are_settings_good(settings):
            raise ValueError(
                (
                    f"Settings provided for run {run_id} are invalid.\n"
                    f"Settings are:\n{settings}"
                )
            )

        self.settings = settings

        if fullmatch(r"[0-9A-Za-z]+", run_id):
            msg = (
                f"Provided run ID is invalid: {run_id}.\n"
                "Run ID must be alphanumeric."
            )

            logging.error(msg)
            raise ValueError(msg)

        self.run_id = run_id

    def setup(self, param_pack: ParameterPack):
        self.__build_root_working_directory()

        self.__write_job_script()

        param_sets: Dict[str, str] = {}

        for param_set in param_pack:
            name = self.__canonical_param_set_name(param_set)

            param_sets[name] = str(param_set)

            self.__build_working_directory(name, param_set)

        self.__write_param_set_register(param_sets)

    def run(self):
        pass

    def __are_settings_good(self) -> bool:
        if isdir(self.base_dir):
            logging.warn(f"Base directory of workflow already exists:\n{self.base_dir}")

        return True

    def __root_dir(self) -> str:
        return join_path(self.settings.base_dir, self.run_id)

    def __build_root_working_directory(self) -> None:
        makedirs(self.__root_dir(), exist_ok=True)

    def __write_job_script(self) -> None:
        job_script = self.__build_job_script()

        job_script_filepath = join_path(self.__root_dir(), ".job")
        with open(job_script_filepath, "w") as f:
            f.write(job_script)

    def __write_param_set_register(name: str, param_set: dict) -> None:
        pass

    @abstractmethod
    def __canonical_param_set_name(self, param_set: dict) -> str:
        pass

    @abstractmethod
    def __build_job_script() -> str:
        pass

    @abstractmethod
    def __build_working_directory(name: str, param_set: dict) -> None:
        pass
