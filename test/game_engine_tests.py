import unittest
import game_engine
from mock import Mock, MagicMock
import message_factory
from message_factory import calcCRC
from game_state.game_types import GameTIME, GameInfo, GameSTART
from game_state.game_event import dict2obj, obj2dict
import logging
from game_state.item_reader import GameItemReader


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game_item_reader = GameItemReader()
        cls.game_item_reader.read('items.txt')

    def createGame(self, connection=None, current_time=1000):
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
        game._getCurrentClientTime = Mock(return_value=current_time)
        return game

    def testGetTimeShouldCallSend(self):
        BASE_REQUEST_ID = 49
        # setup
        game = self.createGame()
        game.send = MagicMock()
        game._getInitialId = lambda: BASE_REQUEST_ID

        # exercise
        game.getTime()

        # verify
        game.send.assert_called_once_with(GameTIME())

    def testGetTimeShouldReturnKeyAndTime(self):
        BASE_REQUEST_ID = 49
        # setup
        connection = Mock()
        expected_key = '678652045157661214'
        expected_time = 1353868293322
        request_string = ('{"cmd":"TIME","key":"' + expected_key + '",'
                         '"redirect":'
                         '"http://95.163.80.23/zombievk",'
                         '"id":"45","time":' +
                         str(expected_time) + '}')
        request_string = (message_factory.calcCRC(request_string) +
                         '$' + request_string)
        connection.sendRequest = Mock(return_value=request_string)
        game = self.createGame(connection=connection)
        game._getInitialId = lambda: BASE_REQUEST_ID

        # exercise
        actual_key, actual_time = game.getTime()

        # verify
        self.assertEqual(expected_time, actual_time)
        self.assertEqual(expected_key, actual_key)

    def testStartGameShouldCallSend(self):
        CLIENT_TIME = 3162L
        USER_INFO = GameInfo(u'', u'', u'', 0L, u'', 0L, u'')
        SERVER_TIME = 1000000000L
        SESSION_KEY = 'session_key'
        # setup
        game = self.createGame()
        game._getUserInfo = lambda: USER_INFO
        game._getClientTime = lambda: CLIENT_TIME
        game._createFactory(SERVER_TIME)
        game.send = Mock()

        # exercise
        game.startGame(SERVER_TIME, SESSION_KEY)

        # verify
        game.send.assert_called_once_with(GameSTART(
                                           clientTime=CLIENT_TIME,
                                           ad=u"user_apps",
                                           lang=u"en",
                                           serverTime=SERVER_TIME,
                                           info=USER_INFO))
        # should set session key
        self.assertEqual(SESSION_KEY, game._getSessionKey())
        # should set request id

    def testSendShouldCallSendRequestAndReturnResponseDict(self):
        BASE_REQUEST_ID = 49
        CLIENT_VERSION = 10000

        # setup
        game_server_connection = Mock()
        game_server_connection.sendRequest = Mock(return_value=calcCRC('{}')
                                                  + "${}")
        game = self.createGame(game_server_connection)
        game._getInitialId = lambda: BASE_REQUEST_ID
        game._createFactory(BASE_REQUEST_ID)
        game._setClientVersion(CLIENT_VERSION)

        # exercise
        game.send({'type': 'TIME', 'id': BASE_REQUEST_ID})

        # verify
        game_server_connection.sendRequest.assert_called_once_with(
            {'data':
             '{"auth":"ce50b18d6504622d8e04615316fd2151",'
             '"type":"TIME",'
             '"clientVersion":' + str(CLIENT_VERSION) + ','
             '"user":"' + str(self.USER_ID) + '",'
             '"id":' + str(BASE_REQUEST_ID) + '}',
             'crc': 'c4acfa714d16e562240d42dfbfcc858e'}
            )

    def testHandleGameResultEvent(self):
        # setup
        logging.basicConfig(level=logging.INFO)
        game = self.createGame()
        event_to_handle = dict2obj({u'action': u'play',
                                    u'extraId': u'B_EMERALD_ROULETTE',
                                    u'nextPlayDate': u'43250684',
                                    u'objId': 278L,
                                    u'result': {u'pos': 5L},
                                    u'type': u'game'}
                                   )
        building = dict2obj({u'level': 2L,
                             u'nextPlayTimes': {u'B_EMERALD_ROULETTE':
                                                u'40061197'},
                             u'item': u'@B_FLAG_EMERALD',
                             u'y': 99L,
                             u'x': 62L,
                             u'type': u'building',
                             u'id': 278L})
        game.getObjectById = Mock(return_value=building)

        # exercise
        game.handleGameResultEvent(event_to_handle)

        # verify
        expected = event_to_handle.nextPlayDate
        actual = building.nextPlayTimes.__dict__[event_to_handle.extraId]
        self.assertEqual(expected, actual)

    def testHandleGainMaterialEventAddsJobTime(self):
        # setup
        game = self.createGame()
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

        # exercise
        game.handleGainMaterialEvent(event_to_handle, wood_grave)

        # verify
        self.assertEqual(wood_grave.jobEndTime, event_to_handle.jobEndTime)
        self.assertEqual(wood_grave.jobStartTime, event_to_handle.jobStartTime)

    def testHandleGainMaterialEventAddsMaterial(self):
        # setup
        game = self.createGame(current_time=2458641)
        TARGET_ID = -190
        location = dict2obj(
                {"gameObjects": [{
                 "type":"woodTree",
                 "item":"@SC_OAK4_A",
                 "id": TARGET_ID,
                 "x":43,
                 "y":19,
                 "materialCount":35,
                 "gainStarted": False}]
                })
        game.getGameLocation = Mock(return_value=location)
        JOB_END_TIME = u'2458640'
        event_to_handle = dict2obj({u'action': u'start',
                                    u'doneCounter': 181L,
                                    u'jobEndTime': JOB_END_TIME,
                                    u'jobStartTime': u'1558640',
                                    u'objId': 267L,
                                    u'startCounter': 182L,
                                    u'targetId': TARGET_ID,
                                    u'type': u'gainMaterial'})
        wood_grave = dict2obj({u'startCounter': 12L,
                               u'target': {u'id': TARGET_ID},
                               u'item': u'@SC_WOOD_GRAVE2',
                               u'jobEndTime': JOB_END_TIME,
                               u'materials': [],
                               u'doneCounter': 12L, u'y': 70L, u'x': 60L,
                               u'type': u'woodGraveDouble', u'id': 307L})

        # exercise
        game.handleGainMaterialEvent(event_to_handle, wood_grave)

        # verify
        self.assertEqual([u'@S_19'], wood_grave.materials)
        self.assertEqual(TARGET_ID, wood_grave.target.id)

    def testHandleStopGainMaterialConvertsTarget(self):
        # setup
        game = self.createGame()
        game._getCurrentClientTime = Mock(return_value=2458641)
        TARGET_ID = -190
        location = dict2obj(
                {"gameObjects": [{
                 "type":"woodTree",
                 "item":"@SC_OAK5",
                 "id": TARGET_ID,
                 "x":43,
                 "y":19,
                 "materialCount":1,
                 "gainStarted": False}]
                })
        game.getGameLocation = Mock(return_value=location)
        JOB_END_TIME = u'2458640'
        event_to_handle = dict2obj({u'action': u'stop',
                                    u'objId': 267L,
                                    u'targetId': TARGET_ID,
                                    u'type': u'gainMaterial'})
        wood_grave = dict2obj({u'startCounter': 12L,
                               u'target': {u'id': TARGET_ID},
                               u'item': u'@SC_WOOD_GRAVE2',
                               u'jobEndTime': JOB_END_TIME,
                               u'materials': [],
                               u'doneCounter': 12L, u'y': 70L, u'x': 60L,
                               u'type': u'woodGraveDouble', u'id': 307L})

        # exercise
        game.handleGainMaterialEvent(event_to_handle, wood_grave)

        # verify
        self.assertEqual([{'item': u'@SC_PICKUP_BOX_WOOD6',
                                    'objId': TARGET_ID,
                                    'type': u'pickupBox'}],
                         obj2dict(location.gameObjects))
