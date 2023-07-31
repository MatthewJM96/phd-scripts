from phdscripts.util import replace_fortran_parameter


def write_jorek_input_file(
    input_filepath: str, output_filepath: str, params: dict
) -> None:
    """
    Writes a JOREK input file with parameters provided to this function being used to
    replace values in the original input file. This function allows specifying a
    different target as often we want multiple JOREK files.
    """

    with open(input_filepath, "r") as f:
        jorek_input = f.read()

    for param, value in params.items():
        # TODO(Matthew): this doesn't handle cases where a parameter has not been placed
        #                in the JOREK input file already, we may want to handle that
        #                explicitly (i.e. closing "/" line).
        jorek_input = replace_fortran_parameter(value, param, jorek_input)

    with open(output_filepath, "w") as f:
        f.write(jorek_input)


def write_fresh_jorek_input_files(filepath: str, params: dict) -> None:
    template_filepath = filepath % "template"
    init_filepath = filepath % "init"
    run_filepath = filepath % "run"

    write_jorek_input_file(
        template_filepath,
        init_filepath,
        {**params, "tstep_n": 1.0, "nstep_n": 0},
    )

    write_jorek_input_file(template_filepath, run_filepath, params)


def write_resuming_jorek_input_files(filepath: str, params: dict) -> None:
    template_filepath = filepath % "template"
    resume_filepath = filepath % "resume"

    write_jorek_input_file(
        template_filepath,
        resume_filepath,
        {**params, "restart": True},
    )
