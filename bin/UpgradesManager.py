from bin import *

class UpgradesManager: #values are called when even is requested
    def __init__(self, player, evManager):
        self.evManager = evManager
        self.player = player

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.evManager = Main.evManager
        print(self.evManager)

    def UpgradeLevel(self):  # initial LEVEL is 1
        self.player.restaurantLvl = self.NextLevel()

    def UpgradeLevelCost(self):
        cost = 40000 * self.player.restaurantLvl**2 *(self.player.restaurantCapacity/100)
        return int(cost)

    def UpgradeCapacity(self):
        self.player.restaurantCapacity = self.NextCapacity()

    def UpgradeCapacityCost(self):
        cost = 20000 * self.player.restaurantLvl**2 *(self.player.restaurantCapacity/100)
        return int(cost)

    def NextLevel(self):
        if self.player.restaurantLvl < 5:
            level = self.player.restaurantLvl + 1
        else:
            level = 5

        return level

    def NextCapacity(self):
        capacity = self.player.restaurantCapacity * 2
        return capacity

    def OperatingCost(self, level, capacity):
        cost = 100 * (level**2) *(capacity/100)
        return int(cost)
