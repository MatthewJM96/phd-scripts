"""
Functions for interacting with Slurm scheduler.
"""

from subprocess import PIPE, run
from typing import Optional

from .. import SchedulerDriver


class SlurmDriver(SchedulerDriver):
    @staticmethod
    def write_job_script(filename: str, contents: str, **kwargs):
        """
        Writes the job script with scheduler-specific parameterisation embedded.
        """
        with open(filename, "w") as f:
            f.write("#!/bin/env bash\n")

            for key, val in kwargs.items():
                f.write(f"#SBATCH --{key.replace('_', '-')}={val}")
            f.write("\n")

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

            for key, val in kwargs.items():
                f.write(f"#SBATCH --{key.replace('_', '-')}={val}")
            f.write("\n")

            f.write("export JOB_INDEX=$SLURM_ARRAY_TASK_ID\n")

            f.write(contents)

    @staticmethod
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
            cmd.append(f"--dependency=aftercorr:{array_dependency}")

        cmd.append(f"{job_script}")

        pipe = run(cmd, stdout=PIPE)

        return pipe.stdout.decode(encoding="UTF8").replace("\n", "")
