# coding=utf-8
import logging
from game_state.game_types import GamePlant, GameFruitTree, GameSlag,\
    GameDigItem, GamePickItem, GameBuyItem
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
            self._pick_harvest(harvestItem)

        slags = self.__game_location.get_all_objects_by_type(GameSlag.type)
        for slag in list(slags):
            item = self.__item_reader.get(slag.item)
            logger.info(u"Копаем '" + item.name + "' " + str(slag.id) +
                        u" по координатам (" +
                        str(slag.x) + ", " + str(slag.y) + u")")
            dig_event = GameDigItem(slag.id)
            self.__events_sender.send_game_events([dig_event])
            # convert slag to ground
            slag.type = 'base'
            slag.item = '@GROUND'

    def _pick_harvest(self, harvestItem):
        if self.__timer.has_elapsed(harvestItem.jobFinishTime):
            item = self.__item_reader.get(harvestItem.item)
            logger.info(u"Собираем '" + item.name + "' " +
                        str(harvestItem.id) +
                        u" по координатам (" +
                        str(harvestItem.x) + u", " + str(harvestItem.y) + u")")
            pick_event = GamePickItem(objId=harvestItem.id)
            self.__events_sender.send_game_events([pick_event])
            if harvestItem.type == GamePlant.type:
                # convert plant to slag
                harvestItem.type = GameSlag.type
                harvestItem.item = GameSlag(0L, 0L, 0L).item
            elif harvestItem.type == GameFruitTree.type:
                harvestItem.fruitingCount -= 1
                if harvestItem.fruitingCount == 0:
                    # remove fruit tree
                    self.__game_location.remove_object_by_id(harvestItem.id)
                    # harvestItem.type = GamePickItem.type
                    # TODO convert to pickup box
                    # convert tree to pick item


class SeederBot(object):

    def __init__(self, item_reader, game_location,
                  events_sender, selected_seed):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__events_sender = events_sender
        self.__selected_seed = selected_seed

    def perform_action(self):
        grounds = self.__game_location.get_all_objects_by_type('ground')
        for ground in list(grounds):
            item = self.__item_reader.get(ground.item)
            seed_item = self.__item_reader.get(self.__selected_seed)
            logger.info(u"Сеем '" + seed_item.name +
                        u"' на '" + item.name + u"' " +
                        str(ground.id) +
                        u" по координатам (" +
                        str(ground.x) + u", " + str(ground.y) + u")")
            buy_event = GameBuyItem(unicode(seed_item.id),
                                    ground.id,
                                    ground.y, ground.x)
            self.__events_sender.send_game_events([buy_event])
            ground.type = u'plant'
            ground.item = unicode(seed_item.id)


class PlantEventHandler(object):
    def __init__(self, game_location):
        self.__game_location = game_location

    def handle(self, event_to_handle):
        gameObject = self.__game_location.get_object_by_id(
            event_to_handle.objId
        )
        if gameObject is None:
            logger.critical("OMG! No such object")
        gameObject.fertilized = True
        logger.info('Plant fertilized')
        gameObject.jobFinishTime = event_to_handle.jobFinishTime
        gameObject.jobStartTime = event_to_handle.jobStartTime
