class GameAction(object):
    pass


class GameEVTCommand(object):
    def __init__(self, cmd,  # @ReservedAssignment
                 id,  # @ReservedAssignment
                 events):  # @ReservedAssignment
        assert isinstance(cmd, unicode)
        assert isinstance(events, list)
        assert isinstance(id, unicode)
        self.cmd = cmd
        self.events = events
        self.id = id


class GameGameState(GameAction):
    def __init__(self, isAway,  # @ReservedAssignment
                 haveTrickTreating,  # @ReservedAssignment
                 haveTreasure,  # @ReservedAssignment
                 wishlist,  # @ReservedAssignment
                 haveAttempts,  # @ReservedAssignment
                 haveRemoteFertilizeFruit,  # @ReservedAssignment
                 locationInfos,  # @ReservedAssignment
                 locationId,  # @ReservedAssignment
                 location,  # @ReservedAssignment
                 playerSettings,  # @ReservedAssignment
                 action,  # @ReservedAssignment
                 playerStatus,  # @ReservedAssignment
                 treasureRehide,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id,  # @ReservedAssignment
                 haveThanksgivingAttempt):  # @ReservedAssignment
        assert isinstance(action, unicode)
        assert isinstance(haveAttempts, bool)
        assert isinstance(haveRemoteFertilizeFruit, bool)
        assert isinstance(haveThanksgivingAttempt, bool)
        assert isinstance(haveTreasure, bool)
        assert isinstance(haveTrickTreating, bool)
        assert isinstance(id, unicode)
        assert isinstance(isAway, bool)
        assert isinstance(location, GameLocation)
        assert isinstance(locationId, unicode)
        assert isinstance(locationInfos, list)
        assert isinstance(playerSettings, GamePlayerSettings)
        assert isinstance(playerStatus, unicode)
        assert isinstance(treasureRehide, int)
        assert isinstance(type, unicode)
        assert isinstance(wishlist, list)
        self.action = action
        self.haveAttempts = haveAttempts
        self.haveRemoteFertilizeFruit = haveRemoteFertilizeFruit
        self.haveThanksgivingAttempt = haveThanksgivingAttempt
        self.haveTreasure = haveTreasure
        self.haveTrickTreating = haveTrickTreating
        self.id = id
        self.isAway = isAway
        self.location = location
        self.locationId = locationId
        self.locationInfos = locationInfos
        self.playerSettings = playerSettings
        self.playerStatus = playerStatus
        self.treasureRehide = treasureRehide
        self.type = type
        self.wishlist = wishlist


class GameGuestInfo(object):
    def __init__(self, visitingTime,
                 userId,
                 playerSettings):
        assert isinstance(playerSettings, GamePlayerSettings)
        assert isinstance(userId, unicode)
        assert isinstance(visitingTime, int)
        self.playerSettings = playerSettings
        self.userId = userId
        self.visitingTime = visitingTime


class GameItem(GameAction):
    def __init__(self, itemId,  # @ReservedAssignment
                 extraId,  # @ReservedAssignment
                 action,  # @ReservedAssignment
                 objId,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(action, unicode)
        assert isinstance(extraId, int)
        assert isinstance(itemId, unicode)
        assert isinstance(objId, int)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.action = action
        self.extraId = extraId
        self.itemId = itemId
        self.objId = objId
        self.type = type
        self.x = x
        self.y = y


class GameLocation(GameItem):
    def __init__(self, width,  # @ReservedAssignment
                 openedAreas,  # @ReservedAssignment
                 height,  # @ReservedAssignment
                 gameObjects,  # @ReservedAssignment
                 guestInfos,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(gameObjects, list)
        assert isinstance(guestInfos, list)
        assert isinstance(height, int)
        assert isinstance(id, unicode)
        assert isinstance(item, unicode)
        assert isinstance(openedAreas, list)
        assert isinstance(width, int)
        self.gameObjects = gameObjects
        self.guestInfos = guestInfos
        self.height = height
        self.id = id
        self.item = item
        self.openedAreas = openedAreas
        self.width = width


class GameLocationInfo(object):
    def __init__(self, openedAreas,
                 occupiedBrainsCount,
                 locationId,
                 maxGameObjectId,
                 giftCoins):
        assert isinstance(giftCoins, int)
        assert isinstance(locationId, unicode)
        assert isinstance(maxGameObjectId, int)
        assert isinstance(occupiedBrainsCount, int)
        assert isinstance(openedAreas, list)
        self.giftCoins = giftCoins
        self.locationId = locationId
        self.maxGameObjectId = maxGameObjectId
        self.occupiedBrainsCount = occupiedBrainsCount
        self.openedAreas = openedAreas


class GameMission(GameAction):
    def __init__(self, action,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id,  # @ReservedAssignment
                 missions):  # @ReservedAssignment
        assert isinstance(action, unicode)
        assert isinstance(id, unicode)
        assert isinstance(missions, list)
        assert isinstance(type, unicode)
        self.action = action
        self.id = id
        self.missions = missions
        self.type = type


class GameNextPlayTimes(object):
    pass


class GamePlayerSettings(object):
    def __init__(self, userName,
                 dressId,
                 hatId):
        assert isinstance(dressId, unicode)
        assert isinstance(hatId, unicode)
        assert isinstance(userName, unicode)
        self.dressId = dressId
        self.hatId = hatId
        self.userName = userName


class GameTarget(object):
    def __init__(self, id):  # @ReservedAssignment
        assert isinstance(id, int)
        self.id = id


class GameTasks(object):
    def __init__(self, Q15_11_T2,
                 Q15_11_T3,
                 Q15_11_T1):
        assert isinstance(Q15_11_T1, GameCountedItem)
        assert isinstance(Q15_11_T2, GameCountedItem)
        assert isinstance(Q15_11_T3, GameCountedItem)
        self.Q15_11_T1 = Q15_11_T1
        self.Q15_11_T2 = Q15_11_T2
        self.Q15_11_T3 = Q15_11_T3


class GameType(object):
    pass


class GameUpgradeBuilding(GameType):
    def __init__(self, count,  # @ReservedAssignment
                 finished,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(count, int)
        assert isinstance(finished, bool)
        assert isinstance(type, unicode)
        self.count = count
        self.finished = finished
        self.type = type


class GameWoodGrave(GameType):
    def __init__(self, target,  # @ReservedAssignment
                 startCounter,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 materials,  # @ReservedAssignment
                 doneCounter,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(doneCounter, int)
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(materials, list)
        assert isinstance(startCounter, int)
        assert isinstance(target, GameTarget)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.doneCounter = doneCounter
        self.id = id
        self.item = item
        self.materials = materials
        self.startCounter = startCounter
        self.target = target
        self.type = type
        self.x = x
        self.y = y


class GameWoodTree(GameType):
    def __init__(self, materialCount,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 gainStarted,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(gainStarted, bool)
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(materialCount, int)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.gainStarted = gainStarted
        self.id = id
        self.item = item
        self.materialCount = materialCount
        self.type = type
        self.x = x
        self.y = y


class GameZombieWork(GameType):
    def __init__(self, count,  # @ReservedAssignment
                 finished,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(count, int)
        assert isinstance(finished, bool)
        assert isinstance(type, unicode)
        self.count = count
        self.finished = finished
        self.type = type


class GameBase(GameType):
    def __init__(self, y,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id,  # @ReservedAssignment
                 x):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.type = type
        self.x = x
        self.y = y


class GameBridge(GameType):
    def __init__(self, level,  # @ReservedAssignment
                 nextPlayTimes,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(level, int)
        assert isinstance(nextPlayTimes, GameNextPlayTimes)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.level = level
        self.nextPlayTimes = nextPlayTimes
        self.type = type
        self.x = x
        self.y = y


class GameBuilding(GameType):
    def __init__(self, level,  # @ReservedAssignment
                 nextPlayTimes,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(level, int)
        assert isinstance(nextPlayTimes, GameNextPlayTimes)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.level = level
        self.nextPlayTimes = nextPlayTimes
        self.type = type
        self.x = x
        self.y = y


class GameCookGraveWithBrains(GameType):
    def __init__(self, speeduped,  # @ReservedAssignment
                 id,  # @ReservedAssignment
                 materials,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 isUp,  # @ReservedAssignment
                 recipeNo,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 pendingRecipes):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(isUp, bool)
        assert isinstance(item, unicode)
        assert isinstance(materials, list)
        assert isinstance(pendingRecipes, list)
        assert isinstance(recipeNo, int)
        assert isinstance(speeduped, bool)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.isUp = isUp
        self.item = item
        self.materials = materials
        self.pendingRecipes = pendingRecipes
        self.recipeNo = recipeNo
        self.speeduped = speeduped
        self.type = type
        self.x = x
        self.y = y


class GameCountedItem(GameType):
    def __init__(self, count,  # @ReservedAssignment
                 finished,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(count, int)
        assert isinstance(finished, bool)
        assert isinstance(type, unicode)
        self.count = count
        self.finished = finished
        self.type = type


class GameEVT(GameType):
    def __init__(self, type,  # @ReservedAssignment
                 events):  # @ReservedAssignment
        assert isinstance(events, list)
        assert isinstance(type, unicode)
        self.events = events
        self.type = type


class GameGameMission(GameType):
    def __init__(self, disabled,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 finished,  # @ReservedAssignment
                 tasks,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(disabled, bool)
        assert isinstance(finished, bool)
        assert isinstance(item, unicode)
        assert isinstance(tasks, GameTasks)
        assert isinstance(type, unicode)
        self.disabled = disabled
        self.finished = finished
        self.item = item
        self.tasks = tasks
        self.type = type


class GameHalloweenTower(GameType):
    def __init__(self, users,  # @ReservedAssignment
                 level,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(level, int)
        assert isinstance(type, unicode)
        assert isinstance(users, list)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.level = level
        self.type = type
        self.users = users
        self.x = x
        self.y = y


class GameMoveGameObjectToLocation(GameType):
    def __init__(self, finished,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(finished, bool)
        assert isinstance(type, unicode)
        self.finished = finished
        self.type = type


class GamePickup(GameType):
    def __init__(self, item,  # @ReservedAssignment
                 parentId,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(parentId, int)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.parentId = parentId
        self.type = type
        self.x = x
        self.y = y


class GamePier(GameType):
    def __init__(self, level,  # @ReservedAssignment
                 nextPlayTimes,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(level, int)
        assert isinstance(nextPlayTimes, GameNextPlayTimes)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.level = level
        self.nextPlayTimes = nextPlayTimes
        self.type = type
        self.x = x
        self.y = y


class GamePlant(GameType):
    def __init__(self, fertilized,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 jobFinishTime,  # @ReservedAssignment
                 jobStartTime,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(fertilized, bool)
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(jobFinishTime, unicode)
        assert isinstance(jobStartTime, unicode)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.fertilized = fertilized
        self.id = id
        self.item = item
        self.jobFinishTime = jobFinishTime
        self.jobStartTime = jobStartTime
        self.type = type
        self.x = x
        self.y = y


class GameSlag(GameType):
    def __init__(self, y,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id,  # @ReservedAssignment
                 x):  # @ReservedAssignment
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.id = id
        self.item = item
        self.type = type
        self.x = x
        self.y = y


class GameSocial(GameType):
    def __init__(self, disabled,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 finished,  # @ReservedAssignment
                 limitShow,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(disabled, bool)
        assert isinstance(finished, bool)
        assert isinstance(item, unicode)
        assert isinstance(limitShow, bool)
        assert isinstance(type, unicode)
        self.disabled = disabled
        self.finished = finished
        self.item = item
        self.limitShow = limitShow
        self.type = type


class GameStayOnLocation(GameType):
    def __init__(self, finished,  # @ReservedAssignment
                 type):  # @ReservedAssignment
        assert isinstance(finished, bool)
        assert isinstance(type, unicode)
        self.finished = finished
        self.type = type


class GameStone(GameType):
    def __init__(self, materialCount,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 gainStarted,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(gainStarted, bool)
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(materialCount, int)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.gainStarted = gainStarted
        self.id = id
        self.item = item
        self.materialCount = materialCount
        self.type = type
        self.x = x
        self.y = y


class GameStoneGrave(GameType):
    def __init__(self, target,  # @ReservedAssignment
                 startCounter,  # @ReservedAssignment
                 item,  # @ReservedAssignment
                 materials,  # @ReservedAssignment
                 doneCounter,  # @ReservedAssignment
                 y,  # @ReservedAssignment
                 x,  # @ReservedAssignment
                 type,  # @ReservedAssignment
                 id):  # @ReservedAssignment
        assert isinstance(doneCounter, int)
        assert isinstance(id, int)
        assert isinstance(item, unicode)
        assert isinstance(materials, list)
        assert isinstance(startCounter, int)
        assert isinstance(target, GameTarget)
        assert isinstance(type, unicode)
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.doneCounter = doneCounter
        self.id = id
        self.item = item
        self.materials = materials
        self.startCounter = startCounter
        self.target = target
        self.type = type
        self.x = x
        self.y = y


if __name__ == '__main__':
    pass
