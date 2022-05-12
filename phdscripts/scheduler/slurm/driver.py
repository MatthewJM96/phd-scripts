"""
Functions for interacting with Slurm scheduler.
"""

from os import popen

from .. import SchedulerDriver


class SlurmDriver(SchedulerDriver):
    def array_batch_jobs(job_script: str, job_count: int, jobs_parallel: int = 1):
        cmd = f"sbatch --array=0-{job_count-1}"

        if jobs_parallel > 0:
            cmd += f"%{jobs_parallel}"

        cmd += f" {job_script}"

        # TODO(Matthew): Do we want to capture any output?
        popen(cmd)
