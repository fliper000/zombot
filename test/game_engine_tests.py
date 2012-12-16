import unittest
import game_engine
from mock import Mock, MagicMock
import message_factory
from message_factory import calcCRC
from game_state.game_types import GameTIME, GameInfo, GameSTART
from game_state.game_event import dict2obj
import logging


class Test(unittest.TestCase):

    def createGame(self):
        connection = Mock()
        game = game_engine.Game(connection, user_id='user_id',
                                auth_key='auth_key', access_token=None,
                                user_prompt=Mock())
        game.send = MagicMock()
        return game

    def testGetTimeShouldCallSend(self):
        BASE_REQUEST_ID = 49
        # setup
        game = self.createGame()
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
        game = game_engine.Game(connection, user_id='user_id',
                                auth_key='auth_key', access_token=None,
                                user_prompt=Mock())
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
        connection = Mock()
        game = game_engine.Game(connection, user_id='user_id',
                                auth_key='auth_key', access_token=None,
                                user_prompt=Mock())
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
        USER_ID = 100000
        AUTH_KEY = 'AUTH_KEY'
        CLIENT_VERSION = 10000

        # setup
        game_server_connection = Mock()
        game_server_connection.sendRequest = Mock(return_value=calcCRC('{}')
                                                  + "${}")
        game = game_engine.Game(game_server_connection,
                                user_id=USER_ID,
                                auth_key=AUTH_KEY, access_token=None,
                                user_prompt=Mock())
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
             '"user":"' + str(USER_ID) + '",'
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

import sys
sys.argv = ['', 'Test.testHandleGameResultEvent']
unittest.main()