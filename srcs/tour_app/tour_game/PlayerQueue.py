class PlayerQueue:
    def __init__(self):
        self.queue = [0 for i in range(8)] 
        self.length = 0

    def isEmpty(self):
        return self.length == 0

    # adds the player to the first empty slot in the queue and returns the position 
    def addPlayer(self, playerId):
        for i in range(len(self.queue)):

        # for idx, a in enumerate(self.queue):
            if self.queue[i] == 0:
                self.queue[i] = playerId
                self.length += 1
                return i

    def removePlayer(self, playerId):
        if not self.isEmpty():
            for i in range(len(self.queue)):
            # for idx, a in enumerate(self.queue):
                if self.queue[i] == playerId:
                    self.queue[i] = 0
                    self.length -= 1
                    break

    def contains(self, playerId):
        if playerId in self.queue:
            return True
        return False
    
    def getCopy(self):
        return self.queue.copy()

    def clear(self):
        self.queue = [0] * 8
        self.length = 0

    def getPlayers(self):
        return self.queue

    def size(self):
        return self.length
