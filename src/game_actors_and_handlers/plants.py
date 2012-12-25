# coding=utf-8
import logging
from game_state.game_types import GamePlant, GameFruitTree, GameSlag,\
    GameDigItem, GamePickItem
logger = logging.getLogger(__name__)


class HarvesterBot():
    def __init__(self, item_reader, game_location,
                  events_sender, timer):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__events_sender = events_sender
        self.__timer = timer

    def perform_action(self):
        plants = self.__game_location.get_all_objects_by_type(GamePlant.type)
        trees = self.__game_location.get_all_objects_by_type(
            GameFruitTree.type)
        harvestItems = plants + trees
        for harvestItem in list(harvestItems):
            self.pickHarvest(harvestItem)

        slags = self.__game_location.get_all_objects_by_type(GameSlag.type)
        for slag in list(slags):
            item = self.__item_reader.get(slag.item)
            logger.info(u"Копаем '" + item.name + "' " + str(slag.id) +
                        u" по координатам (" +
                        str(slag.x) + ", " + str(slag.y) + u")")
            dig_event = GameDigItem(slag.id)
            self.__events_sender.sendGameEvents([dig_event])
            # convert slag to ground
            slag.type = 'base'
            slag.item = '@GROUND'

    def pickHarvest(self, harvestItem):
        if self.__timer.has_elapsed(harvestItem.jobFinishTime):
            item = self.__item_reader.get(harvestItem.item)
            logger.info(u"Собираем '" + item.name + "' " +
                        str(harvestItem.id) +
                        u" по координатам (" +
                        str(harvestItem.x) + u", " + str(harvestItem.y) + u")")
            pick_event = GamePickItem(objId=harvestItem.id)
            self.__events_sender.sendGameEvents([pick_event])
            if harvestItem.type == GamePlant.type:
                # convert plant to slag
                harvestItem.type = GameSlag(0L, 0L, 0L).type
                harvestItem.item = GameSlag(0L, 0L, 0L).item
            elif harvestItem.type == GameFruitTree.type:
                harvestItem.fruitingCount -= 1
                if harvestItem.fruitingCount == 0:
                    # convert tree to pick item
                    harvestItem.type = GamePickItem.type
