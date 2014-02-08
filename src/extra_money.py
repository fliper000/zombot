# coding=utf-8
# Обмен роз и лилий в Бизнес-Центре на деньги
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameStone, GameGainItem, GamePickup
from game_state.game_event import dict2obj, obj2dict
from game_actors_and_handlers.base import BaseActor


logger = logging.getLogger(__name__)


class HarvestExchange(BaseActor):


    def perform_action(self):
        if self._get_game_state().get_state().gameMoney < 1500000000:
            current_loc = self._get_game_state().get_location_id()
            location_id = "isle_02"
            if current_loc == location_id:
                craft = "3"
                exchange = self._get_item_reader().get("B_BUSINESS").crafts
                for one_item in exchange:
                    if one_item.id == craft:
                        rose = one_item.materials[0].item
                        rose_count = one_item.materials[0].count
                        lily = one_item.materials[1].item
                        lily_count = one_item.materials[1].count
                        result = one_item.resultCount
                        #print "lily_count ", lily_count
                        #print "rose_count ", rose_count
                        #print obj2dict(one_item.materials)
                storage = self._get_game_state().get_state().storageItems
                for item in storage:
                    if hasattr(item, "item"):
                        if item.item == rose:
                            storage_rose = item.count
                        elif item.item == lily:
                            storage_lily = item.count
                for item in self._get_game_state().get_state().gameObjects:
                    if item.item == "@B_BUSINESS":
                        o_id = item.id
                for _ in range(10000):
                    if storage_rose > rose_count and storage_lily > lily_count:
                        event = {"itemId":craft,"objId":o_id,"action":"craft","type":"item"}
                        logger.info(u"Обмениваем партию Роз и Лилий. У Вас %d монет.",self._get_game_state().get_state().gameMoney)
                        #print event
                        #print self._get_game_state().get_state().gameMoney
                        self._get_events_sender().send_game_events([event])
                        self._get_game_state().get_state().gameMoney += result
                        self._get_game_state().remove_from_storage(rose, rose_count)
                        self._get_game_state().remove_from_storage(lily, lily_count)
                        storage_rose -= rose_count
                        storage_lily -= lily_count
                        print "storage_lily ", storage_lily
                        print "storage_rose ", storage_rose


    '''def perform_action(self):
        object_id = self.get_building_id("@B_BUSINESS")
        if object_id:
            crafts = self._get_item_reader().get("B_BUSINESS").crafts
            storages = self._get_game_state().get_state().storageItems
            craft_id = "3"
            for craft in crafts:
                while self.craft_is_possible(craft, storages):
                    #self.make_craft(craft_id, object_id)
                    logger.info(craft.name)
                    #for material in craft.materials:
                    #self.decrement_material(material, storages)


    def get_building_id(self, building_type):
            for item in self._get_game_state().get_state().gameObjects:
                if item.item == building_type:
                    return item.id


    def craft_is_possible(self, craft, storages):
        one_material = craft.materials[0].item
        one_material_count = craft.materials[0].count
        two_material = craft.materials[1].item
        two_material_count = craft.materials[1].count
        for item in storages:
            if item.item == one_material:
                one_material_storage = item.count

        open('rose.txt','a').write(str(storage_coll1) + "\n")
        print "1", one_material
        print "2", two_material
        print one_material_storage
        #print storage_coll2
        print "craft", craft

        return self._get_game_state().get_state().gameMoney < 1500000000 and one_material_count <= storage_coll1 and two_material_count <= storage_coll2

def make_craft(self, craft_id, object_id):
                event = {"itemId":craft_id,"objId":object_id,"type":"item","action":"craft"}
                #self._get_events_sender().send_game_events([event])'''

