# coding=utf-8
import random
import message_factory
from message_factory import Session
import vkontakte
import logging
import time
from game_state.item_reader import GameItemReader, GameSeedReader
from game_state.game_event import dict2obj, obj2dict
from game_state.game_types import GameEVT, GameTIME, GameSTART,\
    GameInfo, \
    GameFertilizePlant, GamePlayGame,\
    GameStartGainMaterial
import pprint
from game_actors_and_handlers.gifts import GiftReceiverBot, AddGiftEventHandler
from game_actors_and_handlers.plants import HarvesterBot, SeederBot,\
    PlantEventHandler
from game_actors_and_handlers.roulettes import RouletteRoller,\
    GameResultHandler
from game_actors_and_handlers.wood_graves import WoodPicker,\
    GainMaterialEventHandler, WoodTargetSelecter
from game_actors_and_handlers.pickups import Pickuper
from game_state.brains import PlayerBrains

logger = logging.getLogger(__name__)


class GameLocation():

    def __init__(self, item_reader, game_location):
        self.__item_reader = item_reader
        self.__game_location = game_location

    def append_object(self, obj):
        self.get_game_objects().append(obj)

    def get_game_location(self):
        return self.__game_location

    def get_game_objects(self):
        return self.get_game_location().gameObjects

    def get_location_id(self):
        return self.__game_location.id

    def get_all_objects_by_types(self, object_types):
        objects = []
        for game_object in self.get_game_objects():
            item = self.__item_reader.get(game_object.item)
            if game_object.type in object_types or item.type in object_types:
                objects.append(game_object)
        return objects

    def get_all_objects_by_type(self, object_type):
        return self.get_all_objects_by_types([object_type])

    def get_object_by_id(self, obj_id):
        for game_object in self.get_game_objects():
            if game_object.id == obj_id:
                return game_object
        return None

    def log_game_objects(self):
        for gameObject in self.get_game_objects():
            #if gameObject.type != 'base':
                logger.info(obj2dict(gameObject))

    def remove_object_by_id(self, obj_id):
        for game_object in list(self.get_game_objects()):
            if game_object.id == obj_id:
                self.get_game_objects().remove(game_object)


class GameTimer(object):

    def __init__(self):
        self._client_time = 0
        self._start_time = 0

    def _get_client_time(self):
        random.seed()
        self._client_time = long(random.randrange(2800, 4000))
        self._start_time = time.time()
        return self._client_time

    def _get_current_client_time(self):
        '''
        returns the current in-game time (in milliseconds)
        '''
        currentTime = self._client_time
        currentTime += (time.time() - self._start_time) * 1000
        return currentTime

    def _add_sending_time(self, sending_time):
        self._client_time += sending_time

    def has_elapsed(self, time):
        return int(time) <= self._get_current_client_time()


class GameEventsSender(object):
    def __init__(self, request_sender):
        self.__events_to_handle = []
        self.__request_sender = request_sender

    def print_game_events(self):
        if len(self.__events_to_handle) > 0:
            logger.info("received events: " + str(self.__events_to_handle))

    def get_game_events(self):
        return list(self.__events_to_handle)

    def send_game_events(self, events=[]):
        '''
        Returns key (string) and time (int)
        '''
        if len(events) > 0:
            logger.info("events to send: " + str(events))
        command = GameEVT(events=events)
        game_response = self.__request_sender.send(command)
        self.__events_to_handle += game_response.events

    def remove_game_event(self, event):
        self.__events_to_handle.remove(event)


class Game():

    def __init__(self, connection, user_id, auth_key, access_token,
                  user_prompt, game_item_reader=None):
        self.__connection = connection
        self.__access_token = access_token
        self.__session = Session(user_id, auth_key,
                                 client_version=self._getClientVersion()
                                 )
        self._createFactory()
        if game_item_reader is None:
            self.__itemReader = GameItemReader()
            self.__itemReader.download('items.txt')
            self.__itemReader.read('items.txt')
        else:
            self.__itemReader = game_item_reader
        self.__user_prompt = user_prompt
        self.__selected_seed = None
        self.__receive_gifts_with_messages = False
        self.__receive_non_free_gifts = False
        self.__timer = GameTimer()

    def select_plant_seed(self):
        level = self.__game_state.level
        location = self.get_game_loc().get_location_id()
        seed_reader = GameSeedReader(self.__itemReader)
        available_seeds = seed_reader.getAvailablePlantSeedsDict(level,
                                                                 location)
        seed_name = self.__user_prompt.prompt_user('Plant to seed:',
                                                   available_seeds.keys())
        self.__selected_seed = available_seeds[seed_name]

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
        for attr, val in start_response.params.event.__dict__.iteritems():
            self.__game_state.__setattr__(attr, val)
        self.__game_loc = GameLocation(self.__itemReader,
                                       start_response.params.event.location)
        self.get_game_loc().log_game_objects()

        self.__player_brains = PlayerBrains(self.__game_state,
                                            self.get_game_loc(),
                                            self.__itemReader)
        total_brain_count = self.__player_brains.get_total_brains_count()
        occupied_brain_count = self.__player_brains.get_occupied_brains_count()
        logger.info("Мозги: %d/%d" % (occupied_brain_count, total_brain_count))

        self.select_plant_seed()

        self.create_all_actors()

        # TODO send getMissions
        # TODO handle getMissions response

        self.eventLoop()

    def get_game_loc(self):
        return self.__game_loc

    def eventLoop(self):
        '''
        in a loop, every 30 seconds
        send EVT request
        handle EVT response
        '''
        while(True):
            self.__game_events_sender.send_game_events()
            self.__game_events_sender.print_game_events()
            for event in self.__game_events_sender.get_game_events():
                self.handleEvent(event)
            self.perform_all_actions()
            time.sleep(30)

    def create_all_actors(self):
        receive_options = {'with_messages': self.__receive_gifts_with_messages,
                           'non_free': self.__receive_non_free_gifts}
        events_sender = self.__game_events_sender
        self.__actors = [
            GiftReceiverBot(self.__itemReader, self.__game_state,
                            events_sender, receive_options),
            HarvesterBot(self.__itemReader, self.get_game_loc(),
                         events_sender, self._get_timer()),
            SeederBot(self.__itemReader, self.get_game_loc(),
                      events_sender, self.__selected_seed),
            RouletteRoller(self.__itemReader, self.get_game_loc(),
                           events_sender, self._get_timer()),
            WoodPicker(self.__itemReader, self.get_game_loc(),
                       events_sender, self._get_timer()),
            WoodTargetSelecter(self.__itemReader, self.get_game_loc(),
                               events_sender, self._get_timer(),
                               self.__player_brains)
        ]

    def perform_all_actions(self):
        '''
        Assumes that create_all_actors is called before
        '''
        for actor in self.__actors:
            actor.perform_action()

    def handleEvent(self, event_to_handle):
        events_sender = self.__game_events_sender
        if event_to_handle.action == 'addGift':
            AddGiftEventHandler(self.__game_state).handle(event_to_handle)
        elif event_to_handle.action == 'add':
            if event_to_handle.type == 'pickup':
                Pickuper(self.__itemReader, self.get_game_loc(), events_sender,
                         self.__timer).pickPickups(event_to_handle.pickups)
        elif event_to_handle.type == GameFertilizePlant.type:
            PlantEventHandler(self.get_game_loc()).handle(event_to_handle)
        elif event_to_handle.type == GamePlayGame.type:
            GameResultHandler(self.__itemReader,
                              self.get_game_loc()).handle(event_to_handle)
        elif event_to_handle.type == GameStartGainMaterial.type:
            GainMaterialEventHandler(self.__itemReader, self.get_game_loc(),
                                     self.__timer).handle(event_to_handle)
        else:
            self.logUnknownEvent(event_to_handle)
        self.__game_events_sender.remove_game_event(event_to_handle)

    def logUnknownEvent(self, event_to_handle):
        logger = logging.getLogger('unknownEventLogger')
        logger.info(pprint.pformat(obj2dict(event_to_handle)))

    def getTime(self):
        '''
        Returns key (string) and time (int)
        '''
        command = GameTIME()
        response = self.get_request_sender().send(command)
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
        client_time = self._get_timer()._get_client_time()
        start_time = time.time()
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'user_apps', serverTime=server_time,
                      clientTime=client_time)
        sending_time = (time.time() - start_time) * 1000
        self._get_timer()._add_sending_time(sending_time)
        return self.get_request_sender().send(command)

    def _getSessionKey(self):
        return self.__factory._getSessionKey()

    def _get_timer(self):
        return self.__timer

    def _getClientVersion(self):
        return long(1352868088)

    def _setClientVersion(self, version):
        self.__session.CLIENT_VERSION = version

    def _createFactory(self, requestId=None):
        self.__factory = message_factory.Factory(self.__session, requestId)
        self.__request_sender = RequestSender(self.__factory,
                                              self.__connection)
        self.__game_events_sender = GameEventsSender(self.__request_sender)

    def get_request_sender(self):
        return self.__request_sender


class RequestSender(object):
    def __init__(self, message_factory, connection):
        self.__factory = message_factory
        self.__connection = connection

    def send(self, data):
        data = obj2dict(data)
        assert 'type' in data
        request = self.__factory.createRequest(data)
        return dict2obj(request.send(self.__connection))
