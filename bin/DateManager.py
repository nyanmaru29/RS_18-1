from bin import *


class DateManager:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        Date.day = 1
        Date.month = 1
        Date.year = 2018
        Date.dayNumber = 0
        Date.monthNumber = 0
        Date.yearNumber = 0

        self.deltaDay = 0 # To calculate weeks

    def __getstate__(self):
        self.day = Date.day
        self.month = Date.month
        self.year = Date.year
        self.dayNumber = Date.dayNumber
        self.monthNumber = Date.monthNumber
        self.yearNumber = Date.yearNumber
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.evManager = Main.evManager
        self.evManager.RegisterListener(self)
        print(self.evManager)
        Date.day = self.day
        Date.month = self.month
        Date.year = self.year
        Date.dayNumber = self.dayNumber
        Date.monthNumber = self.monthNumber
        Date.yearNumber = self.yearNumber

    def NewMonth(self):
        Date.day = 1
        Date.month += 1
        Date.monthNumber += 1
        if Date.month == 13:
            Date.month = 1
            Date.year += 1
            Date.yearNumber += 1

            ev = NewYearEvent()
            self.evManager.Post(ev)

        ev = NewMonthEvent()
        self.evManager.Post(ev)

    def LeapYear(self):
        if Date.year % 4 == 0:
            return True

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            Date.day += 1
            Date.dayNumber += 1
            self.deltaDay += 1

            if Date.day == 29:
                if Date.month == 2 and not self.LeapYear():
                    self.NewMonth()
            elif Date.day == 30:
                if Date.month == 2:
                    self.NewMonth()
            elif Date.day == 31:
                if Date.month in [4, 6, 9, 11]:
                    self.NewMonth()
            elif Date.day == 32:
                self.NewMonth()

            if self.deltaDay % 7 == 0:
                self.deltaDay = 0

                ev = NewWeekEvent()
                self.evManager.Post(ev)

            print(Date.day, Date.month, Date.year)
