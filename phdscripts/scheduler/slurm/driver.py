"""
Functions for interacting with Slurm scheduler.
"""

from subprocess import run
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
        cmd = ["sbatch", "--parsable"]

        array_flag = f"--array=0-{job_count-1}"
        if jobs_parallel > 0:
            array_flag += f"%{jobs_parallel}"
        cmd.append(array_flag)

        if array_dependency is not None:
            cmd.append(f"--dependency=aftercorr:${array_dependency}")

        cmd.append(f"{job_script}")

        pipe = run(cmd, capture_output=True)

        return pipe.stdout
