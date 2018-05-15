from bin import *
import math
import random


class CustomerManager:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.totalCustomers = None
        self.prevCustomers = STARTING_CUSTOMERS

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.evManager = Main.evManager
        self.evManager.RegisterListener(self)
        print(self.evManager)

    def TotalCustomers(self):
        # TODO: Implement BETTER system to generate number of customers incorporating random events
        customers = None
        r = random.randint(0, 1) # 50% chance
        if not r:
            customers = self.prevCustomers * 1.01 # Simple growth equation
            self.prevCustomers = customers
        else:
            customers = self.prevCustomers

        self.totalCustomers = math.floor(customers)

    def CalculateCustomerSplit(self, players):
        self.TotalCustomers()

        totalImpression = 0
        for player in players:
            player.impression = player.CalculateImpression()
            if player.impression > 0:
                totalImpression += player.impression
            else:
                player.impression = 0

        for player in players:
            customers = math.floor(self.totalCustomers * (player.impression / totalImpression))

            player.ProcessSales(customers)

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.TotalCustomers()