# coding=utf-8
import logging
from game_state.game_event import dict2obj
from game_actors_and_handlers.base import BaseActor


logger = logging.getLogger(__name__)


class EmeraldExchange(BaseActor):
    
    def perform_action(self):
        object_id = []
        
        for item in self._get_game_state().get_state().gameObjects:
            if item.item == "@B_MILL_EMERALD2":
                exchange = self._get_item_reader().get("B_MILL_EMERALD2").crafts
                object_id = item.id
                self.change(object_id, exchange)
            elif  item.item == "@B_LIGHT_EMERALD2":
                exchange = self._get_item_reader().get("B_LIGHT_EMERALD2").crafts
                object_id = item.id
                self.change(object_id, exchange)

                
    def change(self, object_id, exchange):
        collections = self._get_game_state().get_state().collectionItems
        for one_item in exchange:
            print one_item
            craft = one_item.id
            first_coll = one_item.materials[0].item
            first_coll_count = one_item.materials[0].count
            second_coll = one_item.materials[1].item
            second_coll_count = one_item.materials[1].count
            if getattr(collections, first_coll):
                storage_coll1 = getattr(collections, first_coll)
            elif second_coll in collections:
                storage_coll2 = collections[second_coll]
                if first_coll_count <= storage_coll1 and second_coll_count <= storage_coll2:
                    if storage_coll1 > storage_coll2:
                        repeat = storage_coll1
                    else:
                        repeat = storage_coll2
                    for _ in range(repeat):
                        event = {"itemId":craft,"objId":object_id,"type":"item","action":"craft"}
                        #self._get_events_sender().send_game_events([event])
                        logger.info(one_item.name)
                    collections[first_coll] -= first_coll_count
                    collections[second_coll] -= second_coll_count
