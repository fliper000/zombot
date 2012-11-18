# coding=utf8

import unittest

import message_factory
import collections

class Test(unittest.TestCase):

    def createMessageFactory(self, user_id,
                                base_request_id, auth_key,
                                client_version=1351866062, session_key=None):
        session = message_factory.Session(user_id=user_id,
                                          auth_key=auth_key,
                                          client_version=client_version,
                                          session_key=session_key
                                          )
        factory = message_factory.Factory(session, base_request_id)
        return factory

    def testCrc(self):
        # set up
        message = 'some_string'

        # exercise
        actual_crc = message_factory.calcCRC(message)

        # verify
        expected_crc = "de2e201681e9fb3e8f683cdbb9c8242a"
        self.assertEqual(expected_crc, actual_crc)

    def testAuth(self):
        # setup
        auth_key = 'auth_key'  # auth key from vk.com flashvars
        request_id = 55        # request id is incremented for each request

        # exercise
        actual_auth = message_factory.calcAuth(request_id, auth_key)

        # verify
        expected_auth = '149e08e9c09de24f2d44e300d81afb45'
        self.assertEqual(expected_auth, actual_auth)

    def testSig(self):
        # setup
        auth_key = 'auth_key'  # auth key from vk.com flashvars
        key = 'session_key'    # session key from TIME request
        request_id = 12        # request id is incremented for each request

        # exercise
        actual_sig = message_factory.calcSig(key, request_id, auth_key)

        # verify
        expected_sig = '41720220e226894dfcd97d8961398231'
        self.assertEqual(expected_sig, actual_sig)

    def testCreateTimeRequest(self):
        CLIENT_VERSION = 1351866062
        USER_ID = 'USER_ID'
        MESSAGE_TYPE = 'TIME'
        BASE_REQUEST_ID = 55

        # set up
        factory = self.createMessageFactory(user_id=USER_ID,
                                            client_version=CLIENT_VERSION,
                                            base_request_id=BASE_REQUEST_ID,
                                            auth_key='AUTH_KEY')

        # exercise
        request = factory.createRequest(MESSAGE_TYPE, {})

        # verify
        expected_params = {'data':'{'
                                    '"user":"' + USER_ID+ '",'
                                    '"clientVersion":' + str(CLIENT_VERSION) + ','
                                    '"type":"' + MESSAGE_TYPE + '",'
                                    '"id":' + str(BASE_REQUEST_ID) + ','
                                    '"auth":"3419f6ad53668955e5cc93789746b821"'
                                    '}',
                           'crc':'58c1205eb0e52085305e1dc207635064'}
        actual_params = request.getData()
        self.assertEqual(expected_params, actual_params)

    def testCreateEvtRequest(self):
        USER_ID = '100000'
        MESSAGE_TYPE = 'EVT'
        BASE_REQUEST_ID = 1000000000000000
        SESSION_KEY = '-100000000000000'

        # set up
        factory = self.createMessageFactory(user_id=USER_ID,
                                            base_request_id=BASE_REQUEST_ID,
                                            auth_key='AUTH_KEY',
                                            session_key=SESSION_KEY)
        gameEvent = collections.OrderedDict()
        gameEvent['type']="action"
        gameEvent['id']=1
        gameEvent['action']="getMissions"
        data = {'events':[gameEvent]}

        # exercise
        request = factory.createRequest(MESSAGE_TYPE, data)

        # verify
        expected_params = {'data':'{'
                                    '"user":"' + USER_ID + '",'
                                    '"type":"' + MESSAGE_TYPE + '",'
                                    '"id":'    + str(BASE_REQUEST_ID) + ','
                                    '"sig":"a09c7dcbf755ec5110c1c0a48b870abf",'
                                    '"events":[{'
                                                '"type":"action","id":1,'
                                                '"action":"getMissions"}]}',
                           'crc':'91c6d72ec319794cb05c318bc998770a'
                           }
        actual_params = request.getData()
        self.assertEqual(expected_params, actual_params)

    def testCreateStartRequestUnicode(self):
        self.maxDiff = None
        USER_ID = '100000'
        MESSAGE_TYPE = 'START'
        BASE_REQUEST_ID = 10000000000000
        SESSION_KEY = 'SESSION_KEY'
        USER_BDATE = "USER_BDATE"
        USER_COUNTRY = "USER_COUNTRY"
        USER_FIRST_NAME = "USER_FIRST_NAME"
        USER_SEX = 2
        USER_CITY = u'Город'
        USER_LAST_NAME = "USER_LAST_NAME"
        CLIENT_TIME = 1000
        REFERRER = "user_apps"

        # set up
        factory = self.createMessageFactory(user_id=USER_ID,
                                            base_request_id=BASE_REQUEST_ID,
                                            auth_key='AUTH_KEY',
                                            session_key=SESSION_KEY)

        data = {"user":USER_ID,
                "type":MESSAGE_TYPE,
                "id":BASE_REQUEST_ID,
                "clientTime":CLIENT_TIME,
                "info":{"uid":int(USER_ID),
                        "bdate":USER_BDATE,
                        "country":USER_COUNTRY,
                        "first_name":USER_FIRST_NAME,
                        "sex":USER_SEX,
                        "city":USER_CITY,
                        "last_name":USER_LAST_NAME
                        },
                "ad":REFERRER,
                "serverTime":BASE_REQUEST_ID,
                "sig":"_______________",
                "lang":"en"}

        # exercise
        request = factory.createRequest(MESSAGE_TYPE, data,
                    [
                    'user',
                    'type',
                    'id',
                    'clientTime',
                    'info',
                    'ad',
                    'serverTime',
                    'sig',
                    'lang',
                    ])

        # verify
        actual_params = request.getData()
        expected_params = {'crc':'8639bc86c8cb5196db5b4ad20a1fc040',
                           'data':u'{'
                           '"user":"' + USER_ID + '",'
                           '"type":"' + MESSAGE_TYPE + '",'
                           '"id":' + str(BASE_REQUEST_ID) + ','
                           '"clientTime":' + str(CLIENT_TIME) + ','
                           '"info":{'
                                    '"uid":' + USER_ID + ','
                                    '"bdate":"' + USER_BDATE + '",'
                                    '"country":"' + USER_COUNTRY + '",'
                                    '"first_name":"' + USER_FIRST_NAME + '",'
                                    '"sex":' + str(USER_SEX) + ','
                                    '"city":"' + USER_CITY + '",'
                                    '"last_name":"' + USER_LAST_NAME + '"'
                                    '},'
                           '"ad":"' + REFERRER + '",'
                           '"serverTime":' + str(BASE_REQUEST_ID) + ','
                           '"sig":"cd70a30d872cca0722ce7c229133af3f",'
                           '"lang":"en"}',
                           }
        self.assertEqual(expected_params, actual_params)


    def testCRCUnicode(self):
        # exercise
        crc = message_factory.__dict__['calcCRC'](u'Ф')

        # verify
        expectedCRC = "401f0ddfb82395f7b8484bcf48fd360a"
        self.assertEqual(expectedCRC, crc)
