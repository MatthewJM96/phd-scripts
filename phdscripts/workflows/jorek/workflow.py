"""
Contains the general workflow for Jorek runs.
"""

from .. import Workflow


class JorekWorkflow(Workflow):
    """
    General workflow for Jorek runs. Must be injected with specific logic for working
    directory building, and job script writing.
    """

    def __canonical_param_set_name(self, param_set: dict) -> str:
        pass

    def __build_job_script() -> str:
        pass

    def __build_working_directory(name: str, param_set: dict) -> None:
        pass
