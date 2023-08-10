from json import loads, dumps
from typing import Dict, List, Union

from . import ParameterPack


def write_parameter_pack(param_pack: Union[ParameterPack, List[dict]], filepath: str):
    """
    Serialises a parameter pack, writing a JSON dictionary for each realisation of the
    pack on separate lines.
    """

    serialised = ""
    for realisation in param_pack:
        serialised += f"{dumps(realisation)}\n"

    with open(filepath, "w") as f:
        f.write(serialised)


def write_named_parameter_sets(param_sets: Dict[str, dict], filepath: str):
    """
    Serialises a parameter pack, writing each param set's name and corresponding JSON
    dictionary on each line. Essentially just wrapping dumps.
    """

    serialised = ""
    for name, realisation in param_sets.items():
        serialised += f"{name}, {dumps(realisation)}\n"

    with open(filepath, "w") as f:
        f.write(serialised)


def read_parameter_pack(filepath: str) -> List[dict]:
    """
    Deserialises a parameter pack, reading each line as a separate realisation stored
    as a JSON dictionary.
    """

    realisations = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            realisations.append(loads(line))

    return realisations


def read_named_parameter_sets(filepath: str) -> Dict[str, dict]:
    """
    Deserialises a parameter pack, reading each param set's name and corresponding JSON
    dictionary on each line. Essentially just wrapping loads.
    """

    realisations = {}
    with open(filepath, "r") as f:
        for line in f.readlines():
            parts = line.split(",", maxsplit=1)

            # Should always be two parts, first being name of realisation and second the
            # realisation itself.
            assert len(parts) == 2

            realisations[parts[0].strip()] = loads(parts[1])

    return realisations
