from typing import Dict

from ... import ParameterPack
from .. import Workflow


class JorekWorkflow(Workflow):
    def setup(self, param_pack: ParameterPack):
        param_sets: Dict[str, str] = {}

        for param_set in param_pack:
            name = self.__canonical_param_set_name(param_set)

            param_sets[name] = str(param_set)

            self.__build_working_directory(name, param_set)

    def run(self):
        pass

    def __canonical_param_set_name(self, param_set: dict) -> str:
        pass

    def __build_working_directory(self, name: str, param_set: dict) -> None:
        pass
