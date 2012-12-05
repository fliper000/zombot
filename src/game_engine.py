# coding=utf-8
import random
import message_factory
from message_factory import Session
import vkontakte
import logging
import time
from game_state.game_event import dict2obj, obj2dict, GameItemReader
from game_state.game_types import GameEVT, GameTIME, GameSTART,\
    GameApplyGiftEvent, GameGift, GameInfo, GameDigItem, GameSlag, \
    GamePlant, GamePickItem, GameBuyItem, GamePickPickup
import pprint

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
        self.__receive_non_free_gifts = False

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
        self.__game_location = start_response.params.event.location
        for gameObject in self.__game_location.gameObjects:
            #if gameObject.type != 'base':
                logger.info(obj2dict(gameObject))

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
            for event in list(self.__events_to_handle):
                self.handleEvent(event)
            self.automaticActions()
            time.sleep(30)

    def automaticActions(self):
        self.receiveAllGifts()
        self.digAll()

    def pickPickups(self, pickups):
        if pickups:
            logger.info(u'Подбираем дроп...')
        for pickup in pickups:
            pick_event = GamePickPickup([pickup])
            self.sendGameEvents([pick_event])

    def digAll(self):
        plants = self.getAllObjectsByType(GamePlant(False, u"", u"", 0L, 0L, 0L).type)
        for plant in list(plants):
            if int(plant.jobFinishTime) < 0:
                item = self.__itemReader.get(plant.item)
                logger.info(u"Собираем '" + item.name + "' " + str(plant.id) +
                            u" по координатам (" +
                            str(plant.x) + u", " + str(plant.y) + u")")
                pick_event = GamePickItem(plant.id)
                self.sendGameEvents([pick_event])
                # convert plant to slag
                plant.type = GameSlag(0L, 0L, 0L).type
                plant.item = GameSlag(0L, 0L, 0L).item
        slags = self.getAllObjectsByType(GameSlag(0L, 0L, 0L).type)
        for slag in list(slags):
            item = self.__itemReader.get(slag.item)
            logger.info(u"Копаем '" + item.name + "' " + str(slag.id) +
                        u" по координатам (" +
                        str(slag.x) + ", " + str(slag.y) + u")")
            dig_event = GameDigItem(slag.id)
            self.sendGameEvents([dig_event])
            # convert slag to ground
            slag.type = 'base'
            slag.item = '@GROUND'
        grounds = self.getAllObjectsByType('ground')
        for ground in list(grounds):
            item = self.__itemReader.get(ground.item)
            seed_item = self.__itemReader.get(u'P_14R')
            logger.info(u"Сеем '" + seed_item.name + u" на " + item.name + u"' " +
                        str(ground.id) +
                        u" по координатам (" +
                        str(ground.x) + u", " + str(ground.y) + u")")
            buy_event = GameBuyItem(unicode(seed_item.id),
                                ground.id,
                                ground.y, ground.x)
            self.sendGameEvents([buy_event])
            ground.type = u'item'
            ground.item = unicode(seed_item.id)

    def getAllObjectsByType(self, object_type):
        objects = []
        for game_object in self.__game_location.gameObjects:
            item = self.__itemReader.get(game_object.item)
            if game_object.type == object_type or item.type == object_type:
                objects.append(game_object)
        return objects

    def receiveAllGifts(self):
        gifts = self.__game_state.gifts
        if len(gifts) > 0:
            logger.info("receiving all gifts:" + str(len(gifts)))
        for gift in list(gifts):
            self.receiveGift(gift)

    def receiveGift(self, gift):
        item = self.__itemReader.get(gift.item)
        # logger.info(obj2dict(gift))
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
            if not with_message or self.__receive_gifts_with_messages:
                if free or self.__receive_non_free_gifts:
                    logger.info(u"Принимаю " + gift_name)
                    apply_gift_event = GameApplyGiftEvent(GameGift(gift.id))
                    self.sendGameEvents([apply_gift_event])
        self.removeGiftFromGameState(gift)

    def removeGiftFromGameState(self, gift):
        for current_gift in list(self.__game_state.gifts):
            if gift.id == current_gift.id:
                self.__game_state.gifts.remove(current_gift)

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
        elif event_to_handle.action == 'add':
            if event_to_handle.type == 'pickup':
                self.pickPickups(event_to_handle.pickups)
        else:
            self.logUnknownEvent(event_to_handle)
        self.__events_to_handle.remove(event_to_handle)

    def logUnknownEvent(self, event_to_handle):
        logger = logging.getLogger('unknownEventLogger')
        logger.info(pprint.pformat(obj2dict(event_to_handle)))

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
                 uid=long(info['uid']), country=info['country'],
                 sex=long(info['sex']), bdate=info['bdate'])
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
        return long(random.randrange(2800, 4000))

    def _getClientVersion(self):
        return long(1352868088)

    def _setClientVersion(self, version):
        self.__session.CLIENT_VERSION = version

    def send(self, data):
        data = obj2dict(data)
        assert 'type' in data
        request = self.__factory.createRequest(data)
        return dict2obj(request.send(self.__connection))

    def _createFactory(self, requestId=None):
        self.__factory = message_factory.Factory(self.__session, requestId)
