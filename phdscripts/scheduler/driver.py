from abc import ABC, abstractmethod
from typing import Optional


class SchedulerDriver(ABC):
    @staticmethod
    @abstractmethod
    def write_job_script(filename: str, contents: str, **kwargs):
        """
        Writes the job script with scheduler-specific parameterisation embedded.
        """
        pass

    @staticmethod
    @abstractmethod
    def write_array_job_script(filename: str, contents: str, **kwargs):
        """
        Writes the job script with scheduler-specific parameterisation embedded. In this
        case, array job-specific variables are set up:
            JOB_INDEX: the index of the specific job within the array.
        """
        pass

    @staticmethod
    @abstractmethod
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
