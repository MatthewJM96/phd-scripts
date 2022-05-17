from abc import ABC, abstractclassmethod
from typing import Optional


class SchedulerDriver(ABC):
    @abstractclassmethod
    def array_batch_jobs(
        job_script: str,
        job_count: int,
        jobs_parallel: int = 1,
        array_dependency: Optional[str] = None,
    ) -> str:
        """
        Schedules an array of jobs and sends them to the scheduler to be ran in batches.
        The job array ID is returned by this function.
        """
        pass
