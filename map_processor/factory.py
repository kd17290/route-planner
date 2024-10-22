from logging import Logger

from map_processor.base import MapProcessor
from map_processor.enum import MapProcessorType
from map_processor.map_quest import MapQuestClient


class MapProcessorFactory:
    @staticmethod
    def create_processor(
        processor_type: MapProcessorType, logger: Logger
    ) -> MapProcessor:
        match processor_type:
            case MapProcessorType.map_quest:
                return MapQuestClient(logger)
            case _:
                raise ValueError(f"Invalid map processor type: {processor_type}")
