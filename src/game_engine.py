# coding=utf-8
import random
import message_factory
from message_factory import Session
import vkontakte
import logging
import time
from game_state.game_event import dict2obj, ApplyGiftEvent, Gift,\
    obj2dict

logger = logging.getLogger(__name__)


class Game():

    def __init__(self, connection, user_id, auth_key, access_token):
        self.__connection = connection
        self.__access_token = access_token
        self.__session = Session(user_id, auth_key,
                                 client_version=self._getClientVersion()
                                 )
        self._createFactory()

    def start(self):
        # load items dictionary

        # send TIME request (http://java.shadowlands.ru/zombievk/go)
        # handle redirect (save new url: http://95.163.80.20/zombievk)
        # parse auth key and time id
        session_key, server_time = self.getTime()

        # send START
        self.startGame(server_time, session_key)
        # TODO parse game state

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
            events = self.event()
            logger.info("events: " + str(events))
            for event in events:
                self.handleEvent(event)
            time.sleep(30)

    def event(self, events=[]):
        '''
        Returns key (string) and time (int)
        '''
        logger.info("events to send" + str(events))
        response = self.send({'type': "EVT", 'events': events})
        game_response = dict2obj(response)
        return game_response.events

    def handleEvent(self, event_to_handle):
        if event_to_handle.action == 'addGift':
            logger.info(u"Получен подарок от " +
                        event_to_handle.gift.user + u". Принять!")
            gift_id = event_to_handle.gift.id
            apply_gift_event = ApplyGiftEvent(Gift(gift_id))
            print self.event([obj2dict(apply_gift_event)])

    def getTime(self):
        '''
        Returns key (string) and time (int)
        '''
        response = self.send({'type': "TIME"})
        return response["key"], response["time"]

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
        return info

    def startGame(self, server_time, session_key):
        self.__factory.setRequestId(server_time)
        self.__factory.setSessionKey(session_key)
        self.send({'type': "START", 'lang': 'en', 'info': self._getUserInfo(),
                   'ad': 'user_apps', 'serverTime': server_time,
                   'clientTime': self._getClientTime()})

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
        assert 'type' in data
        if('id' in data):
            assert data['type'] == 'TIME'
        request = self.__factory.createRequest(data)
        return request.send(self.__connection)

    def _createFactory(self, requestId=None):
        self.__factory = message_factory.Factory(self.__session, requestId)
