# coding=utf-8
import random
import message_factory
from message_factory import Session
import vkontakte
from settings import Settings
import vkutils
import logging
import time
from game_state.item_reader import GameItemReader, GameSeedReader
from game_state.game_event import dict2obj, obj2dict
from game_state.game_types import GameEVT, GameTIME, GameSTART, \
    GameInfo, \
    GameFertilizePlant, GamePlayGame, \
    GameStartGainMaterial
import pprint
from game_actors_and_handlers.gifts import GiftReceiverBot, AddGiftEventHandler
from game_actors_and_handlers.plants import HarvesterBot, SeederBot, \
    PlantEventHandler
from game_actors_and_handlers.roulettes import RouletteRoller, \
    GameResultHandler
from game_actors_and_handlers.wood_graves import WoodPicker, \
    GainMaterialEventHandler, WoodTargetSelecter
from game_actors_and_handlers.pickups import Pickuper, AddPickupHandler,\
    BoxPickuper
from game_state.brains import PlayerBrains
import socket

logger = logging.getLogger(__name__)



class GameLocation():

    def __init__(self, item_reader, game_location):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__pickups = []

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
            # if gameObject.type != 'base':
                logger.info(obj2dict(gameObject))

    def remove_object_by_id(self, obj_id):
        for game_object in list(self.get_game_objects()):
            if game_object.id == obj_id:
                self.get_game_objects().remove(game_object)

    def get_pickups(self):
        return tuple(self.__pickups)

    def add_pickups(self, pickups):
        self.__pickups += pickups

    def remove_pickup(self, pickup):
        self.__pickups.remove(pickup)


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


class GameInitializer():
    def __init__(self, timer, request_sender, factory, access_token,
                 session, vk):
        self.__timer = timer
        self.__request_sender = request_sender
        self.__factory = factory
        self.__access_token = access_token
        self.__session = session
        self.__vk = vk

    def start(self):
        # send TIME request (http://java.shadowlands.ru/zombievk/go)
        # handle redirect (save new url: http://95.163.80.20/zombievk)
        # parse auth key and time id
        session_key, server_time = self.get_time()

        # send START
        start_response = self.start_game(server_time, session_key)
        return start_response

    def get_time(self):
        '''
        Returns key (string) and time (int)
        '''
        params = self.__vk.getAppParams('612925')
        auth_key = params['auth_key']
        self.__request_sender.set_auth_key(auth_key)
        self.__request_sender.set_url("http://java.shadowlands.ru/zombievk/go")
        self.__request_sender.clear_session()
        self.__request_sender.reset_request_id()

        command = GameTIME()
        response = self.__request_sender.send(command)
        return response.key, response.time

    def start_game(self, server_time, session_key):
        self.__factory.setRequestId(server_time)
        self.__factory.setSessionKey(session_key)
        client_time = self.__timer._get_client_time()
        start_time = time.time()
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'user_apps', serverTime=server_time,
                      clientTime=client_time)
        sending_time = (time.time() - start_time) * 1000
        self.__timer._add_sending_time(sending_time)
        return self.__request_sender.send(command)

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
        if 'bdate' in info:
            bdate = info['bdate']
        else:
            bdate = None
        my_country = api.places.getCountryById(cids=int(info['country']))[0]
        info['country'] = my_country['name']
        my_city = api.places.getCityById(cids=int(info['city']))[0]
        info['city'] = my_city['name']
        game_info = GameInfo(city=info['city'], first_name=info['first_name'],
                 last_name=info['last_name'],
                 uid=long(info['uid']), country=info['country'],
                 sex=long(info['sex']), bdate=bdate)
        return game_info


class GameState():

    def __init__(self, start_response, item_reader):
        self.__game_state = start_response.state
        for attr, val in start_response.params.event.__dict__.iteritems():
            self.__game_state.__setattr__(attr, val)

        self.__game_loc = GameLocation(item_reader,
                                       start_response.params.event.location)
        self.get_game_loc().log_game_objects()

        self.__player_brains = PlayerBrains(self.__game_state,
                                            self.get_game_loc(),
                                            item_reader)
        total_brain_count = self.__player_brains.get_total_brains_count()
        occupied_brain_count = self.__player_brains.get_occupied_brains_count()
        logger.info("Мозги: %d/%d" % (occupied_brain_count, total_brain_count))

    def get_game_loc(self):
        return self.__game_loc

    def get_state(self):
        return self.__game_state

    def get_brains(self):
        return self.__player_brains


class Game():

    CLIENT_VERSION = long(1352868088)

    def __init__(self, connection, user_id, auth_key, access_token,
                  user_prompt, game_item_reader=None, vk=None):
        self.__connection = connection
        self.__session = Session(user_id, auth_key,
                                 client_version=Game.CLIENT_VERSION
                                 )
        factory = message_factory.Factory(self.__session, None)
        self.__request_sender = RequestSender(factory,
                                              self.__connection)
        self.__game_events_sender = GameEventsSender(self.__request_sender)
        self.__timer = GameTimer()
        self.__game_initializer = GameInitializer(self.__timer,
                                                  self.get_request_sender(),
                                                  factory, access_token,
                                                  self.__session, vk)

        # load items dictionary
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

    def select_plant_seed(self):
        level = self.get_game_state().level
        location = self.get_game_loc().get_location_id()
        seed_reader = GameSeedReader(self.__itemReader)
        available_seeds = seed_reader.getAvailablePlantSeedsDict(level,
                                                                 location)
        if self.__selected_seed is None:
            seed_name = self.__user_prompt.prompt_user('Plant to seed:',
                                                       available_seeds.keys())
            self.__selected_seed = available_seeds[seed_name]

    def start(self):

        while(True):
            try:
                start_response = self.__game_initializer.start()

                self.save_game_state(start_response)

                self.select_plant_seed()

                self.create_all_actors()

                # TODO send getMissions
                # TODO handle getMissions response

                self.eventLoop()
            except socket.timeout:
                seconds = 3
                logger.error('Timeout occurred, retrying in %s seconds...'
                             % seconds)
                time.sleep(seconds)
            except (socket.error, ssl.SSLError) as e:
                seconds = 10
                logger.error('Socket error occurred, retrying in %s seconds...'
                             % seconds)
                time.sleep(seconds)

    def save_game_state(self, start_response):
        # parse game state
        self.__game_state_ = GameState(start_response, self.__itemReader)

    def get_game_loc(self):
        return self.__game_state_.get_game_loc()

    def get_game_state(self):
        return self.__game_state_.get_state()

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
        options = {'GiftReceiverBot': receive_options,
                   'SeederBot': self.__selected_seed}
        events_sender = self.__game_events_sender
        timer = self._get_timer()
        item_reader = self.__itemReader
        game_state = self.__game_state_
        actor_classes = [
            Pickuper,
            BoxPickuper,
            GiftReceiverBot,
            HarvesterBot,
            SeederBot,
            RouletteRoller,
            WoodPicker,
            WoodTargetSelecter,
        ]
        self.__actors = []
        for actor_class in actor_classes:
            self.__actors.append(
                actor_class(item_reader, game_state, events_sender, timer,
                            options))

    def perform_all_actions(self):
        '''
        Assumes that create_all_actors is called before
        '''
        for actor in self.__actors:
            actor.perform_action()

    def handleEvent(self, event_to_handle):
        if event_to_handle.action == 'addGift':
            AddGiftEventHandler(self.get_game_state()).handle(event_to_handle)
        elif event_to_handle.action == 'add':
            if event_to_handle.type == 'pickup':
                AddPickupHandler(self.get_game_loc()).handle(event_to_handle)
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

    def _get_timer(self):
        return self.__timer

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

    def set_url(self, url):
        self.__connection.setUrl(url)

    def clear_session(self):
        self.__factory.setSessionKey(None)

    def reset_request_id(self):
        request_id = message_factory._getInitialId()
        self.__factory.setRequestId(request_id)

    def set_auth_key(self, auth_key):
        self.__factory.set_auth_key(auth_key)
