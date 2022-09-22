from phdscripts.scheduler import SchedulerDriver


def write_mishka_job_script(
    scheduler: SchedulerDriver,
    job_script_filename: str,
    register: str,
    root_dir: str,
    mishka_exec: str,
    output_filename: str,
    error_filename: str,
):
    scheduler.write_array_job_script(
        job_script_filename,
        f"""
### Set environment
source $HOME/.loaders/load_2017_env.sh
source $HOME/.loaders/load_nov1_21_jorek.sh

# Obtain working directory name from reigster.
line_num=$((${{JOB_INDEX}} + 1))
param_set="$(sed -n ${{line_num}}p {register})"
IFS=',' read -ra param_set_parts <<< "$param_set"
param_set_name="${{param_set_parts[0]}}"

cd {root_dir}/${{param_set_name}}

{mishka_exec} >{output_filename} 2>{error_filename}
""",
    )
