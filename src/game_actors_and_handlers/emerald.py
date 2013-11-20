# coding=utf-8
import logging
from game_state.game_event import dict2obj
from game_actors_and_handlers.base import BaseActor


logger = logging.getLogger(__name__)


class EmeraldExchange(BaseActor):
    
    def perform_action(self):
        object_id = self.get_building_id("@B_MILL_EMERALD2")
        crafts = self._get_item_reader().get("B_MILL_EMERALD2").crafts
        for craft in crafts:
            craft_id = craft.id
            while self.craft_is_possible(object_id, craft):
                self.make_craft(craft_id, object_id)
                logger.info(craft.name)
#                collections[first_coll] -= first_coll_count
#                collections[second_coll] -= second_coll_count
        object_id = self.get_building_id("@B_LIGHT_EMERALD2")
        exchange = self._get_item_reader().get("B_LIGHT_EMERALD2").crafts
        self.craft_is_possible(object_id, exchange)
                
    def get_building_id(self, building_type):
            for item in self._get_game_state().get_state().gameObjects:
                if item.item == building_type:
                    return item.id
                
    def craft_is_possible(self, object_id, craft):
        collections = self._get_game_state().get_state().collectionItems
        first_coll = craft.materials[0].item
        first_coll_count = craft.materials[0].count
        second_coll = craft.materials[1].item
        second_coll_count = craft.materials[1].count
        storage_coll1 = getattr(collections, first_coll, 0)
        if storage_coll1:
            pass
        storage_coll2 = getattr(collections, second_coll, 0)
        if storage_coll2:
            pass
        return first_coll_count <= storage_coll1 and second_coll_count <= storage_coll2
                
    def make_craft(self, craft_id, object_id):
                event = {"itemId":craft_id,"objId":object_id,"type":"item","action":"craft"}
                #self._get_events_sender().send_game_events([event])

