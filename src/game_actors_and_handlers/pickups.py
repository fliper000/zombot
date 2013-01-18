# coding=utf-8
import logging
from game_state.game_types import GamePickPickup
from game_actors_and_handlers.base import BaseActor


logger = logging.getLogger(__name__)


class Pickuper(BaseActor):

    def perform_action(self):
        pickups = self._get_game_location().get_pickups()
        self.pick_pickups(pickups)

    def pick_pickups(self, pickups):
        if pickups:
            logger.info(u'Подбираем дроп...')
        for pickup in pickups:
            pick_event = GamePickPickup([pickup])
            self._get_events_sender().send_game_events([pick_event])
            self._get_game_location().remove_pickup(pickup)


class AddPickupHandler(object):
    def __init__(self, game_location):
        self.__game_loc = game_location

    def handle(self, event_to_handle):
        self.__game_loc.add_pickups(event_to_handle.pickups)
