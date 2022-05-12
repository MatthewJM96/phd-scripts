from abc import ABC, abstractmethod

from phdscripts.parameter_pack import ParameterPack


class Workflow(ABC):
    @abstractmethod
    def setup(self, param_pack: ParameterPack):
        pass

    @abstractmethod
    def run(self):
        pass
