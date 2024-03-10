class PlayerQueue:
    def __init__(self, maxPos):
        self.uids = [0 for i in range(maxPos)]
        self.channelNames = [None for i in range(maxPos)]
        self.length = 0

    def isEmpty(self):
        return self.length == 0

    # adds the player to the first empty slot in the uid list and returns the position 
    def addPlayer(self, playerId, channelName):
        for i in range(len(self.uids)):
        # for idx, a in enumerate(self.uids):
            if self.uids[i] == 0:
                self.uids[i] = playerId
                self.channelNames[i] = channelName
                self.length += 1
                return i

    def removePlayer(self, playerId):
        if not self.isEmpty():
            for i in range(len(self.uids)):
            # for idx, a in enumerate(self.uids):
                if self.uids[i] == playerId:
                    self.uids[i] = 0
                    self.channelNames[i] = None
                    self.length -= 1
                    break

    def contains(self, playerId):
        if playerId in self.uids:
            return True
        return False
    
    def getCopy(self):
        return self.uids.copy(), self.channelNames.copy()

    def clear(self):
        self.uids = [0] * 14
        self.channelNames = [None] * 14
        self.length = 0

    def getPlayers(self):
        return self.uids

    def size(self):
        return self.length
