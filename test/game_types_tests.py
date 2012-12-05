import unittest
from game_state.game_types import CommonEqualityMixin


class GameTypesTest(unittest.TestCase):

    def testCommonEqualityStr(self):
        myObject = CommonEqualityMixin()
        myObject.attribute = ''

        # exercise & verify
        self.assertEqual("{'attribute': ''}", str(myObject))

    def testCommonEqualityRepr(self):
        myObject = CommonEqualityMixin()
        myObject.attribute = ''

        # exercise & verify
        self.assertEqual("CommonEqualityMixin: {'attribute': ''}",
                         repr(myObject))

    def testCommonEqualityNeq(self):
        myObject1 = CommonEqualityMixin()
        myObject1.attribute2 = ''
        myObject2 = CommonEqualityMixin()
        myObject2.attribute1 = ''

        # exercise & verify
        self.assertNotEqual(myObject1, myObject2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'GameTypesTest.testCommonEquality']
    unittest.main()
