# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameStone, GameGainItem, GamePickup
from game_state.game_event import dict2obj
from game_actors_and_handlers.base import BaseActor

logger = logging.getLogger(__name__)


class HarvestExchange(BaseActor):

    def perform_action(self):
        if self._get_game_state().get_state().gameMoney < 100000000:
            location_id = "isle_02"
            change_location_event = {
              "user": None,
              "locationId" : location_id,
              "type":"gameState",
              "action":"gameState",
              "objId": None
            }
            self._get_events_sender().send_game_events([change_location_event])
            print "na ostrov"
            craft = "3"
            exchange = self._get_item_reader().get("B_BUSINESS").crafts
            for one_item in exchange:
                if one_item.id == craft:
                    rose = one_item.materials[0].item
                    rose_count = one_item.materials[0].count
                    lily = one_item.materials[1].item
                    lily_count = one_item.materials[0].count
            storage = self._get_game_state().get_state().storageItems
            for item in storage:
                if item.item == rose:
                    storage_rose = item.count
                elif item.item == lily:
                    storage_lily = item.count
            for _ in range(5000):
                if storage_rose > rose_count and storage_lily > lily_count:
                    logger.info("Обмениваем партию Роз и Лилий")
                    event = {"itemId":craft,"objId":17249,"action":"craft","type":"item"}
                    self._get_events_sender().send_game_events([event])