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
        self.__change_location()

    def __change_location(self):
        print self._get_options()
