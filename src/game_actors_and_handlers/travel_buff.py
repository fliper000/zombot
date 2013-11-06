# coding=utf-8
import logging
from game_state.game_event import dict2obj
from game_actors_and_handlers.base import BaseActor


logger = logging.getLogger(__name__)


class GameTravelBuff(BaseActor):
    
    def perform_action(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        o_id = False
        for buff in buff_list:
            if buff.item == "@BUFF_TRAVEL_TICKET_TIME" or "@BUFF_TRAVEL_TICKET_TIME2":
                time_exp = buff.expire.endDate
                is_there_travel_buff = True
            elif buff.item == "@BUFF_TRAVEL_TICKET_COUNT" or "@BUFF_TRAVEL_TICKET_COUNT2":
                #time_exp = buff.expire.count
                is_there_travel_buff = True
        if is_there_travel_buff == False or self._get_timer().has_elapsed(time_exp):
            for item in self._get_game_state().get_state().gameObjects:
                if item.item == "@B_VAN_ICE_CREAM":
                    o_id = item.id
            if o_id:
                craft = "1"
                exchange = self._get_item_reader().get("B_VAN_ICE_CREAM").crafts
                for one_item in exchange:
                    if one_item.id == craft:
                        sharp = one_item.materials[0].item
                        sharp_count = one_item.materials[0].count
                        books = one_item.materials[1].item
                        books_count = one_item.materials[0].count
                storage = self._get_game_state().get_state().storageItems
                for item in storage:
                    if item.item == sharp:
                        storage_sharp = item.count
                    elif item.item == books:
                        storage_books = item.count
                event = {"itemId":craft,"objId":o_id,"type":"item","action":"craft"}
                self._get_events_sender().send_game_events([event])
                logger.info(self._get_item_reader().get("@BUFF_TRAVEL_TICKET_TIME").name)
                buff_list.append(dict2obj({"item":"@BUFF_TRAVEL_TICKET_TIME", "expire": dict2obj({"type":"time", "time": str(int(self._get_timer()._get_current_client_time())+86400000*5)})}))
                self._get_game_state().remove_from_storage(sharp, sharp_count)
                self._get_game_state().remove_from_storage(books, books_count)
