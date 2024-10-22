from abc import ABC, abstractmethod
from logging import Logger


class MapProcessor(ABC):
    def __init__(self, logger: Logger):
        self.logger = logger

    @abstractmethod
    def get_coordinates(self, location: str) -> tuple[float, float]:
        ...

    @abstractmethod
    def get_route(self, start: str, finish: str) -> dict:
        ...
