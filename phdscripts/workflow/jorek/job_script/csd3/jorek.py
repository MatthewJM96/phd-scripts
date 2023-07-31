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
):
    scheduler.write_array_job_script(
        job_script_filename,
        f"""
### Set environment
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

export OMP_NUM_THREADS=8
export I_MPI_PIN_MODE=lib

export KMP_AFFINITY=compact,verbose # These three lines were suggested by Tamas Feher
export I_MPI_PIN_DOMAIN=auto        # and have been useful for decreasing computation
export KMP_HW_SUBSET=1t             # time on KNL

# Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {register})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

cd {root_dir}/${{param_set_name}}

mpirun -n 2                                \\
    {jorek_exec} < {input_filename} \\
        | tee log.{log_name}
        """,
        job_name=f"{run_id}_{log_name}",
        partition="skl_fua_prod",
        time=walltime,
        nodes=2,
        ntasks_per_node=1,
        mem="177GB",
        output=f"{root_dir}/%x.%a.{output_filename}",
        error=f"{root_dir}/%x.%a.{error_filename}",
        account="FUA36_UKAEA_ML",
    )
