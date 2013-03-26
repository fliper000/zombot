# coding=utf-8
import logging
from game_actors_and_handlers.base import BaseActor

logger = logging.getLogger(__name__)


class ChangeLocationBot(BaseActor):
    '''
    Changes location

    @param options: Available receive options:

    selected_location: location to change to
    '''

    def perform_action(self):
        location_id = self._get_options()
        if location_id != self._get_game_state().get_location_id():
            self.__change_location(location_id)

    def __change_location(self, location_id):
        logger.info(u'Переходим на ' + location_id)
        change_location_event = {
          "user": None,
          "locationId" : location_id,
          "type":"gameState",
          "action":"gameState",
          "objId": None
        }
        self._get_events_sender().send_game_events([change_location_event])


class GameStateEventHandler(object):
    def __init__(self, game_state):
        self.__game_state = game_state

    def handle(self, event_to_handle):
        logger.info(u'Перешли на ' + event_to_handle.locationId)
        self.__game_state.set_game_loc(event_to_handle)
