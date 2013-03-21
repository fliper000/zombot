# coding=utf-8
import logging
from game_state.game_types import GameDiggerGrave, GameDiggerGraveWithBrains
from game_actors_and_handlers.workers import ResourcePicker

logger = logging.getLogger(__name__)

class BagsPicker(ResourcePicker):

    def get_worker_types(self):
        return [GameDiggerGrave.type, GameDiggerGraveWithBrains.type]
    
    def perform_action(self):
        graves = self._get_game_location().get_all_objects_by_types(
                            self.get_worker_types())
        for grave in graves:
            if grave.materials:
                logger.info("Собираем мешки " + str(grave.materials) + ' шт.')
            for _ in range(grave.materials):
                self._pick_material(grave, None)
                grave.materials -= 1

class TimeGainEventHandler(object):
    '''
    {"type":"timeGain","action":"start","objId":-3650,"gainDone":418}]
    '''

    def __init__(self, item_reader, game_location,
                  timer):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__timer = timer

    def handler(self, event_to_handle):
        gameObject = self.__game_location.get_object_by_id(
            event_to_handle.objId
        )
        if gameObject.materials < 3:
            gameObject.materials += 1

