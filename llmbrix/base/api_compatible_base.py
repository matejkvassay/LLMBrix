from abc import ABC, abstractmethod


class ApiCompatibleBase(ABC):
    @abstractmethod
    def api_dict(self) -> dict:
        pass
