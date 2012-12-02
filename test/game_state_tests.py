# encoding=utf-8
import unittest
from game_state.game_event import GameItemReader, dict2obj


class GameStateTest(unittest.TestCase):

    def testGameState(self):
        start_response = dict2obj({
            "cmd": "START",
            "id": "1",
            "state": {
                        "registerDate": "-2147483648",
                        "playerStatus": "@PS_ZOMBIE",
                        "dailyBonus": {},
                        "mailBonus": {
                          "bonuses": [],
                          "acceptedBonuses": []
                        },
                        "magic": {"expire": "80000000", "used": 0},
                        "definedBonuses": ["ITEM_ID", ],
                        "playerSettings": {"userName": "User name",
                                          "dressId": "ITEM_ID",
                                          "hatId": "ITEM_ID"},
                        "gameSettings": {"sound": False,
                                        "music": False,
                                        "tutorialState": 0},
                        "brainsCount": 3,
                        "buyedBrains": [],
                        "experience": 50000,
                        "level": 20,
                        "gameMoney": 1000000,
                        "cashMoney": 10,
                        "gameMoneyReal": 0,
                        "cashMoneyReal": 0,
                        "burySlots": [{"enabled": True}, ],
                        "shopOpened": ["P_09"],
                        "collectionItems": {"C_ITEM_ID": 2, },
                        "giftId": 3000,
                        "gifts": [],
                        "receivedGiftsExpire": "80000000",
                        "receivedGiftsCoins": 0,
                        "freeGiftUsers": [],
                        "storageItems": [],
                        "remoteTreasure": [],
                        "treasureHide": "-80000000",
                        "treasureExpire": "80000000",
                        "treasureCount": 0,
                        "remoteTrickTreating": [],
                        "remoteThanksgiving": [],
                        "remoteNewYearExpire": "80000000",
                        "remoteNewYear": [],
                        "remoteFertilizeFruitTreeCount": 0,
                        "remoteFertilizeFruitTree": [],
                        "wishlist": [None, None, None, None, None],
                        "buyedClothing": ["ITEM_ID"],
                        "retentionBonuses": False,
                        "npcs": {"npcClientId": 1},
                        "buffs": {"list": []}
            },
            "params": {
                "event": {
                    "action": 'gameState',
                    "locationId": 'main',
                    "haveTreasure": True,
                    "isAway": False,
                    "haveAttempts": True,
                    "treasureRehide": 100,
                    "haveTrickTreating": True,
                    "haveThanksgivingAttempt": True,
                    "haveRemoteFertilizeFruit": True,
                    "playerStatus": "@PS_ZOMBIE",
                    "locationInfos": [],
                    "wishlist": [],
                    "location": {},
                    "playerSettings": {"userName": "User name",
                                      "dressId": "ITEM_ID",
                                      "hatId": "ITEM_ID"},
                },
                "magicLimit": 500
            }
        })
        item = start_response.params.event.wishlist
        self.assertEqual([], item)
        game_items = GameItemReader()
        game_items.download('items.txt')
        game_items.read('items.txt')
        location = start_response.params.event.playerStatus
        self.assertEqual(u"Зомби", (game_items.get(location)['name']))
