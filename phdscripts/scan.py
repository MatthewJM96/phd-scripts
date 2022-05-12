"""
Handles parameter scanning based on a parameter pack.
"""

from typing import Callable, Tuple

from .parameter_pack import ParameterPack
from .scheduler import get_scheduler_driver


class ScanSettings:
    def __init__(self, scheduler: str = "slurm", parallel_jobs: int = 1):
        self.scheduler = get_scheduler_driver(scheduler)
        self.parallel_jobs = parallel_jobs


class ParameterScanner:
    def __init__(
        self,
        param_pack: ParameterPack,
        scan_settings: ScanSettings,
        setup: Callable[[ParameterPack], Tuple[str, int]],
    ):
        self.param_pack = param_pack
        self.scan_settings = scan_settings
        self.setup = setup

    def run(self):
        # Set up list of parameter sets to run & assign canonicalised names.
        # Set up directories by canonicalised name.
        job_script, job_count = self.setup(self.param_pack)

        # Submit jobs (using array batching - index into list with job array ID).
        self.scheduler["array_batch_jobs"](
            job_script, job_count, self.setup.parallel_jobs
        )
