# coding=utf-8
import logging
from game_state.game_types import GamePickPickup


logger = logging.getLogger(__name__)


class Pickuper(object):
    def __init__(self, item_reader, game_location,
                  events_sender, timer):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__events_sender = events_sender
        self.__timer = timer

    def pickPickups(self, pickups):
        if pickups:
            logger.info(u'Подбираем дроп...')
        for pickup in pickups:
            pick_event = GamePickPickup([pickup])
            self.__events_sender.send_game_events([pick_event])
