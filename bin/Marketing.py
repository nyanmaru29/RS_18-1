from bin import *
import configparser


class Marketing:
    def __init__(self, evManager):
        self.evManager = evManager

        self.activeBonuses = []

        # Load list of marketing strats
        config = configparser.ConfigParser()
        config.read("data/marketing.rs")
        for section in config.sections():
            name = str(config.get(section, "name"))
            modifier = config.getfloat(section, "modifier")
            cost = config.getint(section, "cost")
            duration = config.getint(section, "duration")
            desc = config.get(section, "desc")

            MARKETING_LIST.append(MarketingBonus(name, modifier, cost, duration, desc))

    def __getstate__(self):
        self.marketingList = MARKETING_LIST
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        MARKETING_LIST.extend(self.marketingList)
        self.evManager = Main.evManager
        print(self.evManager)

    # return value total bonus
    # list of marketing player owns
    def MarketingModifier(self):
        modifier = 0
        for bonus in self.activeBonuses:
            modifier += bonus.modifier

        return modifier

    def AddBonus(self, bonus):
        newBonus = copy.deepcopy(bonus)
        newBonus.Activate(self, self.evManager)

        self.activeBonuses.append(newBonus)

        ev = MarketingUpdateEvent(self.activeBonuses)
        self.evManager.Post(ev)

    def RemoveBonus(self, bonus):
        for b in self.activeBonuses:
            if bonus.name == b.name:
                self.activeBonuses.remove(b)

        ev = MarketingUpdateEvent(self.activeBonuses)
        self.evManager.Post(ev)


class MarketingBonus:
    def __init__(self, name, modifier, cost, duration, desc):
        self.evManager = None
        self.parent = None

        self.name = name
        self.modifier = modifier
        self.cost = cost
        self.duration = duration
        self.desc = desc

        self.dayPassed = 0

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        try:
            self.evManager.RegisterListener(self) # Only for activated MarketingBonus
        except AttributeError:
            pass

    def Activate(self, parent, evManager):
        self.parent = parent
        self.evManager = evManager
        self.evManager.RegisterListener(self)

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.dayPassed += 1
            if self.dayPassed == self.duration:
                self.parent.RemoveBonus(self)