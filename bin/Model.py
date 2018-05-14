from bin import *
from .Events import *
import configparser
import copy



class Game:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        # Human player exclusive modules
        self.finance = Finance(self.evManager)
        self.marketing = MarketingManager(self.evManager)

        self.trendManager = TrendManager(self.evManager)
        self.customerManager = CustomerManager(self.evManager)
        self.dishManager = DishManager(self.evManager)
        self.cart = Cart(self.evManager)

        self.players = [Player(self, self.evManager),
                        AI("Deen's Cafe", CUISINE_WESTERN, self, self.evManager),
                        AI("Emperor's Spice", CUISINE_CHINESE, self, self.evManager),
                        AI("Bap Bap", CUISINE_KOREAN, self, self.evManager)]

        for player in self.players:
            playerList = self.players[:]
            playerList.remove(player)
            player.rivals = playerList

            if not hasattr(player, "ai"):
                self.finance.player = player
                player.finance = self.finance
                player.marketing = self.marketing
                player.inventory.evManager = self.evManager

        ev = GameStartedEvent(self.players)
        self.evManager.Post(ev)


    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.customerManager.CalculateCustomerSplit(self.players)


class Player:
    def __init__(self, game, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.game = game
        self.rivals = None
        self.name = "Bichi bichi na"

        self.finance = None
        self.marketing = None
        self.upgrades = UpgradesManager(self, self.evManager)
        self.customerManager = self.game.customerManager
        self.dishManager = self.game.dishManager


        self.menu = Menu(self.evManager)
        self.inventory = Inventory()
        self.chefs = [Chef(0, CUISINE_WESTERN, self, self.evManager)]
        self.waiters = [Waiter(0, self, self.evManager), Waiter(0, self, self.evManager)]

        self.impression = 0 # Value assigned at start of day
        self.baseImpression = 10000 # Affected by satisfaction
        self.impressionRetention = 10000

        self.cash = 1000000
        self.restaurantLvl = 1
        self.restaurantCapacity = 100
        self.menu.dishLimit = 4 * self.restaurantLvl

    def SpendMoney(self, value, category):
        if value > self.cash:
            return False
        else:
            self.cash -= value
            self.finance.CashFlow(value, category)

            ev = CashUpdateEvent(self.cash)
            self.evManager.Post(ev)

            return True

    def EarnMoney(self, value, category):
        self.cash += value
        self.finance.CashFlow(value, category)

        ev = CashUpdateEvent(self.cash)
        self.evManager.Post(ev)

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
        marketingModifier = 0
        try:
            marketingModifier = self.marketing.MarketingModifier()
        except AttributeError:
            pass

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
            qualityModifier = (dish['quality']/2) * (1 + ((dish['quality'] - 2) / 20))  # Scale from 10 to 2, 2 to 1
            cost = dish['dish'].baseCost * qualityModifier
            adjustedCost = cost * costModifier

            if dish['price'] == 0:
                qualitySatisfaction = 100
            else:
                qualitySatisfaction = math.floor( ((adjustedCost / dish['price']) * 100) * (qualityModifier - 0.2) )
                if qualitySatisfaction > 100:
                    qualitySatisfaction = 100

            dish['satisfaction'] = qualitySatisfaction # To calculate dish competition for next day

            # Dish competition comparison modifier
            rivalsDishSatisfaction = None
            rivalDishes = []
            for rival in self.rivals:
                for d in rival.menu.dishes:
                    if d['dish'].name == dish['dish'].name:
                        rivalDishes.append(d)
                        break

                if len(rivalDishes) > 0:
                    rivalsDishSatisfaction = sum(d['satisfaction'] for d in rivalDishes) / len(rivalDishes)

            if rivalsDishSatisfaction:
                competitionModifier = qualitySatisfaction / rivalsDishSatisfaction
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
        totalSatisfaction *= 1 - 0.025 * ((3 - waitersLvl) ** 2)

        return math.floor(totalSatisfaction)

    def ProcessSales(self, customers):
        dishesServed = self.dishManager.ProcessDishes(self, customers)

        unfedCustomers = self.dishManager.UnfedCustomers(customers, dishesServed)
        salesRevenue = self.dishManager.SalesRevenue(dishesServed)

        satisfaction = self.CalculateSatisfaction(dishesServed, customers, unfedCustomers)
        if satisfaction < 0:
            satisfaction = 0

        if customers > 0:
            avgSatisfaction = math.floor(satisfaction / customers)
        else:
            satisfaction = 0
            avgSatisfaction = 0

        self.baseImpression = satisfaction

        self.EarnMoney(salesRevenue, SALES)

        ev = SalesReportEvent(self, dishesServed, customers, unfedCustomers, salesRevenue, avgSatisfaction)
        self.evManager.Post(ev)

        self.ProcessDay(customers) # For AI usage

    def ProcessDay(self, customers):
        pass

    def HireChef(self, level, cuisine):
        self.SpendMoney(CHEF_SALARY[level], SALARY)
        self.chefs.append(Chef(level, cuisine, self, self.evManager))

    def HireWaiter(self, level):
        self.SpendMoney(WAITER_SALARY[level], SALARY)
        self.waiters.append(Waiter(level, self, self.evManager))

    def FireStaff(self, staff):
        self.SpendMoney(staff.salary * 3, SALARY)
        try:
            self.chefs.remove(staff)
        except ValueError:
            pass
        try:
            self.waiters.remove(staff)
        except ValueError:
            pass

    def Notify(self, event):
        if isinstance(event, GameScreenLoadedEvent):
            ev = RestaurantUpdateEvent(self.restaurantLvl, self.restaurantCapacity,
                                       self.upgrades.OperatingCost(self.restaurantLvl, self.restaurantCapacity),
                                       self.upgrades)
            self.evManager.Post(ev)

            ev = MarketingUpdateEvent(self.marketing.activeBonuses)
            self.evManager.Post(ev)

            ev = InventoryUpdateEvent(self.inventory.Stock())
            self.evManager.Post(ev)

            ev = MenuUpdateEvent(self.menu.dishes)
            self.evManager.Post(ev)

            ev = CashUpdateEvent(self.cash)
            self.evManager.Post(ev)

            ev = StaffUpdateEvent(self.chefs, self.waiters)
            self.evManager.Post(ev)

        elif isinstance(event, NewDayEvent):
            ev = InventoryUpdateEvent(self.inventory.Stock())
            self.evManager.Post(ev)

        elif isinstance(event, AddDishEvent):
            if self.SpendMoney(ADD_DISH_COST, MISC):
                self.menu.AddDish(event.dish, event.price)

                ev = MenuUpdateEvent(self.menu.dishes)
                self.evManager.Post(ev)

        elif isinstance(event, UpdateDishPriceEvent):
            self.menu.UpdateDishPrice(event.dish, event.price)

            ev = MenuUpdateEvent(self.menu.dishes)
            self.evManager.Post(ev)

        elif isinstance(event, RemoveDishEvent):
            self.menu.RemoveDish(event.dish)

            ev = MenuUpdateEvent(self.menu.dishes)
            self.evManager.Post(ev)

        elif isinstance(event, BuyIngredientsEvent):
            if self.SpendMoney(event.price, INVENTORY):
                new = True
                for batch in self.inventory.batches:
                    # Loop and check for same-day batch
                    if batch.age == 0:
                        batch.AddIngredients(event.cart)
                        new = False

                if new:
                    newBatch = Batch(self.inventory, self.evManager)
                    newBatch.AddIngredients(event.cart)
                    self.inventory.batches.append(newBatch)

                ev = InventoryUpdateEvent(self.inventory.Stock())
                self.evManager.Post(ev)

        elif isinstance(event, RequestIngredientAmountEvent):
            amount = self.inventory.IngredientStock(event.ingredient)
            expired = self.inventory.IngredientExpiredAmount(event.ingredient)

            ev = ReturnIngredientAmountEvent(event.ingredient, amount, expired)
            self.evManager.Post(ev)

        elif isinstance(event, HireChefEvent):
            self.HireChef(event.level, event.cuisine)

            ev = StaffUpdateEvent(self.chefs, self.waiters)
            self.evManager.Post(ev)

        elif isinstance(event, HireWaiterEvent):
            self.HireWaiter(event.level)

            ev = StaffUpdateEvent(self.chefs, self.waiters)
            self.evManager.Post(ev)

        elif isinstance(event, FireStaffEvent):
            self.FireStaff(event.staff)

            ev = StaffUpdateEvent(self.chefs, self.waiters)
            self.evManager.Post(ev)

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

        elif isinstance(event, UpgradeLevelEvent):
            if self.SpendMoney(self.upgrades.UpgradeLevelCost(), RENOVATION):
                self.upgrades.UpgradeLevel()

                ev = RestaurantUpdateEvent(self.restaurantLvl, self.restaurantCapacity,
                                           self.upgrades.OperatingCost(self.restaurantLvl, self.restaurantCapacity),
                                           self.upgrades)
                self.evManager.Post(ev)

        elif isinstance(event, UpgradeCapacityEvent):
            if self.SpendMoney(self.upgrades.UpgradeCapacityCost(), RENOVATION):
                self.upgrades.UpgradeCapacity()

                ev = RestaurantUpdateEvent(self.restaurantLvl, self.restaurantCapacity,
                                           self.upgrades.OperatingCost(self.restaurantLvl, self.restaurantCapacity),
                                           self.upgrades)
                self.evManager.Post(ev)

        elif isinstance(event, AddMarketingEvent):
            if self.SpendMoney(event.bonus.cost, MARKETING):
                self.marketing.AddBonus(event.bonus)


class AI(Player):
    def __init__(self, name, cuisine, game, evManager):
        super().__init__(game, evManager)
        self.ai = ""
        self.name = name
        self.cuisine = cuisine

        self.chefs = [Chef(3, self.cuisine, self, self.evManager)]
        self.waiters = [Waiter(1, self, self.evManager), Waiter(1, self, self.evManager), Waiter(1, self, self.evManager)]

        self.baseImpression = 80
        self.impressionRetention = 80

        self.cash = 100000000
        self.restaurantLvl = 2
        self.restaurantCapacity = 100
        self.menu.dishLimit = 4 * self.restaurantLvl

        self.customers = 0 # For RivalsTab

        self.ProcessDay(100)

    def SpendMoney(self, value, category=None):
        self.cash -= value

    def EarnMoney(self, value, category=None):
        self.cash += value

    def GetLeastPopularDish(self):
        dish = None
        for d in self.menu.dishes:
            if dish:
                if d['dish'].ImpressionPoints() < dish.ImpressionPoints():
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

    def UpdateMenu(self):
        while len(self.menu.dishes) < self.menu.dishLimit:
            dish = None
            for d in DISHES_LIST:
                if d.cuisine == self.cuisine:
                    if d not in (x['dish'] for x in self.menu.dishes):
                        if dish:
                            if d.ImpressionPoints() > dish.ImpressionPoints():
                                dish = d
                        else:
                            dish = d
            quality = 5
            self.menu.AddDish( dish, math.floor(dish.baseCost * quality * (1 + ((quality - 1) / 10))) )



    def EvaluateInventory(self, customers):
        dishList = self.dishManager.DishesByDemand(self, customers, estimate=True)
        ingredientsList = []

        # Estimate amount of ingredients required
        for dish in dishList:
            amount = dish['demand']
            for ingredient in dish['dish'].ingredients:
                new = True

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
            expiredStock = sum(self.inventory.IngredientExpiredAmount(ingredient))
            ingredient.amount -= stock
            ingredient.amount += expiredStock
            if ingredient.amount < 0:
                ingredient.amount = 0

        return ingredientsList

    def PurchaseIngredients(self, ingredientList):
        newBatch = Batch(self.inventory, self.evManager)
        newBatch.AddIngredients(ingredientList)
        self.inventory.batches.append(newBatch)

        price = 0
        for ingredient in ingredientList:
            price += ingredient.Price(ingredient.quality) * ingredient.amount

        self.SpendMoney(price)


    def ProcessDay(self, customers):
        self.customers = customers
        
        self.EvaluateMenu()
        self.UpdateMenu()

        ingredientList = self.EvaluateInventory(customers)
        self.PurchaseIngredients(ingredientList)


    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            pass


class Staff:
    def __init__(self, player, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.player = player

        self.salary = 0
        self.deltaDay = 0

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.deltaDay += 1
            if self.deltaDay == 30:
                self.deltaDay = 0
                self.player.SpendMoney(self.salary, SALARY)

class Chef(Staff):
    def __init__(self, level, cuisine, player, evManager):
        super().__init__(player, evManager)
        self.name = ""
        self.level = level
        self.cuisine = cuisine

        self.salary = CHEF_SALARY[self.level]


class Waiter(Staff):
    def __init__(self, level, player, evManager):
        super().__init__(player, evManager)
        self.name = ""
        self.level = level

        self.salary = WAITER_SALARY[self.level]

class Menu:
    def __init__(self, evManager):
        self.evManager = evManager

        # Dishes stored as dictionary of 'dish' and 'price'
        self.dishes = []
        self.dishLimit = 0

    def AddDish(self, dish, price):
        dishDict = dict(dish=dish, price=price, satisfaction=0)
        if dish not in (d['dish'] for d in self.dishes):
            self.dishes.append(dishDict)

    def UpdateDishPrice(self, dish, price):
        for d in self.dishes:
            if d['dish'].name == dish.name:
                d['price'] = price

    def RemoveDish(self, dish):
        for d in self.dishes:
            if d['dish'].name == dish.name:
                self.dishes.remove(d)

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
            points += dish['dish'].ImpressionPoints()

        return points


class Dish:
    def __init__(self, name, type, cuisine, ingredients):
        self.name = name
        self.type = type
        self.cuisine = cuisine
        self.ingredients = ingredients

        self.numberIngredients = len(self.ingredients)

        self.baseCost = 0
        for ingredient in self.ingredients:
            self.baseCost += ingredient.baseCost

        self.trendModifier = 1.0

    def ImpressionPoints(self):
        points = DISH_POINTS * self.trendModifier
        return points


class Ingredient:
    def __init__(self, name, ingreType, baseCost):
        self.name = name
        self.type = ingreType
        self.baseCost = baseCost * 10

        self.quality = None
        self.amount = None

    def Price(self, quality):
        price = self.baseCost * quality * (1 + ((quality - 1) / 10))
        price = round(price * 100)
        return round(price / 100)



class Inventory:
    def __init__ (self):
        self.evManager = None

        self.batches = []
        self.expiredList = []

    def Stock(self):
        stock = []
        for batch in self.batches:
            for ingredient in batch.ingredients:
                new = True
                for i in stock:
                    if ingredient.name == i.name:
                        i.amount += ingredient.amount
                        new = False

                if new:
                    ing = copy.deepcopy(ingredient)
                    ing.quality = 0 # No need quality
                    ing.amount = ingredient.amount
                    stock.append(ing)

        return stock

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
                    for i in batch.ingredients:
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

        for batch in self.batches:
            ingredientsToRemove = []
            for ingredient in batch.ingredients:
                if ingredient.amount <= 0:
                    ingredientsToRemove.append(ingredient)

            for ingredient in ingredientsToRemove:
                batch.ingredients.remove(ingredient)

                try:
                    ev = ReturnIngredientAmountEvent(ingredient, self.IngredientStock(ingredient), self.IngredientExpiredAmount(ingredient))
                    self.evManager.Post(ev)
                except AttributeError:
                    pass

    def IngredientExpiredAmount(self, ingredient):
        stock = [0, 0, 0, 0, 0] # Initialise based on quality 5 to 1
        for i in self.expiredList:
            if i.name == ingredient.name:
                stock[5 - i.quality] = i.amount

        return stock

    def AddToExpiredList(self, batch):
        self.expiredList = []
        for ingredient in batch.ingredients:
            new = True
            for i in self.expiredList:
                if ingredient.name == i.name and ingredient.quality == i.quality:
                    i.amount += ingredient.amount
                    new = False

            if new:
                if ingredient.amount > 0:
                    self.expiredList.append(ingredient)

    def RemoveBatch(self, batch):
        for b in self.batches:
            if b is batch:
                self.batches.remove(b)


class Batch:
    def __init__(self, inventory, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.inventory = inventory

        self.ingredients = []
        self.age = 0

    def IngredientStock(self, ingredient):
        stock = [0, 0, 0, 0, 0] # Initialise based on quality 1 to 5
        for i in self.ingredients:
            if i.name == ingredient.name:
                quality = i.quality
                amount = i.amount
                stock[quality - 1] = amount

        stock.reverse()
        return stock

    def AddIngredients(self, list):
        new = True
        for ingredient in list:
            for i in self.ingredients:
                if i.name == ingredient.name and i.quality == ingredient.quality:
                    i.amount += ingredient.amount
                    new = False

            if new:
                self.ingredients.append(ingredient)

    def RemoveIngredients(self, ingredient, quality, amount):
        for ing in self.ingredients:
            if ing.name == ingredient.name \
                    and ing.quality == quality:
                ing.amount -= amount

                if ing.amount == 0:
                    for i in self.ingredients:
                        if i is ing:
                            self.ingredients.remove(ing)

    def Clear(self):
        self.ingredients = []

    def Notify(self, event):
        if isinstance(event, NewDayEvent):
            self.age += 1
            if self.age > 6:
                self.inventory.AddToExpiredList(self)
                self.inventory.RemoveBatch(self)


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

        elif isinstance(event, BuyIngredientsEvent):
            self.cart = []
            self.totalPrice = 0

            ev = CartUpdateEvent(self.cart, self.totalPrice)
            self.evManager.Post(ev)

        elif isinstance(event, ClearCartEvent):
            self.cart = []
            self.totalPrice = 0

            ev = CartUpdateEvent(self.cart, self.totalPrice)
            self.evManager.Post(ev)

