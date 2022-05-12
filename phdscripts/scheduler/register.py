"""
Register for schedulers.
"""

from .driver import SchedulerDriver
from .slurm import SlurmDriver


class SchedulerRegister:
    def __init__(self):
        self.schedulers = {}

    def register_scheduler(
        self, scheduler_name: str, scheduler: SchedulerDriver
    ) -> None:
        if scheduler_name in self.schedulers:
            raise ValueError(
                f"A scheduler with the name {scheduler_name} is already registered."
            )

        self.schedulers[scheduler_name] = scheduler

    def has_scheduler(self, scheduler_name: str) -> bool:
        return scheduler_name in self.schedulers

    def get_scheduler(self, scheduler_name: str) -> SchedulerDriver:
        if scheduler_name not in self.schedulers:
            raise ValueError(
                f"No scheduler is registered with the name {scheduler_name}."
            )

        return self.schedulers[scheduler_name]()


def get_default_register() -> SchedulerRegister:
    register = SchedulerRegister()

    register.register_scheduler("slurm", SlurmDriver)

    return register
