# coding=utf-8
import random
import message_factory
from message_factory import Session
import vkontakte
import logging
import time
from game_state.game_event import dict2obj, obj2dict, GameItemReader
from game_state.game_types import GameEVT, GameTIME, GameSTART,\
    GameApplyGiftEvent, GameGift, GameInfo

logger = logging.getLogger(__name__)


class Game():

    def __init__(self, connection, user_id, auth_key, access_token):
        self.__connection = connection
        self.__access_token = access_token
        self.__session = Session(user_id, auth_key,
                                 client_version=self._getClientVersion()
                                 )
        self._createFactory()
        self.__itemReader = GameItemReader()
        self.__itemReader.read('items.txt')
        self.__events_to_handle = []
        self.__receive_gifts_with_messages = False
        self.__receive_only_free_gifts = True

    def start(self):
        # load items dictionary

        # send TIME request (http://java.shadowlands.ru/zombievk/go)
        # handle redirect (save new url: http://95.163.80.20/zombievk)
        # parse auth key and time id
        session_key, server_time = self.getTime()

        # send START
        start_response = self.startGame(server_time, session_key)
        # TODO parse game state
        self.__game_state = start_response.state

        # TODO send getMissions
        # TODO handle getMissions response

        self.eventLoop()

    def eventLoop(self):
        '''
        in a loop, every 30 seconds
        send EVT request
        handle EVT response
        '''
        while(True):
            self.sendGameEvents()
            if len(self.__events_to_handle) > 0:
                logger.info("received events: " + str(self.__events_to_handle))
            for event in self.__events_to_handle:
                self.handleEvent(event)
            self.automaticActions()
            time.sleep(30)

    def automaticActions(self):
        self.receiveAllGifts()

    def receiveAllGifts(self):
        gifts = self.__game_state.gifts
        if len(gifts) > 0:
            logger.info("receiving all gifts:")
        for gift in gifts:
            self.receiveGift(gift)

    def receiveGift(self, gift):
        item = dict2obj(self.__itemReader.get(gift.item))
        # logger.info(obj2dict(gift))
        gift_name = "подарок '" + item.name + u"'"
        if hasattr(gift, 'msg') and gift.msg != '':
            gift_name += " с сообщением: '" + gift.msg + "'"
            if not self.__receive_gifts_with_messages:
                return
        if hasattr(item, 'moved') and item.moved == True:
            logger.info(gift_name + "' нужно поместить")
            return
        if hasattr(gift, 'free') and gift.free:
            gift_name = 'бесплатный ' + gift_name
        else:
            if self.__receive_only_free_gifts:
                return

        logger.info(u"Принимаю " + gift_name +
                    u" от " + gift.user)
        apply_gift_event = GameApplyGiftEvent(gift=GameGift(id=gift.id))
        self.sendGameEvents([apply_gift_event])
        self.removeGiftFromGameState(gift)

    def removeGiftFromGameState(self, gift):
        for current_gift in self.__game_state.gifts:
            if gift.id == current_gift.id:
                self.__game_state.gifts.remove(current_gift)
                break

    def sendGameEvents(self, events=[]):
        '''
        Returns key (string) and time (int)
        '''
        if len(events) > 0:
            logger.info("events to send: " + str(events))
        command = GameEVT(events=events)
        game_response = self.send(command)
        self.__events_to_handle += game_response.events

    def handleEvent(self, event_to_handle):
        if event_to_handle.action == 'addGift':
            logger.info(u"Получен подарок.")
            gift = event_to_handle.gift
            self.receiveGift(gift)
            self.__events_to_handle.remove(event_to_handle)

    def getTime(self):
        '''
        Returns key (string) and time (int)
        '''
        command = GameTIME()
        response = self.send(command)
        return response.key, response.time

    def _getUserInfo(self):
        '''
        returns user info using vk api
        '''
        # get vk user info
        api = vkontakte.api.API(token=self.__access_token)
        info = api.getProfiles(
            uids=self.__session.getUserId(), format='json',
            fields='bdate,sex,first_name,last_name,city,country')
        info = info[0]
        my_country = api.places.getCountryById(cids=int(info['country']))[0]
        info['country'] = my_country['name']
        my_city = api.places.getCityById(cids=int(info['city']))[0]
        info['city'] = my_city['name']
        game_info = GameInfo(city=info['city'], first_name=info['first_name'],
                 last_name=info['last_name'],
                 uid=info['uid'], country=info['country'],
                 sex=info['sex'], bdate=info['bdate'])
        return game_info

    def startGame(self, server_time, session_key):
        self.__factory.setRequestId(server_time)
        self.__factory.setSessionKey(session_key)
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'user_apps', serverTime=server_time,
                      clientTime=self._getClientTime())
        return self.send(command)

    def _getSessionKey(self):
        return self.__factory._getSessionKey()

    def _getClientTime(self):
        random.seed()
        return random.randrange(2800, 4000)

    def _getClientVersion(self):
        return 1352868088

    def _setClientVersion(self, version):
        self.__session.CLIENT_VERSION = version

    def send(self, data):
        data = obj2dict(data)
        assert 'type' in data
        request = self.__factory.createRequest(data)
        return dict2obj(request.send(self.__connection))

    def _createFactory(self, requestId=None):
        self.__factory = message_factory.Factory(self.__session, requestId)
