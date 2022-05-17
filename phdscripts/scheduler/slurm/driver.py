"""
Functions for interacting with Slurm scheduler.
"""

from os import popen
from typing import Optional

from .. import SchedulerDriver


class SlurmDriver(SchedulerDriver):
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
        cmd = f"sbatch --parsable --array=0-{job_count-1}"

        if jobs_parallel > 0:
            cmd += f"%{jobs_parallel}"

        if array_dependency is not None:
            cmd += f" --dependency=aftercorr:${array_dependency}"

        cmd += f" {job_script}"

        pipe = popen(cmd)

        return pipe.readline()
