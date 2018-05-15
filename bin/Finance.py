from bin import *
import json


class Finance:
    def __init__(self, folder, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.player = None # To be assigned after init

        self.folder = folder

        try:
            with open(self.folder + '/cashFlow.json', 'r') as json_file:
                json_file.close()
        except FileNotFoundError:
            key = {'daily': [], 'monthly': [], 'yearly': []}
            with open(self.folder + '/cashFlow.json', 'a+') as json_file:
                json.dump(key, json_file)
                json_file.close()

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.evManager = Main.evManager
        self.evManager.RegisterListener(self)
        print(self.evManager)

    def NewDay(self):
        cashFlow = dict()

        cashFlow[FIN_SALES] = 0
        cashFlow[FIN_INVENTORY] = 0
        cashFlow[FIN_MARKETING] = 0
        cashFlow[FIN_RENOVATION] = 0
        cashFlow[FIN_SALARY] = 0
        cashFlow[FIN_MISC] = 0
        cashFlow[FIN_CASH] = self.player.cash
        cashFlow['Profit'] = 0
        cashFlow['Expense'] = 0
        cashFlow['Day'] = Date.day
        cashFlow['Month'] = Date.month
        cashFlow['Year'] = Date.year

        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashDict = json.load(json_file)
            cashDict['daily'].append(cashFlow)
        json_file.close()

        with open(self.folder + '/cashFlow.json', 'w') as json_file:
            json.dump(cashDict, json_file, indent=2)
        json_file.close()

    def NewMonth(self):
        cashFlow = dict()
        cashFlow[FIN_SALES] = 0
        cashFlow[FIN_INVENTORY] = 0
        cashFlow[FIN_MARKETING] = 0
        cashFlow[FIN_RENOVATION] = 0
        cashFlow[FIN_SALARY] = 0
        cashFlow[FIN_MISC] = 0
        cashFlow[FIN_CASH] = self.player.cash
        cashFlow['Profit'] = 0
        cashFlow['Expense'] = 0
        cashFlow['Month'] = Date.month
        cashFlow['Year'] = Date.year

        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashDict = json.load(json_file)
            cashDict['monthly'].append(cashFlow)
        json_file.close()

        with open(self.folder + '/cashFlow.json', 'w') as json_file:
            json.dump(cashDict, json_file, indent=2)
        json_file.close()

    def NewYear(self):
        cashFlow = dict()
        cashFlow[FIN_SALES] = 0
        cashFlow[FIN_INVENTORY] = 0
        cashFlow[FIN_MARKETING] = 0
        cashFlow[FIN_RENOVATION] = 0
        cashFlow[FIN_SALARY] = 0
        cashFlow[FIN_MISC] = 0
        cashFlow[FIN_CASH] = self.player.cash
        cashFlow['Profit'] = 0
        cashFlow['Expense'] = 0
        cashFlow['Year'] = Date.year

        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashDict = json.load(json_file)
            cashDict['yearly'].append(cashFlow)
        json_file.close()

        with open(self.folder + '/cashFlow.json', 'w') as json_file:
            json.dump(cashDict, json_file, indent=2)
        json_file.close()

    def CashFlow(self, value, category):
        self.CashFlowDay(value, category)
        self.CashFlowMonth(value, category)
        self.CashFlowYear(value, category)

    #   This edit the current day's dictionary. Make sure the entry would be corresponding!! Ask Hakeem,
    def CashFlowDay(self, value, category):

        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashFlow = json.load(json_file)
        json_file.close()

        i = Date.dayNumber

        with open(self.folder + '/cashFlow.json', 'w') as json_file:

            cashFlow['daily'][i][FIN_CASH] = self.player.cash
            cashFlow['daily'][i][category] += value

            if category in [FIN_INVENTORY, FIN_MARKETING, FIN_RENOVATION, FIN_SALARY, FIN_MISC]:
                cashFlow['daily'][i]['Expense'] += value

            cashFlow['daily'][i]['Profit'] = cashFlow['daily'][i]['Sales'] - cashFlow['daily'][i]['Expense']

            json.dump(cashFlow, json_file, indent=2)
        json_file.close()

    def CashFlowMonth(self, value, category):
        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashFlow = json.load(json_file)
        json_file.close()

        i = Date.monthNumber

        with open(self.folder + '/cashFlow.json', 'w') as json_file:

            cashFlow['monthly'][i][FIN_CASH] = self.player.cash
            cashFlow['monthly'][i][category] += value

            if category in [FIN_INVENTORY, FIN_MARKETING, FIN_RENOVATION, FIN_SALARY, FIN_MISC]:
                cashFlow['monthly'][i]['Expense'] += value

            cashFlow['monthly'][i]['Profit'] = cashFlow['monthly'][i]['Sales'] - cashFlow['monthly'][i]['Expense']

            json.dump(cashFlow, json_file, indent=2)
        json_file.close()

    def CashFlowYear(self, value, category):
        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashFlow = json.load(json_file)
        json_file.close()

        i = Date.yearNumber

        with open(self.folder + '/cashFlow.json', 'w') as json_file:

            cashFlow['yearly'][i][FIN_CASH] = self.player.cash
            cashFlow['yearly'][i][category] += value

            if category in [FIN_INVENTORY, FIN_MARKETING, FIN_RENOVATION, FIN_SALARY, FIN_MISC]:
                cashFlow['yearly'][i]['Expense'] += value

            cashFlow['yearly'][i]['Profit'] = cashFlow['yearly'][i]['Sales'] - cashFlow['yearly'][i]['Expense']

            json.dump(cashFlow, json_file, indent=2)
        json_file.close()

    def CashBook(self, fiscalTerm):
        with open(self.folder + '/cashFlow.json', 'r') as json_file:
            cashFlow = json.load(json_file)
        json_file.close()
        statementList = []

        if fiscalTerm == FIN_TERM_DAILY:
            i = Date.dayNumber

            if len(cashFlow[fiscalTerm]) >= 3:
                statementList.append(cashFlow[fiscalTerm][i])
                statementList.append(cashFlow[fiscalTerm][i - 1])
                statementList.append(cashFlow[fiscalTerm][i - 2])

            else:
                for x in range(len(cashFlow[fiscalTerm])):
                    statementList.append(cashFlow[fiscalTerm][i - x])


        elif fiscalTerm == FIN_TERM_MONTHLY:
            i = Date.monthNumber

            if len(cashFlow[fiscalTerm]) >= 3:
                statementList.append(cashFlow[fiscalTerm][i])
                statementList.append(cashFlow[fiscalTerm][i - 1])
                statementList.append(cashFlow[fiscalTerm][i - 2])

            else:
                for x in range(len(cashFlow[fiscalTerm])):
                    statementList.append(cashFlow[fiscalTerm][i - x])

        elif fiscalTerm == FIN_TERM_YEARLY:
            i = Date.yearNumber

            if len(cashFlow[fiscalTerm]) >= 3:
                statementList.append(cashFlow[fiscalTerm][i])
                statementList.append(cashFlow[fiscalTerm][i - 1])
                statementList.append(cashFlow[fiscalTerm][i - 2])

            else:
                for x in range(len(cashFlow[fiscalTerm])):
                    statementList.append(cashFlow[fiscalTerm][i - x])

        return statementList

    # get daily or monthly or yearly
    # check date
    # pass the value in the dict

    def Notify(self, event):
        if isinstance(event, GameStartedEvent):
            self.NewDay()
            self.NewMonth()
            self.NewYear()

        elif isinstance(event, NewDayEvent):
            self.NewDay()
            """self.Graph(CASH, "daily")"""

        elif isinstance(event, NewMonthEvent):
            self.NewMonth()

        elif isinstance(event, NewYearEvent):
            self.NewYear()

        elif isinstance(event, RequestFinanceWindowEvent):
            ev = UpdateFinanceWindowEvent(self.CashBook(event.fiscalTerm))
            self.evManager.Post(ev)
