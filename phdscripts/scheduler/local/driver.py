"""
Functions that run locally as if using a scheduler.
"""

from functools import partial
from multiprocessing import Pool
from os import environ
from subprocess import DEVNULL, run
from typing import Optional

from .. import SchedulerDriver


class LocalDriver(SchedulerDriver):
    @staticmethod
    def write_job_script(filename: str, contents: str, **kwargs):
        """
        Writes the job script with scheduler-specific parameterisation embedded.
        """
        with open(filename, "w") as f:
            f.write("#!/bin/env bash\n")

            f.write(contents)

    @staticmethod
    def write_array_job_script(filename: str, contents: str, **kwargs):
        """
        Writes the job script with scheduler-specific parameterisation embedded. In this
        case, array job-specific variables are set up:
            JOB_INDEX: the index of the specific job within the array.
        """
        with open(filename, "w") as f:
            f.write("#!/bin/env bash\n")

            f.write(contents)

    @staticmethod
    def _execute_local_script(index: int, job_script: str):
        env = environ.copy()
        env["JOB_INDEX"] = f"{index}"
        # TODO(Matthew): Probably want to optionally log the stdout/err streams.
        run(["/bin/bash", f"{job_script}"], env=env, stdout=DEVNULL, stderr=DEVNULL)

    @staticmethod
    def array_batch_jobs(
        job_script: str,
        job_count: int,
        jobs_parallel: int = 1,
        array_dependency: Optional[str] = None,
        blocking: bool = False,
    ) -> str:
        """
        Handles running an array of jobs in sequence, locally, as if submitted as an
        array job to a scheduler.
        """
        # TODO(Matthew): array_dependency unused. Use map_async and watch for completion
        #                of such coded array (this means coding this array ofc!).
        with Pool(jobs_parallel) as thread_pool:
            thread_pool.map(
                partial(LocalDriver._execute_local_script, job_script=job_script),
                list(range(0, job_count)),
            )
