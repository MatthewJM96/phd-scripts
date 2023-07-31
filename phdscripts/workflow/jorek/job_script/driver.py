def write_job_script(machine: str, software: str, *args, **kwargs):
    if machine.lower() == "marconi":
        from marconi import write_jorek_job_script, write_starwall_job_script

        if software.lower() == "jorek":
            write_jorek_job_script(*args, **kwargs)
        elif software.lower() == "starwall":
            write_starwall_job_script(*args, **kwargs)
    elif machine.lower() == "csd3":
        from csd3 import write_jorek_job_script, write_starwall_job_script

        if software.lower() == "jorek":
            write_jorek_job_script(*args, **kwargs)
        elif software.lower() == "starwall":
            write_starwall_job_script(*args, **kwargs)
