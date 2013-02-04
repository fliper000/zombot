import unittest
import game_engine
from mock import Mock
import message_factory
from message_factory import calcCRC, Session
from game_state.game_types import GameTIME, GameInfo, GameSTART
from game_state.game_event import dict2obj, obj2dict
import logging
from game_state.item_reader import GameItemReader
from game_engine import GameLocation, GameInitializer, RequestSender
from game_actors_and_handlers.wood_graves import GainMaterialEventHandler
from game_actors_and_handlers.roulettes import GameResultHandler


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game_item_reader = GameItemReader()
        cls.game_item_reader.read('items.txt')

    def createGame(self, connection=None, current_time=1000,
                    client_time=1000):
        self.USER_ID = 100000
        self.AUTH_KEY = 'AUTH_KEY'

        if connection is None:
            connection = Mock()
            connection.sendRequest = Mock(return_value='{}')
        game_item_reader = Test.game_item_reader
        game = game_engine.Game(connection, user_id=self.USER_ID,
                                auth_key=self.AUTH_KEY, access_token=None,
                                user_prompt=Mock(),
                                game_item_reader=game_item_reader)
        game._get_timer = Mock()
        game._get_timer()._get_client_time = Mock(return_value=client_time)
        game._add_sending_time = Mock()
        return game

    def testGetTimeShouldCallSend(self):
        # setup
        request_sender = Mock()
        game_initializer = GameInitializer(Mock(),
                                           request_sender,
                                           Mock(),
                                           Mock(), Mock())

        # exercise
        game_initializer.get_time()

        # verify
        request_sender.send.assert_called_once_with(GameTIME())

    def testGetTimeShouldReturnKeyAndTime(self):
        # setup
        expected_key = '678652045157661214'
        expected_time = 1353868293322
        request_string = ({"cmd": "TIME", "key": expected_key,
                         "redirect":
                         "http://95.163.80.23/zombievk",
                         "id": "45", "time": expected_time})
        request_string = (request_string)
        request_sender = Mock()
        request_sender.send = Mock(return_value=dict2obj(request_string))
        game_initializer = GameInitializer(Mock(),
                                           request_sender,
                                           Mock(),
                                           Mock(), Mock())

        # exercise
        actual_key, actual_time = game_initializer.get_time()
        # verify
        self.assertEqual(expected_time, actual_time)
        self.assertEqual(expected_key, actual_key)

    def testStartGameShouldCallSend(self):
        SERVER_TIME = 1000000000L
        SESSION_KEY = 'session_key'
        USER_INFO = GameInfo(u'', u'', u'', 0L, u'', 0L, u'')
        request_sender = Mock()
        CLIENT_TIME = 3162L
        timer = Mock()
        timer._get_client_time = Mock(return_value=CLIENT_TIME)
        game_initializer = GameInitializer(timer,
                                           request_sender,
                                           Mock(),
                                           Mock(), Mock())
        game_initializer._getUserInfo = lambda: USER_INFO
        # exercise
        game_initializer.start_game(SERVER_TIME, SESSION_KEY)

        # verify
        request_sender.send.assert_called_once_with(GameSTART(
                                           clientTime=CLIENT_TIME,
                                           ad=u"user_apps",
                                           lang=u"en",
                                           serverTime=SERVER_TIME,
                                           info=USER_INFO))

    def testSendShouldCallSendRequestAndReturnResponseDict(self):
        BASE_REQUEST_ID = 49
        CLIENT_VERSION = 10000
        USER_ID = 100000
        AUTH_KEY = 'AUTH_KEY'

        # setup
        game_server_connection = Mock()
        game_server_connection.sendRequest = Mock(return_value=calcCRC('{}')
                                                  + "${}")
        factory = message_factory.Factory(Session(USER_ID, AUTH_KEY,
                                                  CLIENT_VERSION),
                                          BASE_REQUEST_ID)
        sender = RequestSender(factory, game_server_connection)

        # exercise
        sender.send({'type': 'TIME', 'id': BASE_REQUEST_ID})

        # verify
        game_server_connection.sendRequest.assert_called_once_with(
            {'data':
             '{"auth":"ce50b18d6504622d8e04615316fd2151",'
             '"type":"TIME",'
             '"clientVersion":' + str(CLIENT_VERSION) + ','
             '"user":"' + str(USER_ID) + '",'
             '"id":' + str(BASE_REQUEST_ID) + '}',
             'crc': 'c4acfa714d16e562240d42dfbfcc858e'}
            )

    def testHandleGameResultEvent(self):
        # setup
        BUILDING_ID = 278L
        logging.basicConfig(level=logging.INFO)
        event_to_handle = dict2obj({u'action': u'play',
                                    u'extraId': u'B_EMERALD_ROULETTE',
                                    u'nextPlayDate': u'43250684',
                                    u'objId': BUILDING_ID,
                                    u'result': {u'pos': 5L},
                                    u'type': u'game'}
                                   )
        building_dict = {
                             u'level': 2L,
                             u'nextPlayTimes': {u'B_EMERALD_ROULETTE':
                                                u'40061197'},
                             u'item': u'@B_FLAG_EMERALD',
                             u'y': 99L,
                             u'x': 62L,
                             u'type': u'building',
                             u'id': BUILDING_ID
                        }
        game_location = GameLocation(Test.game_item_reader,
                                     dict2obj({"gameObjects":
                                               [building_dict]}))
        building = game_location.get_object_by_id(BUILDING_ID)

        # exercise
        result_handler = GameResultHandler(Test.game_item_reader,
                                           game_location)
        result_handler.handle(event_to_handle)

        # verify
        expected = event_to_handle.nextPlayDate
        actual = building.nextPlayTimes.__dict__[event_to_handle.extraId]
        self.assertEqual(expected, actual)

    def testHandleGainMaterialEventAddsJobTime(self):
        # setup
        JOB_END_TIME = u'2458640'
        event_to_handle = dict2obj({u'action': u'start',
                                    u'doneCounter': 181L,
                                    u'jobEndTime': JOB_END_TIME,
                                    u'jobStartTime': u'1558640',
                                    u'objId': 267L,
                                    u'startCounter': 182L,
                                    u'targetId': -190L,
                                    u'type': u'gainMaterial'})
        wood_grave = dict2obj({u'startCounter': 12L,
                               u'item': u'@SC_WOOD_GRAVE2',
                               u'materials': [u'@S_19', u'@S_19', u'@S_19'],
                               u'doneCounter': 12L, u'y': 70L, u'x': 60L,
                               u'type': u'woodGraveDouble', u'id': 307L})
        game_location = Mock()
        game_location.get_object_by_id = Mock(return_value=wood_grave)

        # exercise
        GainMaterialEventHandler(Test.game_item_reader,
                                 game_location, Mock()).handle(event_to_handle)

        # verify
        self.assertEqual(wood_grave.jobEndTime, event_to_handle.jobEndTime)
        self.assertEqual(wood_grave.jobStartTime, event_to_handle.jobStartTime)

    def testHandleGainMaterialEventAddsMaterial(self):
        # setup
        TARGET_ID = -190
        GRAVE_ID = 307L
        JOB_END_TIME = u'2458640'
        location = dict2obj(
                {"gameObjects": [{
                 "type":"woodTree",
                 "item":"@SC_OAK4_A",
                 "id": TARGET_ID,
                 "x":43,
                 "y":19,
                 "materialCount":35,
                 "gainStarted": False},
                 {u'startCounter': 12L,
                               u'target': {u'id': TARGET_ID},
                               u'item': u'@SC_WOOD_GRAVE2',
                               u'jobEndTime': JOB_END_TIME,
                               u'materials': [],
                               u'doneCounter': 12L, u'y': 70L, u'x': 60L,
                               u'type': u'woodGraveDouble', u'id': GRAVE_ID},
                 ]
                })
        game_location = GameLocation(Test.game_item_reader, location)
        event_to_handle = dict2obj({u'action': u'start',
                                    u'doneCounter': 181L,
                                    u'jobEndTime': JOB_END_TIME,
                                    u'jobStartTime': u'1558640',
                                    u'objId': GRAVE_ID,
                                    u'startCounter': 182L,
                                    u'targetId': TARGET_ID,
                                    u'type': u'gainMaterial'})
        wood_grave = game_location.get_object_by_id(307L)

        # exercise
        GainMaterialEventHandler(Test.game_item_reader,
                                 game_location, Mock()).handle(event_to_handle)

        # verify
        self.assertEqual([u'@S_19'], wood_grave.materials)
        self.assertEqual(TARGET_ID, wood_grave.target.id)

    def testHandleStopGainMaterialConvertsTarget(self):
        # setup
        TARGET_ID = -190
        GRAVE_ID = 307L
        JOB_END_TIME = u'2458640'
        location = dict2obj(
                {"gameObjects": [
                    {
                        "type":"woodTree",
                        "item":"@SC_OAK5",
                        "id": TARGET_ID,
                        "x":43,
                        "y":19,
                        "materialCount":1,
                        "gainStarted": False
                    },
                    {
                        u'startCounter': 12L,
                        u'target': {u'id': TARGET_ID},
                        u'item': u'@SC_WOOD_GRAVE2',
                        u'jobEndTime': JOB_END_TIME,
                        u'materials': [],
                        u'doneCounter': 12L, u'y': 70L, u'x': 60L,
                        u'type': u'woodGraveDouble',
                        u'id': GRAVE_ID
                    }
               ]})
        game_location = GameLocation(Test.game_item_reader, location)
        wood_grave = game_location.get_object_by_id(GRAVE_ID)
        event_to_handle = dict2obj({u'action': u'stop',
                                    u'objId': GRAVE_ID,
                                    u'targetId': TARGET_ID,
                                    u'type': u'gainMaterial'})

        # exercise
        GainMaterialEventHandler(Test.game_item_reader,
                                 game_location, Mock()).handle(event_to_handle)

        # verify
        self.assertEqual([obj2dict(wood_grave), {
                                    'item': u'@SC_PICKUP_BOX_WOOD6',
                                    'id': TARGET_ID,
                                    'type': u'pickup'}],
                         obj2dict(location.gameObjects))
