# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem

logger = logging.getLogger(__name__)


class WoodPicker(object):
    def __init__(self, item_reader, game_location,
                  events_sender, timer):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__events_sender = events_sender
        self.__timer = timer

    def perform_action(self):
        wood_graves = self.__game_location.get_all_objects_by_type(
                            GameWoodGrave.type)
        wood_graves += self.__game_location.get_all_objects_by_type(
                            GameWoodGraveDouble.type)
        for wood_grave in wood_graves:
            for material_id in list(wood_grave.materials):
                material = self.__item_reader.get(material_id)
                name = material.name
                logger.info(u'Подбираем ' + name)
                self._pick_material(wood_grave, material.id)
                # update game state
                wood_grave.materials.remove(material_id)

    def _pick_material(self, wood_grave, material_id):
        pick_item = GamePickItem(itemId=material_id, objId=wood_grave.id)
        self.__events_sender.sendGameEvents([pick_item])
