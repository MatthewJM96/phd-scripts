"""
Entry for acquiring the appropriate driver.
"""


def get_scheduler_driver(scheduler: str):
    if scheduler == "slurm":
        from .slurm import array_batch_jobs
    else:
        raise ValueError(f"No scheduler, {scheduler}, recognised.")

    return {"array_batch_jobs": array_batch_jobs}
