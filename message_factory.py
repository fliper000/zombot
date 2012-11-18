# coding=utf8

import hashsum
import json
import collections


def __saltFunction(string):
    result = ""
    # from classWithGo
    result += str(len(string)) + hashsum._md5hash(string + "stufff...")
    salt13 = str(len(string) * 13)  # from main.initialize
    salt2 = hashsum._md5hash(salt13 + str(len(salt13)) + str(len(string)))
    result += salt2
    characterSum = 0  # calc sum of byte codes in a string
    for i in range(0, len(string)):
        characterSum += (ord(string[i]) & 255)
    result += str(characterSum)
    return result

def calcCRC(string):
    return hashsum._md5hash(string + __saltFunction(string))

def calcSig(sessionKey, requestId, authKey):
    sig = sessionKey + str(requestId) + authKey
    sig += __saltFunction(sig)
    sig = hashsum._md5hash(sig)
    return sig

def calcAuth(requestId, authKey):
    auth = str(requestId) + authKey
    auth += __saltFunction(auth)
    sig = hashsum._md5hash(auth)
    return sig


class Session():
    '''
    This class represents session data needed
    to authenticate and sign messages
    '''
    def __init__(self, user_id, auth_key, client_version=1351866062, session_key=None):
        self.__user_id = user_id          # vk user id
        self.__session_key = session_key  # session key from TIME request
        self.__auth_session_key = None    # key from TIME response
        self.__auth_key = auth_key        # auth key from vk.com flashvars
        self.CLIENT_VERSION = client_version

    def getUserId(self):
        return self.__user_id

    def getSessionKey(self):
        return self.__session_key

    def setSessionKey(self, session_key):
        self.__session_key = session_key

    def getAuthKey(self):
        return self.__auth_key

    def getAuthSessionKey(self):
        return self.__auth_session_key


class Factory():
    '''
    This class will be used to generate signed messages
    '''
    def __init__(self, session, base_request_id=55):
        self.__session = session
        assert isinstance(self.__session, Session)
        self.BASE_REQUEST_ID = base_request_id # "magick" initial value
        self.__request_id = self.BASE_REQUEST_ID

    def createRequest(self, message_type, data, data_keys_order=None):
        request_data = {}
        request_data['data'] = self.__createDataValue(message_type, data, data_keys_order)
        request_data['crc'] = calcCRC(request_data['data'])
        return Request(request_data)

    def __createDataValue(self, message_type, data, data_keys_order):
        data_value = collections.OrderedDict()
        if data_keys_order is None:
            data_keys_order = self.__getDataKeyOrder(message_type)
        for key in data_keys_order:
            data_value[key] = ""

        data_value['user'] = self.__session.getUserId()
        if message_type == 'TIME':
            data_value['clientVersion'] = self.__session.CLIENT_VERSION
        if message_type == 'START':
            data_value['serverTime'] = data['serverTime']
            data_value['ad'] = data['ad']
            info_keys = ["uid", "bdate", "country", "first_name",
                         "sex", "city", "last_name"]
            data_value['info'] = collections.OrderedDict()
            for info_key in info_keys:
                data_value['info'][info_key] = data['info'][info_key]
            data_value['clientTime'] = data['clientTime']
            data_value['lang'] = data['lang']
        data_value['type'] = message_type
        data_value['id'] = self.__request_id
        self.__addSigOrAuth(data_value)
        if message_type == 'EVT':
            data_value['events'] = data['events']
        self._generateRequestId()
        return json.dumps(data_value, separators=(',', ':'),
                          ensure_ascii=False, encoding="utf-8")

    def __getDataKeyOrder(self, message_type):
        keys = []
        if message_type == 'TIME':
            keys = []
        if message_type == 'START':
            keys = [
                    'id',
                    'sig',
                    'clientTime',
                    'serverTime',
                    'info',
                    'type',
                    'user',
                    'ad',
                    'lang',
                    ]
        if message_type == 'EVT':
            keys = []
        return keys

    def __addSigOrAuth(self, objectData):
        sessionKey = self.__session.getSessionKey()
        auth_key = self.__session.getAuthKey()
        authSessionKey = self.__session.getAuthSessionKey()

        if sessionKey is not None:
            objectData["sig"] = calcSig(sessionKey, self.__request_id, auth_key)
        else:
            objectData["auth"] = calcAuth(self.__request_id, auth_key)
            if authSessionKey is not None:
                objectData["key"] = authSessionKey
        return objectData

    def _generateRequestId(self):
        self.__request_id += 1

    def setRequestId(self, request_id):
        self.__request_id = request_id


class Request():
    '''
    This class represents a POST body ready to be send via HTTP
    '''
    def __init__(self, data):
        self.__data = data

    def __str__(self):
        return str(self.__data)

    def getData(self):
        return self.__data


class Response():
    '''
    This class represents a response
    '''
    def __init__(self):
        pass
