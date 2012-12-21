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
    GameInfo, GameDigItem, GameSlag, \
    GamePlant, GamePickItem, GameBuyItem, GamePickPickup, GameFruitTree,\
    GameFertilizePlant, GameBuilding, GamePlayGame,\
    GameWoodGrave, GameStartGainMaterial, GameWoodGraveDouble
import pprint
from game_actors_and_handlers.gifts import GiftReceiverBot, AddGiftEventHandler

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

    def get_all_objects_by_type(self, object_type):
        objects = []
        for game_object in self.get_game_objects():
            item = self.__item_reader.get(game_object.item)
            if game_object.type == object_type or item.type == object_type:
                objects.append(game_object)
        return objects

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
        self.__events_to_handle = []
        self.__receive_gifts_with_messages = False
        self.__receive_non_free_gifts = False

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
        self.__game_loc = GameLocation(self.__itemReader,
                                       start_response.params.event.location)
        self.get_game_loc().log_game_objects()

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
            self.sendGameEvents()
            if len(self.__events_to_handle) > 0:
                logger.info("received events: " + str(self.__events_to_handle))
            for event in list(self.__events_to_handle):
                self.handleEvent(event)
            self.automaticActions()
            time.sleep(30)

    def rouletteRoll(self):
        buildings = self.get_game_loc().get_all_objects_by_type(
                        GameBuilding.type)
        for building in list(buildings):
            building_item = self.__itemReader.get(building.item)
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
                        next_play <= self._getCurrentClientTime() and
                        play_cost is None
                ):
                    logger.info(
                        u"Крутим рулетку в '" +
                        building_item.name + "' " +
                        str(building.id) +
                        u" по координатам (" +
                        str(building.x) + u", " + str(building.y) + u")")
                    roll = GamePlayGame(building.id, game_id)
                    self.sendGameEvents([roll])

    def pickMaterial(self, wood_grave, material_id):
        pick_item = GamePickItem(itemId=material_id, objId=wood_grave.id)
        self.sendGameEvents([pick_item])

    def pickAllWood(self):
        wood_graves = self.get_game_loc().get_all_objects_by_type(
                            GameWoodGrave.type)
        wood_graves += self.get_game_loc().get_all_objects_by_type(
                            GameWoodGraveDouble.type)
        for wood_grave in wood_graves:
            for material_id in list(wood_grave.materials):
                material = self.__itemReader.get(material_id)
                name = material.name
                logger.info(u'Подбираем ' + name)
                self.pickMaterial(wood_grave, material.id)
                # update game state
                wood_grave.materials.remove(material_id)

    def updateJobDone(self, wood_grave):
        if hasattr(wood_grave, 'jobEndTime'):
            logger.info('jobEndTime:' + wood_grave.jobEndTime +
                        ', current time:' + str(self._getCurrentClientTime()))
            if int(wood_grave.jobEndTime) < self._getCurrentClientTime():
                if hasattr(wood_grave, 'target'):
                    target_id = wood_grave.target.id
                    target = self.get_game_loc().get_object_by_id(target_id)
                    target.materialCount -= 1
                    target_item = self.__itemReader.get(target.item)
                    logger.info("Материал добыт")
                    wood_grave.materials.append(target_item.material)
                    if target.materialCount == 0:
                        logger.info("Ресурсы исчерпаны!")
                        box_item = self.__itemReader.get(target_item.box)
                        new_obj = dict2obj({'item': '@' + box_item.id,
                                            'type': box_item.type,
                                            'objId': target_id})
                        self.get_game_loc().remove_object_by_id(target_id)
                        self.get_game_loc().append_object(new_obj)
                        logger.info(u"'%s' превращён в '%s'" %
                                    (target_item.name, box_item.name))
                delattr(wood_grave, 'jobEndTime')
        else:
            logger.info("There's no jobEndTime")

    def automaticActions(self):
        self.perform_all_actions()
        self.harvestAndDigAll()
        self.seedAll()
        self.rouletteRoll()
        self.pickAllWood()

    def pickPickups(self, pickups):
        if pickups:
            logger.info(u'Подбираем дроп...')
        for pickup in pickups:
            pick_event = GamePickPickup([pickup])
            self.sendGameEvents([pick_event])

    def pickHarvest(self, harvestItem):
        if int(harvestItem.jobFinishTime) < self._getCurrentClientTime():
            item = self.__itemReader.get(harvestItem.item)
            logger.info(u"Собираем '" + item.name + "' " +
                        str(harvestItem.id) +
                        u" по координатам (" +
                        str(harvestItem.x) + u", " + str(harvestItem.y) + u")")
            pick_event = GamePickItem(objId=harvestItem.id)
            self.sendGameEvents([pick_event])
            if harvestItem.type == GamePlant.type:
                # convert plant to slag
                harvestItem.type = GameSlag(0L, 0L, 0L).type
                harvestItem.item = GameSlag(0L, 0L, 0L).item
            elif harvestItem.type == GameFruitTree.type:
                harvestItem.fruitingCount -= 1
                if harvestItem.fruitingCount == 0:
                    # convert tree to pick item
                    harvestItem.type = GamePickItem.type

    def harvestAndDigAll(self):
        plants = self.get_game_loc().get_all_objects_by_type(GamePlant.type)
        trees = self.get_game_loc().get_all_objects_by_type(GameFruitTree.type)
        harvestItems = plants + trees
        for harvestItem in list(harvestItems):
            self.pickHarvest(harvestItem)

        slags = self.get_game_loc().get_all_objects_by_type(GameSlag.type)
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

    def seedAll(self):
        grounds = self.get_game_loc().get_all_objects_by_type('ground')
        for ground in list(grounds):
            item = self.__itemReader.get(ground.item)
            seed_item = self.__itemReader.get(self.__selected_seed)
            logger.info(u"Сеем '" + seed_item.name +
                        u"' на '" + item.name + u"' " +
                        str(ground.id) +
                        u" по координатам (" +
                        str(ground.x) + u", " + str(ground.y) + u")")
            buy_event = GameBuyItem(unicode(seed_item.id),
                                ground.id,
                                ground.y, ground.x)
            self.sendGameEvents([buy_event])
            ground.type = u'plant'
            ground.item = unicode(seed_item.id)

    def create_gift_receiver(self):
        receive_options = {'with_messages': self.__receive_gifts_with_messages,
                           'non_free': self.__receive_non_free_gifts}
        events_sender = self
        receiver = GiftReceiverBot(self.__itemReader, self.__game_state,
                                events_sender, receive_options)
        return receiver

    def create_all_actors(self):
        self.__actors = [
            self.create_gift_receiver()
        ]

    def perform_all_actions(self):
        '''
        Assumes that create_all_actors is called before
        '''
        for actor in self.__actors:
            actor.perform_action()

    def sendGameEvents(self, events=[]):
        '''
        Returns key (string) and time (int)
        '''
        if len(events) > 0:
            logger.info("events to send: " + str(events))
        command = GameEVT(events=events)
        game_response = self.send(command)
        self.__events_to_handle += game_response.events

    def handleGameResultEvent(self, event_to_handle):
        nextPlayDate = event_to_handle.nextPlayDate
        extraId = event_to_handle.extraId
        obj_id = event_to_handle.objId
        gameObject = self.get_game_loc().get_object_by_id(obj_id)
        if gameObject is None:
            logger.critical("OMG! No such object")
        gameObject.nextPlayTimes.__setattr__(extraId, nextPlayDate)
        building = self.__itemReader.get(gameObject.item)
        for game in building.games:
            if game.id == extraId:
                game_prize = None
                if hasattr(event_to_handle.result, 'pos'):
                    prize_pos = event_to_handle.result.pos
                    game_prize = game.prizes[prize_pos]
                elif hasattr(event_to_handle.result, 'won'):
                    prize_pos = event_to_handle.result.won
                    if prize_pos is not None:
                        game_prize = game.combinations[prize_pos].prize
                if game_prize:
                    prize_item = game_prize.item
                    prize = self.__itemReader.get(prize_item)
                    count = game_prize.count
                    logger.info(u'Вы выиграли ' + prize.name +
                                u'(' + str(count) + u' шт.)')
                else:
                    logger.info('Вы ничего не выиграли.')

    def handleGainMaterialEvent(self, event_to_handle, gameObject):
        self.updateJobDone(gameObject)
        if event_to_handle.action == 'start':
            logger.info("Начата работа" + '. jobEndTime:'
                        + str(event_to_handle.jobEndTime) +
                        ', current time:' + str(self._getCurrentClientTime()))
            gameObject.target = dict2obj({'id': event_to_handle.targetId})
            gameObject.jobStartTime = event_to_handle.jobStartTime
            gameObject.jobEndTime = event_to_handle.jobEndTime
        elif event_to_handle.action == 'stop':
            logger.info("Окончена работа")

    def handleEvent(self, event_to_handle):
        if event_to_handle.action == 'addGift':
            AddGiftEventHandler(self.__game_state).handle(event_to_handle)
        elif event_to_handle.action == 'add':
            if event_to_handle.type == 'pickup':
                self.pickPickups(event_to_handle.pickups)
        elif event_to_handle.type == GameFertilizePlant.type:
            gameObject = self.get_game_loc().get_object_by_id(
                event_to_handle.objId
            )
            if gameObject is None:
                logger.critical("OMG! No such object")
            gameObject.fertilized = True
            gameObject.jobFinishTime = event_to_handle.jobFinishTime
            gameObject.jobStartTime = event_to_handle.jobStartTime
        elif event_to_handle.type == GamePlayGame.type:
            self.handleGameResultEvent(event_to_handle)
        elif event_to_handle.type == GameStartGainMaterial.type:
            gameObject = self.get_game_loc().get_object_by_id(
                event_to_handle.objId
            )
            self.handleGainMaterialEvent(event_to_handle, gameObject)
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
        self._clientTime = long(random.randrange(2800, 4000))
        self._startTime = time.time()
        return self._clientTime

    def _getCurrentClientTime(self):
        '''
        returns the current in-game time (in milliseconds)
        '''
        currentTime = self._clientTime
        currentTime += (time.time() - self._startTime) * 1000
        return currentTime

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
