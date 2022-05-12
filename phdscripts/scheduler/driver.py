from abc import ABC, abstractclassmethod


class SchedulerDriver(ABC):
    @abstractclassmethod
    def array_batch_jobs(job_script: str, job_count: int, jobs_parallel: int = 1):
        pass
