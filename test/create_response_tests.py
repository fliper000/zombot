import unittest

import message_factory


class TestResponse(unittest.TestCase):

    def testResponseInvalidCRCRaisesError(self):
        # setup
        try:
            response = "{}"
            # exercise
            message_factory.Response("00000000000000000000" + "$" +
                                     response)
            # verify
            self.fail("Exception should've been raised")
        except ValueError:
            pass

    def testResponseValidShouldNotRaiseError(self):
        # setup
        try:
            response = "{}"
            # exercise
            message_factory.Response(message_factory.calcCRC(response) + "$" +
                                     response)
        except ValueError:
            # verify
            self.fail("Exception should not have been raised")

    def testResponseShouldReturnParsedDict(self):
        # setup
        response = '{"cmd":"EVT","id":"1","events":[]}'

        # exercise
        actual_response = message_factory.Response(
                message_factory.calcCRC(response) + "$" +
                response).getDict()

        # verify
        expected_response = {"cmd": "EVT", "id": "1", "events": []}
        self.assertEqual(expected_response, actual_response)
