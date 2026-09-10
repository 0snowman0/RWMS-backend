from abc import ABC, abstractmethod


class IHandlerLoader(ABC):

    @abstractmethod
    def load(
        self,
        package_name: str,
    ) -> None:
        pass