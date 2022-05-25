"""
Register for workflows.
"""

from .workflow import Workflow


class WorkflowRegister:
    def __init__(self):
        self.workflows = {}

    def register_workflow(self, workflow_name: str, workflow: Workflow) -> None:
        if workflow_name in self.workflows:
            raise ValueError(
                f"A workflow with the name {workflow_name} is already registered."
            )

        self.workflows[workflow_name] = workflow

    def has_workflow(self, workflow_name: str) -> bool:
        return workflow_name in self.workflows

    def get_workflow(self, workflow_name: str) -> Workflow:
        if workflow_name not in self.workflows:
            raise ValueError(
                f"No workflow is registered with the name {workflow_name}."
            )

        return self.workflows[workflow_name]


def get_default_register() -> WorkflowRegister:
    register = WorkflowRegister()

    return register
