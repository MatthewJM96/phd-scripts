from phdscripts.scheduler import SchedulerDriver


def write_jorek_job_script(
    run_id: str,
    scheduler: SchedulerDriver,
    job_script_filename: str,
    register: str,
    root_dir: str,
    jorek_exec: str,
    input_filename: str,
    output_filename: str,
    error_filename: str,
    log_name: str,
    walltime: str,
    **kwargs,
):
    # Set some defaults for nodes, CPUs per task, and number of tasks if these weren't
    # provided.
    if "nodes" not in kwargs:
        kwargs = {**kwargs, "nodes": 4}
    if "cpus_per_task" not in kwargs:
        kwargs = {**kwargs, "cpus_per_task": 7}
    if "ntasks" not in kwargs:
        kwargs = {**kwargs, "ntasks": 32}

    nodes = kwargs["nodes"]
    ntasks = kwargs["ntasks"]
    cpus_per_task = kwargs["cpus_per_task"]

    scheduler.write_array_job_script(
        job_script_filename,
        f"""
### Set environment
. /etc/profile.d/modules.sh
source $HOME/load_jorek_modules.sh

export OMP_NUM_THREADS={cpus_per_task}
export I_MPI_PIN_DOMAIN=omp:compact
export I_MPI_PIN_ORDER=scatter

### Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {register})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

cd {root_dir}/${{param_set_name}}

restart = "jorek_restart.h5"
if [ -L "$restart" ]; then
    target=$(readlink "$restart")
    rm "$restart"
    cp "$target" "$restart"
fi

mpirun -ppn {int(ntasks / nodes)} -np {ntasks} \\
    {jorek_exec} < {input_filename}       \\
        | tee log.{log_name}
        """,
        job_name=f"{run_id}_{log_name}",
        account="UKAEA-AP002-CPU",
        partition="cclake",
        output=f"{root_dir}/%x.%a.{output_filename}",
        error=f"{root_dir}/%x.%a.{error_filename}",
        time=walltime,
        **kwargs,
    )
