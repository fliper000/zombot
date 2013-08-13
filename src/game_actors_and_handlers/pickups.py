# coding=utf-8
import logging
from game_state.game_types import GamePickPickup, GamePickItem, GamePickup
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


class BoxPickuper(BaseActor):

    def perform_action(self):
        boxes = self._get_game_location().get_all_objects_by_type(
                                                    GamePickup.type)
        for box in boxes:
            name = self._get_item_reader().get_name(box)
            logger.info(u'Вскрываем ' + name)
            pick_event = GamePickItem(objId=box.id)
            self._get_events_sender().send_game_events([pick_event])
            self._get_game_location().remove_object_by_id(box.id)


class AddPickupHandler(object):
    def __init__(self, game_location):
        self.__game_loc = game_location

    def handle(self, event_to_handle):
        for c in event_to_handle.pickups:
            try: 
                i=obj2dict(c)
                if i['type'] == 'coins': logger.info(u'Подбираем %d денег по координатам (%d,%d)'%(i['count'],i['x'],i['y']))
                elif i['type'] == 'xp': logger.info(u'Подбираем %d опыта по координатам (%d,%d)'%(i['count'],i['x'],i['y']))
                else: logger.info(u'Подбираем %d предмет коллекции %s по координатам (%d,%d)'%(i['count'],i['id'].encode('utf-8'),i['x'],i['y']))
            except: logger.info(u'Подбираем %s'%(str(i)))
        self.__game_loc.add_pickups(event_to_handle.pickups)
