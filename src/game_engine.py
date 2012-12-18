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
    GameApplyGiftEvent, GameGift, GameInfo, GameDigItem, GameSlag, \
    GamePlant, GamePickItem, GameBuyItem, GamePickPickup, GameFruitTree,\
    GameFertilizePlant, GameBuilding, GameNextPlayTimes, GamePlayGame,\
    GameWoodGrave, GameStartGainMaterial, GameWoodGraveDouble
import pprint

logger = logging.getLogger(__name__)


class Game():

    def __init__(self, connection, user_id, auth_key, access_token,
                  user_prompt):
        self.__connection = connection
        self.__access_token = access_token
        self.__session = Session(user_id, auth_key,
                                 client_version=self._getClientVersion()
                                 )
        self._createFactory()
        self.__itemReader = GameItemReader()
        self.__itemReader.download('items.txt')
        self.__itemReader.read('items.txt')
        self.__user_prompt = user_prompt
        self.__selected_seed = None
        self.__events_to_handle = []
        self.__receive_gifts_with_messages = False
        self.__receive_non_free_gifts = False

    def select_plant_seed(self):
        level = self.__game_state.level
        location = self.__game_location.id
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
        self.__game_location = start_response.params.event.location
        for gameObject in self.__game_location.gameObjects:
            #if gameObject.type != 'base':
                logger.info(obj2dict(gameObject))

        self.select_plant_seed()

        # TODO send getMissions
        # TODO handle getMissions response

        self.eventLoop()

    def getGameLocation(self):
        return self.__game_location

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
        buildings = self.getAllObjectsByType(
                        GameBuilding(0L, GameNextPlayTimes(), 0L, 0L, 0L).type)
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
        wood_graves = self.getAllObjectsByType(GameWoodGrave.type)
        wood_graves += self.getAllObjectsByType(GameWoodGraveDouble.type)
        for wood_grave in wood_graves:
            for material_id in list(wood_grave.materials):
                material = self.__itemReader.get(material_id)
                name = material.name
                logger.info(u'Подбираем ' + name)
                self.pickMaterial(wood_grave, material.id)
                # update game state
                wood_grave.materials.remove(material_id)

    def removeObjectById(self, objId):
        for game_object in list(self.getGameLocation().gameObjects):
            if game_object.id == objId:
                self.getGameLocation().gameObjects.remove(game_object)

    def appendObject(self, obj):
        self.getGameLocation().gameObjects.append(obj)

    def updateJobDone(self, wood_grave):
        if hasattr(wood_grave, 'jobEndTime'):
            if int(wood_grave.jobEndTime) < self._getCurrentClientTime():
                if hasattr(wood_grave, 'target'):
                    target = self.getObjectById(wood_grave.target.id)
                    target.materialCount -= 1
                    target_item = self.__itemReader.get(target.item)
                    logger.info("Материал добыт")
                    wood_grave.materials.append(target_item.material)
                    if target.materialCount == 0:
                        logger.info("Ресурсы исчерпаны!")
                        box_item = self.__itemReader.get(target_item.box)
                        new_obj = dict2obj({'item': '@' + box_item.id,
                                            'type': box_item.type,
                                            'objId': wood_grave.target.id})
                        self.removeObjectById(wood_grave.target.id)
                        self.appendObject(new_obj)
                        logger.info("'%s' превращён в '%s'" %
                                    (target_item.name, box_item.name))
                delattr(wood_grave, 'jobEndTime')

    def automaticActions(self):
        self.receiveAllGifts()
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
        plants = self.getAllObjectsByType(GamePlant.type)
        trees = self.getAllObjectsByType(GameFruitTree.type)
        harvestItems = plants + trees
        for harvestItem in list(harvestItems):
            self.pickHarvest(harvestItem)

        slags = self.getAllObjectsByType(GameSlag.type)
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
        grounds = self.getAllObjectsByType('ground')
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

    def getAllObjectsByType(self, object_type):
        objects = []
        for game_object in self.getGameLocation().gameObjects:
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

    def getObjectById(self, objId):
        for game_object in self.getGameLocation().gameObjects:
            if game_object.id == objId:
                return game_object
        return None

    def handleGameResultEvent(self, event_to_handle):
        nextPlayDate = event_to_handle.nextPlayDate
        extraId = event_to_handle.extraId
        gameObject = self.getObjectById(event_to_handle.objId)
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
                    logger.info('Вы выиграли ' + prize.name +
                                '(' + str(count) + ' шт.)')
                else:
                    logger.info('Вы ничего не выиграли.')

    def handleGainMaterialEvent(self, event_to_handle, gameObject):
        self.updateJobDone(gameObject)
        if event_to_handle.action == 'start':
            logger.info("Начата работа")
            gameObject.target = dict2obj({'id': event_to_handle.targetId})
            gameObject.jobStartTime = event_to_handle.jobStartTime
            gameObject.jobEndTime = event_to_handle.jobEndTime
        elif event_to_handle.action == 'stop':
            logger.info("Окончена работа")

    def handleEvent(self, event_to_handle):
        if event_to_handle.action == 'addGift':
            logger.info(u"Получен подарок.")
            gift = event_to_handle.gift
            self.receiveGift(gift)
        elif event_to_handle.action == 'add':
            if event_to_handle.type == 'pickup':
                self.pickPickups(event_to_handle.pickups)
        elif event_to_handle.type == GameFertilizePlant(u"", u"", 0L).type:
            # fertilized
            # getObjectById
            gameObject = self.getObjectById(event_to_handle.objId)
            if gameObject is None:
                logger.critical("OMG! No such object")
            gameObject.fertilized = True
            gameObject.jobFinishTime = event_to_handle.jobFinishTime
            gameObject.jobStartTime = event_to_handle.jobStartTime
        elif event_to_handle.type == GamePlayGame.type:
            self.handleGameResultEvent(event_to_handle)
        elif event_to_handle.type == GameStartGainMaterial.type:
            gameObject = self.getObjectById(event_to_handle.objId)
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
