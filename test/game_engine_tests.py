import unittest
import game_engine
from mock import Mock

class Test(unittest.TestCase):
    def testGetTimeShouldCallSend(self):
        BASE_REQUEST_ID = 49
        # setup
        connection = Mock()
        game = game_engine.Game(connection, user_id='user_id', auth_key='auth_key')
        game.send = Mock()
        game._getInitialId = lambda: BASE_REQUEST_ID

        # exercise
        game.getTime()

        # verify
        game.send.assert_called_once_with({"type":"TIME",
                                           "id": BASE_REQUEST_ID })

    def testStartShouldCallSend(self):
        CLIENT_TIME = 3162
        USER_INFO = 'user_info'
        SERVER_TIME = 1000000000
        SESSION_KEY = 'session_key'
        # setup
        connection = Mock()
        game = game_engine.Game(connection, user_id='user_id', auth_key='auth_key')
        game._getUserInfo = lambda: USER_INFO
        game._getClientTime = lambda: CLIENT_TIME
        game._createFactory(SERVER_TIME)
        game.send = Mock()

        # exercise
        game.startGame(SERVER_TIME, SESSION_KEY)

        # verify
        game.send.assert_called_once_with({"type":"START",
                                           "clientTime":CLIENT_TIME,
                                           "ad":"user_apps",
                                           "lang":"en",
                                           "serverTime":SERVER_TIME,
                                           "info": USER_INFO})
        # should set session key
        self.assertEqual(SESSION_KEY, game._getSessionKey())
        # should set request id

    def testSendShouldCallConnectionSendRequest(self):
        BASE_REQUEST_ID = 49
        USER_ID = 100000
        AUTH_KEY = 'AUTH_KEY'
        CLIENT_VERSION = 10000

        # setup
        game_server_connection = Mock()
        game_server_connection.sendRequest = Mock()
        game = game_engine.Game(game_server_connection,
                                user_id = USER_ID,
                                auth_key=AUTH_KEY)
        game._getInitialId = lambda: BASE_REQUEST_ID
        game._setClientVersion(CLIENT_VERSION)

        # exercise
        game.send({'type':'TIME', 'id': BASE_REQUEST_ID})

        # verify
        game_server_connection.sendRequest.assert_called_once_with(
            {'data':
             '{"auth":"ce50b18d6504622d8e04615316fd2151",'
             '"type":"TIME",'
             '"clientVersion":' + str(CLIENT_VERSION) + ','
             '"user":"' + str(USER_ID) + '",'
             '"id":' + str(BASE_REQUEST_ID) + '}',
             'crc':'c4acfa714d16e562240d42dfbfcc858e'}
            )

    def testGetInitialIdShouldReturn40to60(self):
        self.assertLessEqual(40, game_engine.Game(None, None, None)._getInitialId())
        self.assertGreaterEqual(60, game_engine.Game(None, None, None)._getInitialId())
