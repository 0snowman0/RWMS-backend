from abc import ABC, abstractmethod


class IBehaviorLoader(ABC):

    @abstractmethod
    def load(
        self,
        package_name: str,
    ) -> None:
        pass