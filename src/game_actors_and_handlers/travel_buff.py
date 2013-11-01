# coding=utf-8
import logging
from game_state.game_event import dict2obj
from game_actors_and_handlers.base import BaseActor


logger = logging.getLogger(__name__)


class GameTravelBuff(BaseActor):
    
    def perform_action(self):
        self.travel_count()
        #self.travel_count_2()

    def travel_time(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        for buff in buff_list:
            if buff.item == "@BUFF_TRAVEL_TICKET_TIME":
                time_exp = buff.expire.count
                is_there_travel_buff = True
        if is_there_travel_buff == False or time_exp < 1:
            current_loc = self._get_game_state().get_location_id()
            location_id = "isle_02"
            if current_loc == location_id:
                craft = "1"
                exchange = self._get_item_reader().get("B_VAN_ICE_CREAM").crafts
                for one_item in exchange:
                    if one_item.id == craft:
                        sharp = one_item.materials[0].item
                        sharp_count = one_item.materials[0].count
                        books = one_item.materials[1].item
                        books_count = one_item.materials[0].count
                        result = one_item.resultCount
                        print result
                storage = self._get_game_state().get_state().storageItems
                for item in storage:
                    if item.item == sharp:
                        storage_sharp = item.count
                    elif item.item == books:
                        storage_books = item.count
                for item in self._get_game_state().get_state().gameObjects:
                    if item.item == "@B_VAN_ICE_CREAM":
                        o_id = item.id
                event = {"itemId":craft,"objId":o_id,"action":"craft","type":"item"}
                self._get_events_sender().send_game_events([event])
                logger.info(u"Проездной на 5 дней")
               # buff_list.append(dict2obj({"item":"@BUFF_TRAVEL_TICKET_TIME", "expire": dict2obj({"type":"count", "count": 100})}))
                self._get_game_state().remove_from_storage(sharp, sharp_count)
                self._get_game_state().remove_from_storage(books, books_count)

    def travel_count(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        for buff in buff_list:
            if buff.item == "@BUFF_TRAVEL_TICKET_COUNT":
                time_exp = buff.expire.count
                is_there_travel_buff = True
        if is_there_travel_buff == False or time_exp < 1:
            current_loc = self._get_game_state().get_location_id()
            location_id = "isle_02"
            if current_loc == location_id:
                craft = "3"
                exchange = self._get_item_reader().get("B_VAN_ICE_CREAM").crafts
                for one_item in exchange:
                    if one_item.id == craft:
                        sharp = one_item.materials[0].item
                        sharp_count = one_item.materials[0].count
                        books = one_item.materials[1].item
                        books_count = one_item.materials[0].count
                        result = one_item.resultCount
                        print result
                storage = self._get_game_state().get_state().storageItems
                for item in storage:
                    if item.item == sharp:
                        storage_sharp = item.count
                    elif item.item == books:
                        storage_books = item.count
                for item in self._get_game_state().get_state().gameObjects:
                    if item.item == "@B_VAN_ICE_CREAM":
                        o_id = item.id
                event = {"itemId":craft,"objId":o_id,"action":"craft","type":"item"}
                self._get_events_sender().send_game_events([event])
                logger.info(u"Жетоны на 100 поездок")
                buff_list.append(dict2obj({"item":"@BUFF_TRAVEL_TICKET_COUNT", "expire": dict2obj({"type":"count", "count": 100})}))
                self._get_game_state().remove_from_storage(sharp, sharp_count)
                self._get_game_state().remove_from_storage(books, books_count)

    def travel_count_2(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        for buff in buff_list:
            if buff.item == "@@BUFF_TRAVEL_TICKET_COUNT2":
                time_exp = buff.expire.count
                is_there_travel_buff = True
        if is_there_travel_buff == False or time_exp < 1:
            current_loc = self._get_game_state().get_location_id()
            location_id = "isle_02"
            if current_loc == location_id:
                craft = "4"
                exchange = self._get_item_reader().get("B_VAN_ICE_CREAM").crafts
                for one_item in exchange:
                    if one_item.id == craft:
                        sharp = one_item.materials[0].item
                        sharp_count = one_item.materials[0].count
                        books = one_item.materials[1].item
                        books_count = one_item.materials[0].count
                        result = one_item.resultCount
                        print result
                storage = self._get_game_state().get_state().storageItems
                for item in storage:
                    if item.item == sharp:
                        storage_sharp = item.count
                    elif item.item == books:
                        storage_books = item.count
                for item in self._get_game_state().get_state().gameObjects:
                    if item.item == "@B_VAN_ICE_CREAM":
                        o_id = item.id
                event = {"itemId":craft,"objId":o_id,"action":"craft","type":"item"}
                self._get_events_sender().send_game_events([event])
                logger.info(u"Жетоны на 1000 поездок")
                buff_list.append(dict2obj({"item":"@BUFF_TRAVEL_TICKET_COUNT2", "expire": dict2obj({"type":"count", "count": 1000})}))
                self._get_game_state().remove_from_storage(sharp, sharp_count)
                self._get_game_state().remove_from_storage(books, books_count)



