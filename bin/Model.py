from bin import *
from .Events import *
import configparser
import copy


class Game:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.dateManager = DateManager(self.evManager)
        self.customerManager = CustomerManager(self.evManager)
        self.dishManager = DishManager(self.evManager)
        self.cart = Cart(self.evManager)

        """self.player1 = Player(self, self.evManager)
        self.player2 = AI(self, self.evManager)

        self.player1.rival = self.player2
        self.player2.rival = self.player1"""

        self.players = [Player(self, self.evManager), AI(self, self.evManager)]

        ev = GameStartedEvent()
        self.evManager.Post(ev)


    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.customerManager.CalculateCustomerSplit(self.players)


class Player:
    def __init__(self, game, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.game = game
        self.rival = None

        self.customerManager = self.game.customerManager
        self.dishManager = self.game.dishManager

        self.menu = Menu(self.evManager)
        self.inventory = Inventory(self.evManager)
        self.chefs = [Chef(0, CUISINE_WESTERN, self.evManager), Chef(3, CUISINE_WESTERN, self.evManager),
                      Chef(0, CUISINE_CHINESE, self.evManager), Chef(3, CUISINE_CHINESE, self.evManager),
                      Chef(0, CUISINE_INDIAN, self.evManager)]
        self.waiters = [Waiter(0, self.evManager)]
        self.marketingBonuses = []

        self.impression = 0 # Value assigned at start of day
        self.baseImpression = 10000 # Affected by satisfaction
        self.impressionRetention = 10000

        self.cash = 10000
        self.restaurantLvl = 0
        self.restaurantCapacity = 50
        self.menu.dishLimit = 4 * self.restaurantLvl

    def SpendMoney(self, value):
        self.cash -= value

    def EarnMoney(self, value):
        self.cash += value

    def GetChefs(self):
        # Returns highest level of each cuisine chef in dictionary
        chefs = []
        for chef in self.chefs:
            if chef.cuisine not in (c['cuisine'] for c in chefs):
                chefDict = dict(cuisine=chef.cuisine, level=chef.level)
                chefs.append(chefDict)
            else:
                for c in chefs:
                    if chef.cuisine == c['cuisine'] and chef.level > c['level']:
                        c['level'] = chef.level
        return chefs

    def WaitersLevel(self):
        total = 0
        for waiter in self.waiters:
            total += waiter.level
        return total / len(self.waiters)

    def CalculateImpression(self):
        cuisineDiversityModifer = -0.1 + (self.menu.NumberOfCuisines() / 10)
        restaurantModifier = 0.05 * (self.restaurantLvl - 1)
        marketingModifier = 0 # TODO: Call function in marketing module

        if self.baseImpression > 0:
            grossImpression = self.baseImpression + self.menu.ImpressionPoints()
        else:
            grossImpression = self.menu.ImpressionPoints()

        impression = grossImpression * (1 + restaurantModifier + marketingModifier + cuisineDiversityModifer)

        # Impression retention bonus
        if impression > self.impressionRetention:
            self.impressionRetention = impression
        else:
            difference = self.impressionRetention - impression
            retention = math.floor(difference * 0.25)
            impression += retention
            self.impressionRetention -= retention

        return impression

    def CalculateSatisfaction(self, dishesServed, customers, unfedCustomers):
        # Calculate satisfaction based on base cost to sale price value
        costModifier = math.floor(self.restaurantLvl ** 1.7)
        totalSatisfaction = 0

        # Calculate gross satisfaction
        for dish in dishesServed:
            qualityModifier = ((dish['quality'] - 2) / 40) + 1  # Scale from 10 to 1.2, 1 to 1.02
            cost = dish['dish'].baseCost ** qualityModifier
            adjustedCost = cost + costModifier

            qualitySatisfaction = math.floor((adjustedCost / dish['price']) * 100)
            if qualitySatisfaction > 100:
                qualitySatisfaction = 100

            dish['satisfaction'] = qualitySatisfaction # To calculate dish competition for next day

            # Dish competition comparison modifier
            rivalDish = None
            for d in self.rival.menu.dishes:
                if d['dish'].name == dish['dish'].name:
                    rivalDish = d
                    break

            if rivalDish:
                competitionModifier = qualitySatisfaction / rivalDish['satisfaction']
                satisfaction = qualitySatisfaction * competitionModifier
            else:
                satisfaction = qualitySatisfaction

            totalSatisfaction += satisfaction * dish['sales']

            # Missing demand fulfilled penalty
            if dish['demand'] > dish['sales']:
                missingDemand = dish['demand'] - dish['sales']
                totalSatisfaction -= missingDemand * 40

        totalSatisfaction -= unfedCustomers * 200

        # Customer service modifiers
        insufficientStaff = customers - (len(self.waiters) * 30)
        if insufficientStaff > 0:
            totalSatisfaction -= insufficientStaff ** 2

        waitersLvl = int(self.WaitersLevel())
        totalSatisfaction *= 0.95 + 0.5 * (waitersLvl ** 2)

        print(dishesServed)
        return math.floor(totalSatisfaction)

    def ProcessSales(self, rawCustomers):
        dishesServed = self.dishManager.ProcessDishes(self, rawCustomers)

        customers = self.dishManager.Customers(dishesServed) # Actual number of customers
        unfedCustomers = self.dishManager.UnfedCustomers(dishesServed)
        salesRevenue = self.dishManager.SalesRevenue(dishesServed)

        satisfaction = self.CalculateSatisfaction(dishesServed, customers, unfedCustomers)
        self.baseImpression = satisfaction

        return customers, unfedCustomers, salesRevenue, satisfaction


    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.ProcessSales()

        elif isinstance(event, SalesReportEvent):
            self.baseImpression = event.satisfaction

        elif isinstance(event, AddDishEvent):
            self.menu.AddDish(event.dish, event.price)

        elif isinstance(event, UpdateDishPriceEvent):
            self.menu.UpdateDishPrice(event.dish, event.price)

        elif isinstance(event, RemoveDishEvent):
            self.menu.RemoveDish(event.dish)

        elif isinstance(event, BuyIngredientsEvent):
            new = True
            for batch in self.inventory.batches:
                # Loop and check for same-day batch
                if batch.age == 0:
                    batch.AddIngredients(event.cart)
                    new = False
            if new:
                newBatch = Batch(self.evManager)
                newBatch.AddIngredients(event.cart)
                self.inventory.batches.append(newBatch)

        elif isinstance(event, HireChefEvent):
            self.chefs.append(Chef(event.level, event.cuisine, self.evManager))

        elif isinstance(event, HireWaiterEvent):
            self.waiters.append(Waiter(event.level, self.evManager))

        elif isinstance(event, GUICheckDishMenuEvent):
            d = None
            for dish in self.menu.dishes:
                if event.dish == dish['dish']:
                    d = dish

            ev = GUICheckDishMenuResponseEvent(d, event.container)
            self.evManager.Post(ev)

        elif isinstance(event, StaffUpdateRequestEvent):
            ev = StaffUpdateEvent(self.chefs, self.waiters)
            self.evManager.Post(ev)


class AI(Player):
    def __init__(self, game, evManager):
        super().__init__(game, evManager)
        self.name = "AI 1 "

        self.chefs = [Chef(0, CUISINE_WESTERN, self.evManager), Chef(3, CUISINE_WESTERN, self.evManager),
                      Chef(0, CUISINE_CHINESE, self.evManager), Chef(3, CUISINE_CHINESE, self.evManager),
                      Chef(0, CUISINE_INDIAN, self.evManager)]
        self.waiters = [Waiter(3, self.evManager), Waiter(3, self.evManager), Waiter(3, self.evManager)]

        self.baseImpression = 80
        self.impressionRetention = 80

        self.cash = 10000
        self.restaurantLvl = 1
        self.restaurantCapacity = 100
        self.menu.dishLimit = 5 + (5 * self.restaurantLvl)

    def GetLeastPopularDish(self):
        dish = None
        for d in self.menu.dishes:
            if dish:
                if d['dish'].CalculateImpression() < dish.ImpressionPoints():
                    dish = d['dish']
            else:
                dish = d['dish']

        return dish

    def EvaluateMenu(self):
        dish = self.GetLeastPopularDish()
        if dish:
            dishImpression = dish.ImpressionPoints()
            averageImpression = self.menu.ImpressionPoints() / len(self.menu.dishes)

            if dishImpression < averageImpression * 0.75:
                self.menu.RemoveDish(dish)

    def EvaluatePricing(self):
        for dish in self.menu.dishes:
            for d in self.rival.menu.dishes:
                if dish['dish'] == d['dish'] and dish['satisfaction'] < d['dish']:
                    dish['price'] = d['price'] - 1

    def UpdateMenu(self):
        while len(self.menu.dishes) < self.menu.dishLimit:
            dish = None
            for d in DISHES_LIST:
                if d not in (x['dish'] for x in self.menu.dishes):
                    if dish:
                        if d.CalculateImpression() > dish.ImpressionPoints():
                            dish = d
                    else:
                        dish = d

            self.menu.AddDish(dish, dish.baseCost * 2)


    def EvaluateInventory(self, customers):
        dishList = self.dishManager.DishesByDemand(self, customers)
        ingredientsList = []

        # Estimate amount of ingredients required
        for dish in dishList:
            for ingredient in dish['dish'].ingredients:
                new = True

                amount = math.floor(dish['demand'] * 1.2)
                for i in ingredientsList:
                    if i.name == ingredient.name:
                        i.amount += amount
                        new = False

                if new:
                    ing = copy.deepcopy(ingredient)
                    ing.quality = 5
                    ing.amount = amount
                    ingredientsList.append(ing)

        # Calculate ingredients needed to purchase
        for ingredient in ingredientsList:
            stock = sum(self.inventory.IngredientStock(ingredient))
            ingredient.amount -= stock

        return ingredientsList

    def PurchaseIngredients(self, ingredientList):
        newBatch = Batch(self.evManager)
        newBatch.AddIngredients(ingredientList)
        self.inventory.batches.append(newBatch)


    def ProcessDay(self):
        customers = self.customerManager.CalculateCustomerSplit(self.CalculateImpression())

        self.EvaluateMenu()
        self.EvaluatePricing()
        self.UpdateMenu()

        ingredientList = self.EvaluateInventory(customers)
        self.PurchaseIngredients(ingredientList)

        salesReport = customers, unfedCustomers, salesRevenue, satisfaction = self.ProcessSales()

        print(self.name + str(satisfaction))
        #print(unfedCustomers)
        #print(customers)

        ev = RivalSalesReportEvent(*salesReport)
        self.evManager.Post(ev)

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.ProcessDay()


class Chef:
    def __init__(self, level, cuisine, evManager):
        self.evManager = evManager
        self.name = ""
        self.level = level
        self.cuisine = cuisine

        # TODO: Possible features - chef experience


class Waiter:
    def __init__(self, level, evManager):
        self.evManager = evManager
        self.name = ""
        self.level = level
        # TODO: Possible features - waiter experience


class Menu:
    def __init__(self, evManager):
        self.evManager = evManager

        # Dishes stored as dictionary of 'dish' and 'price'
        self.dishes = []
        self.dishLimit = 0

    def AddDish(self, dish, price):
        dishDict = dict(dish=dish, price=price, satisfaction=None)
        if dish not in (d['dish'] for d in self.dishes):
            self.dishes.append(dishDict)

            ev = MenuUpdateEvent(self.dishes)
            self.evManager.Post(ev)

    def UpdateDishPrice(self, dish, price):
        for d in self.dishes:
            if d['dish'].name == dish.name:
                d['price'] = price

                ev = MenuUpdateEvent(self.dishes)
                self.evManager.Post(ev)

    def RemoveDish(self, dish):
        for d in self.dishes:
            if d['dish'].name == dish.name:
                self.dishes.remove(d)

                ev = MenuUpdateEvent(self.dishes)
                self.evManager.Post(ev)

    def NumberOfCuisines(self):
        cuisines = []
        for dish in self.dishes:
            if dish['dish'].cuisine not in cuisines:
                cuisines.append(dish['dish'].cuisine)

        return len(cuisines)

    def ImpressionPoints(self):
        points = 0
        cuisines = []
        for dish in self.dishes:
            points += dish['dish'].CalculateImpression()

        return points


class Dish:
    def __init__(self, name, type, cuisine, ingredients, evManager):
        self.evManager = evManager

        self.name = name
        self.type = type
        self.cuisine = cuisine
        self.ingredients = ingredients

        self.numberIngredients = len(self.ingredients)

        self.baseCost = 0
        for ingredient in self.ingredients:
            self.baseCost += ingredient.baseCost

        self.trendModifier = 1

    def ImpressionPoints(self):
        points = DISH_POINTS * self.trendModifier
        return points


class Ingredient:
    def __init__(self, name, ingreType, baseCost, evManager):
        self.evManager = evManager

        self.name = name
        self.type = ingreType
        self.baseCost = baseCost * 1000

        self.quality = None
        self.amount = None

    def Price(self, quality):
        price = self.baseCost ** ((quality - 1)/20 + 1)
        price = math.ceil(price / 10)
        return price * 10



class Inventory:
    def __init__ (self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.batches = []

    def IngredientStock(self, ingredient):
        stock = [0, 0, 0, 0, 0] # Initialise based on quality 5 to 1
        for batch in self.batches:
            addStock = batch.IngredientStock(ingredient)
            stock = [sum(x) for x in zip(stock, addStock)] # Sums value of corresponding elements

        return stock

    def UseIngredients(self, dish, amount):
        # amount must be non-zero
        # Debits ingredient stock based on precalculated amount of dishes (amount reflects how much able to make)
        for ingredient in dish.ingredients:
            useAmount = amount
            quality = 5
            countIngredient = True
            while countIngredient:
                for batch in self.batches:
                    for i in batch.batch:
                        if i.name == ingredient.name and i.quality == quality:
                            i.amount -= useAmount
                            if i.amount < 0:
                                useAmount = - i.amount
                                i.amount = 0
                                break
                            else:
                                useAmount = 0
                                countIngredient = False
                quality -= 1


    def RemoveBatch(self, batch):
        for b in self.batches:
            if b is batch:
                self.batches.remove(b)

    def Notify(self, event):
        if isinstance(event, BatchExpiredEvent):
            self.RemoveBatch(event.batch)


class Batch:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.batch = []
        self.age = 0

    def IngredientStock(self, ingredient):
        stock = [0, 0, 0, 0, 0, 0] # Initialise based on quality 1 to 5
        for i in self.batch:
            if i.name == ingredient.name:
                quality = i.quality
                amount = i.amount
                stock[quality - 1] = amount

        stock.reverse()
        return stock

    def AddIngredients(self, list):
        new = True
        for ingredient in list:
            for i in self.batch:
                if i.name == ingredient.name and i.quality == ingredient.quality:
                    i.amount += ingredient.amount
                    new = False
            if new:
                self.batch.append(ingredient)

    def RemoveIngredients(self, ingredient, quality, amount):
        for ing in self.batch:
            if ing.name == ingredient.name \
                    and ing.quality == quality:
                ing.amount -= amount

                if ing.amount == 0:
                    for i in self.batch:
                        if i is ing:
                            self.batch.remove(ing)

    def Clear(self):
        self.batch = []

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.age += 1
            if self.age > 6:
                ev = BatchExpiredEvent(self)
                self.evManager.Post(ev)


class Cart:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.cart = []
        self.totalPrice = 0

    def AddToCart(self, ingredient, quality, amount):
        new = True
        for i in self.cart:
            if i.name == ingredient.name and i.quality == quality:
                i.amount += amount
                new = False

        if new:
            newIng = copy.deepcopy(ingredient)
            newIng.quality = quality
            newIng.amount = amount
            self.cart.append(newIng)

        self.totalPrice += ingredient.Price(quality) * amount

        # Tell View to update cart list
        ev = CartUpdateEvent(self.cart, self.totalPrice)
        self.evManager.Post(ev)

    def RemoveFromCart(self, ingredient):
        for i in self.cart:
            if i.name == ingredient.name and i.quality == ingredient.quality:
                self.cart.remove(i)

        self.totalPrice -= ingredient.Price(ingredient.quality) * ingredient.amount

        ev = CartUpdateEvent(self.cart, self.totalPrice)
        self.evManager.Post(ev)

    def Notify(self, event):
        if isinstance(event, AddToCartEvent):
            self.AddToCart(event.ingredient, event.quality, event.amount)

        elif isinstance(event, RemoveFromCartEvent):
            self.RemoveFromCart(event.ingredient)
