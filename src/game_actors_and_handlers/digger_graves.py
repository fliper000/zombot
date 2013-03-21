# coding=utf-8
import logging
from game_state.game_types import GameDiggerGrave, GameDiggerGraveWithBrains,\
    GamePickItem, GameGainItem, GamePickup
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
