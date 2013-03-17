# coding=utf-8
import logging
from game_state.game_types import GameCookGrave, GameCookGraveWithBrains
from game_actors_and_handlers.workers import ResourcePicker

logger = logging.getLogger(__name__)


class BrewPicker(ResourcePicker):

    def get_worker_types(self):
        return [GameCookGrave.type, GameCookGraveWithBrains.type]
