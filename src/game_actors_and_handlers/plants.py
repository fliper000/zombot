# coding=utf-8
import logging
from game_state.game_types import GamePlant, GameFruitTree, GameSlag,\
    GameDigItem, GamePickItem, GameBuyItem
from game_actors_and_handlers.base import BaseActor
from game_state.item_reader import GameSeedReader

logger = logging.getLogger(__name__)


class HarvesterBot(BaseActor):

    def perform_action(self):
        plants = self._get_game_location().get_all_objects_by_type(
            GamePlant.type)
        trees = self._get_game_location().get_all_objects_by_type(
            GameFruitTree.type)
        harvestItems = plants + trees
        for harvestItem in list(harvestItems):
            self._pick_harvest(harvestItem)

        slags = self._get_game_location().get_all_objects_by_type(
            GameSlag.type)
        for slag in list(slags):
            item = self._get_item_reader().get(slag.item)
            logger.info(u"Копаем '" + item.name + "' " + str(slag.id) +
                        u" по координатам (" +
                        str(slag.x) + ", " + str(slag.y) + u")")
            dig_event = GameDigItem(slag.id)
            self._get_events_sender().send_game_events([dig_event])
            # convert slag to ground
            slag.type = 'base'
            slag.item = '@GROUND'

    def _pick_harvest(self, harvestItem):
        if self._get_timer().has_elapsed(harvestItem.jobFinishTime):
            item = self._get_item_reader().get(harvestItem.item)
            logger.info(u"Собираем '" + item.name + "' " +
                        str(harvestItem.id) +
                        u" по координатам (" +
                        str(harvestItem.x) + u", " + str(harvestItem.y) + u")")
            pick_event = GamePickItem(objId=harvestItem.id)
            self._get_events_sender().send_game_events([pick_event])
            if harvestItem.type == GamePlant.type:
                # convert plant to slag
                harvestItem.type = GameSlag.type
                harvestItem.item = GameSlag(0L, 0L, 0L).item
            elif harvestItem.type == GameFruitTree.type:
                harvestItem.fruitingCount -= 1
                if harvestItem.fruitingCount == 0:
                    # remove fruit tree
                    self._get_game_location().remove_object_by_id(
                                                                harvestItem.id)
                    # harvestItem.type = GamePickItem.type
                    # TODO convert to pickup box
                    # convert tree to pick item


class SeederBot(BaseActor):

    def perform_action(self):
        grounds = self._get_game_location().get_all_objects_by_type('ground')
        for ground in list(grounds):
            item = self._get_item_reader().get(ground.item)
            seed_item = self._get_item_reader().get(self._get_options())
            print self._get_available_seeds()
            print seed_item.id
            if seed_item.id not in self._get_available_seeds():
                logger.info(u'Это растение здесь сажать запрещено')
                return
            logger.info(u"Сеем '" + seed_item.name +
                        u"' на '" + item.name + u"' " +
                        str(ground.id) +
                        u" по координатам (" +
                        str(ground.x) + u", " + str(ground.y) + u")")
            buy_event = GameBuyItem(unicode(seed_item.id),
                                    ground.id,
                                    ground.y, ground.x)
            self._get_events_sender().send_game_events([buy_event])
            ground.type = u'plant'
            ground.item = unicode(seed_item.id)

    def _get_available_seeds(self):
        level = self._get_game_state().get_state().level
        location = self._get_game_state().get_game_loc().get_location_id()
        print location
        seed_reader = GameSeedReader(self._get_item_reader())
        available_seeds = seed_reader.getAvailablePlantSeedsDict(level,
                                                                 location)
        return available_seeds.values()


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
        logger.info(u'Растение посажено')
        gameObject.jobFinishTime = event_to_handle.jobFinishTime
        gameObject.jobStartTime = event_to_handle.jobStartTime
