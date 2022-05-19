"""
Functions that run locally as if using a scheduler.
"""

from functools import partial
from multiprocessing import Pool
from subprocess import run
from typing import Optional

from .. import SchedulerDriver


class LocalDriver(SchedulerDriver):
    @staticmethod
    def _execute_local_script(index: int, job_script: str):
        run([f"JOB_INDEX={index}", f"{job_script}"])

    @staticmethod
    def array_batch_jobs(
        job_script: str,
        job_count: int,
        jobs_parallel: int = 1,
        array_dependency: Optional[str] = None,
    ) -> str:
        """
        Handles running an array of jobs in sequence, locally, as if submitted as an
        array job to a scheduler.
        """
        # TODO(Matthew): array_dependency unused. Use map_async and watch for completion
        #                of such coded array (this means coding this array ofc!).
        with Pool(jobs_parallel) as thread_pool:
            thread_pool.map(
                partial(LocalDriver._execute_local_script(job_script=job_script)),
                list(range(0, job_count)),
            )
