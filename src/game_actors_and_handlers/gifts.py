# coding=utf-8
import logging
from game_state.game_types import GameApplyGiftEvent, GameGift
logger = logging.getLogger(__name__)


class GiftReceiverBot(object):
    '''
    Receives gifts
    '''

    def __init__(self, item_reader, game_state,
                  events_sender, receive_options):
        '''
        @param receive_options: Available receive options:

        with_messages: receive gifts with messages
        non_free: receive non-free gifts
        '''
        self.__item_reader = item_reader
        self.__game_state = game_state
        self.__events_sender = events_sender
        self.__receive_options = receive_options

    def perform_action(self):
        self.receive_all_gifts()

    def receive_all_gifts(self):
        gifts = self.__game_state.gifts
        if len(gifts) > 0:
            logger.info("receiving all gifts:" + str(len(gifts)))
        for gift in list(gifts):
            self.receive_gift(gift)

    def receive_gift(self, gift):
        item = self.__item_reader.get(gift.item)
        gift_name = u"подарок '" + item.name + u"'"
        with_message = hasattr(gift, 'msg') and gift.msg != ''
        moved = hasattr(item, 'moved') and item.moved == True
        free = hasattr(gift, 'free') and gift.free
        if with_message:
            gift_name += u" с сообщением: '" + gift.msg + u"'"
        if moved:
            logger.info(gift_name + u"' нужно поместить")
        if free:
            gift_name = u'бесплатный ' + gift_name
        gift_name += u" от " + gift.user
        logger.info(u'Получен ' + gift_name)
        if not moved:
            if not with_message or self.__receive_options["with_messages"]:
                if free or self.__receive_options["non_free"]:
                    logger.info(u"Принимаю " + gift_name)
                    apply_gift_event = GameApplyGiftEvent(GameGift(gift.id))
                    self.__events_sender.sendGameEvents([apply_gift_event])
        self.remove_gift_from_game_state(gift)

    def remove_gift_from_game_state(self, gift):
        for current_gift in list(self.__game_state.gifts):
            if gift.id == current_gift.id:
                self.__game_state.gifts.remove(current_gift)


class AddGiftEventHandler(object):
    def __init__(self, game_state):
        self.__game_state = game_state

    def handle(self, event):
        gift = event.gift
        self.append_gift_to_game_state(gift)

    def append_gift_to_game_state(self, gift):
        logger.info(u"Получен подарок.")
        self.__game_state.gifts.append(gift)
