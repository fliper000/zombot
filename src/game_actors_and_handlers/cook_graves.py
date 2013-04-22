# coding=utf-8
import logging
from game_state.game_types import GameCookGrave, GameCookGraveWithBrains
from game_actors_and_handlers.workers import ResourcePicker
from game_actors_and_handlers.base import BaseActor

logger = logging.getLogger(__name__)


class BrewPicker(ResourcePicker):

    def get_worker_types(self):
        return [GameCookGrave.type, GameCookGraveWithBrains.type]
    
#        [{"itemId":"RECIPE_54","action":"cook","objId":26688,"type":"item"}]

class BrewSelecter(BaseActor):
    
    def get_worker_types(self):
        return [GameCookGrave.type, GameCookGraveWithBrains.type]
    
    def perform_action(self):
        cook_graves = self._get_game_location().get_all_objects_by_types(
            self.get_worker_types())
        free_workers = []
        for cook_grave in cook_graves:
            if len(cook_grave.pendingRecipes)<2:
                free_workers.append(cook_grave)
        for free_worker in free_workers:
            logger.info("Варим")
            self._get_events_sender().send_game_events([{"itemId":"RECIPE_02","action":"cook","objId":free_worker.id,"type":"item"}])
