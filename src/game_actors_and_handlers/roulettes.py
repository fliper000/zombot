# coding=utf-8
import logging
from game_state.game_types import GameBuilding, GamePlayGame

logger = logging.getLogger(__name__)


class RouletteRoller(object):
    def __init__(self, item_reader, game_location,
                  events_sender, timer):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__events_sender = events_sender
        self.__timer = timer

    def perform_action(self):
        buildings = self.__game_location.get_all_objects_by_type(
                        GameBuilding.type)
        for building in list(buildings):
            building_item = self.__item_reader.get(building.item)
            for game in building_item.games:
                game_id = game.id
                play_cost = None
                if hasattr(game, 'playCost'):
                    play_cost = game.playCost
                next_play = None
                next_play_times = building.nextPlayTimes.__dict__
                if game_id in next_play_times:
                    next_play = int(next_play_times[game_id])
                if (
                        next_play and
                        self.__timer.has_elapsed(next_play) and
                        play_cost is None
                ):
                    logger.info(
                        u"Крутим рулетку в '" +
                        building_item.name + "' " +
                        str(building.id) +
                        u" по координатам (" +
                        str(building.x) + u", " + str(building.y) + u")")
                    roll = GamePlayGame(building.id, game_id)
                    self.__events_sender.sendGameEvents([roll])
