from abc import ABC, abstractmethod

from Core.Application.Mapping.mapper import Mapper


class MappingProfile(ABC):

    @abstractmethod
    def configure(
        self,
        mapper: Mapper,
    ) -> None:
        pass