# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameGainItem, GamePickup
from game_state.game_event import dict2obj
from game_actors_and_handlers.base import BaseActor

logger = logging.getLogger(__name__)


class FriendDigger(BaseActor):

    def perform_action(self):
        go_to_friend = {"action":"gameState","locationId":"main","user":"8448924","type":"gameState"}#{"id":8,"action":"gameState","objId":null,"locationId":"main","user":"200961723","type":"gameState"}
        self._get_events_sender().send_game_events([go_to_friend])
        logger.info(u"Иду к другу")
#        dig = {"x":63,"action":"remoteDig","y":57,"type":"item","objId":159}
#        dig_count = 300
#        for _ in range(dig_count):
#            self._get_events_sender().send_game_events([dig])
#            logger.info(u"Копаю клад")
        friend_ret ={"action":"gameState","locationId":"un_09","type":"gameState"} #{"id":14,"action":"gameState","objId":null,"locationId":"main","user":null,"type":"gameState"}
        self._get_events_sender().send_game_events([friend_ret])
        logger.info(u"Возвращаюсь на домашний")

class ByRockets(BaseActor):

    def perform_action(self):
        id_what_to_by = "B_ROCKET"
        what_to_by = self._get_item_reader().get(id_what_to_by).buyCoins
        print what_to_by
        next_id = self._get_game_state().get_state().gameObjects[-1].id
        by_rocket = {"x":12,"action":"buy","y":10,"itemId":id_what_to_by,"type":"item","objId":next_id}
        sell_rocket = {"action":"sell","type":"item","objId":next_id}
        print self._get_game_state().get_state().gameMoney
        for _ in range(10):
            if self._get_game_state().get_state().gameMoney > what_to_by:
                self._get_events_sender().send_game_events([by_rocket])
                logger.info(u"Покупаю ракету")
                self._get_events_sender().send_game_events([sell_rocket])
                logger.info(u"Продаю ракету")
                self._get_game_state().get_state().gameMoney -= what_to_by
                print self._get_game_state().get_state().gameMoney
                next_id += 1
