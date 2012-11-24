import random
import message_factory
from message_factory import Session


class Game():

    def __init__(self, connection, user_id, auth_key):
        self.__connection = connection
        self.__session = Session(user_id, auth_key,
                                 client_version=self._getClientVersion()
                                 )
        self._createFactory()

    def start(self):
        # load items dictionary

        # send TIME request (http://java.shadowlands.ru/zombievk/go)
        # handle redirect (save new url: http://95.163.80.20/zombievk)
        # parse auth key and time id
        self.getTime()

        # get vk user info

        # send START

        # parse game state

        # send getMissions

        # handle getMissions response

        # in a loop, every 30 seconds
        # send EVT request
        # handle EVT response

    def getTime(self):
        self.send({'type': "TIME"})
        return {}

    def _getUserInfo(self):
        '''
        returns user info using vk api
        '''
        pass

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
        request.send(self.__connection)

    def _createFactory(self, requestId=None):
        self.__factory = message_factory.Factory(self.__session, requestId)
