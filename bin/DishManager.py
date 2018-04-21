from bin import *
import copy


class DishManager:
    def __init__(self, evManager):
        self.evManager = evManager

    def Customers(self, dishList):
        # Returns actual number of customers in restaurant
        customers = 0
        for dish in dishList:
            customers += dish['demand']
        return customers


    def UnfedCustomers(self, dishList):
        customers = 0
        sales = 0
        for dish in dishList:
            customers += dish['demand']
            sales += dish['sales']
        return customers - sales

    def SalesRevenue(self, dishList):
        revenue = 0
        for dish in dishList:
            revenue += dish['price'] * dish['sales']
        return revenue

    def DishesByDemand(self, player, customers):
        dishList = []
        menuImpression = player.menu.ImpressionPoints

        # Arrange dishes based on demand
        for dish in player.menu.dishes:
            demand = math.floor((dish.ImpressionPoints / menuImpression) * customers)
            dishDict = dict(dish=dish['dish'], price=dish['price'], demand=demand, sales=int(0), quality=0)
            if len(dishList) == 0:
                dishList.append(dishDict)
            else:
                for d in dishList:
                    if dishDict not in dishList:
                        if demand > d['demand'] and dish is not d['dish']:
                            i = dishList.index(d)
                            dishList = dishList[:i] + [dishDict] + dishList[i:]
                        else:
                            dishList.append(dishDict)

        return dishList

    def GetDishAvailable(self, dishList, player):
        checkDishes = copy.deepcopy(dishList)
        stock = copy.deepcopy(player.inventory)

        doLoop = True
        while doLoop:
            toStopCheck = []
            leftoverDemand = 0
            stockCopy = copy.deepcopy(stock)

            for d1 in checkDishes:
                dish = None
                for d2 in dishList:
                    if d1['dish'].name == d2['dish'].name:
                        dish = d2

                first = True
                lowestAmount = 0
                for ingredient in dish['dish'].ingredients:
                    ingredientAmount = sum(stockCopy.IngredientStock(ingredient))
                    if first:
                        if ingredientAmount < d1['demand']:
                            lowestAmount = ingredientAmount
                        else:
                            lowestAmount = d1['demand']
                    else:
                        if ingredientAmount < lowestAmount:
                            lowestAmount = ingredientAmount
                    first = False

                dish['sales'] = lowestAmount
                if dish['sales'] > 0:
                    stockCopy.UseIngredients(dish['dish'], dish['sales'])

                missingDemand = d1['demand'] - dish['sales']
                leftoverDemand += missingDemand

                if missingDemand:
                    toStopCheck.append(d1)
                    if dish['sales'] > 0:
                        stock.UseIngredients(dish['dish'], dish['sales'])

            for dish in toStopCheck:
                if dish in checkDishes:
                    checkDishes.remove(dish)

            for dish in checkDishes:
                dish['demand'] += math.floor(leftoverDemand / len(checkDishes))

            if len(toStopCheck) == 0:
                break

        return dishList

    def ProcessDishes(self, player, customers):
        chefs = player.GetChefs()
        if len(chefs) == 0:
            ev = NoChefEvent()
            self.evManager.Post(ev)
            return

        dishList = self.DishesByDemand(player, customers)
        dishList = self.GetDishAvailable(dishList, player)


        for dish in dishList:
            dishAmount = dish['sales']

            # Calculate dish quality based on ingredients
            if dishAmount > 0:
                quality = 0
                for ingredient in dish['dish'].ingredients:
                    stock = player.inventory.IngredientStock(ingredient)
                    ingredientAmount = dishAmount
                    ingredientQuality = 5
                    for amount in stock:
                        if amount > 0:
                            amount -= ingredientAmount
                            if amount < 0:
                                ingredientAmount = - amount
                                quality += (dishAmount - ingredientAmount) * ingredientQuality
                            else:
                                quality += ingredientAmount * ingredientQuality
                                break
                        ingredientQuality -= 1
                player.inventory.UseIngredients(dish['dish'], dishAmount)

                averageQuality = quality / (dish['dish'].numberIngredients * dishAmount)
                averageQuality = averageQuality * 2 # Scale from 0 - 5 to 0 - 10

                # Chef quality modifier
                qualityModifier = 1
                if dish['dish'].cuisine not in (c['cuisine'] for c in chefs):
                    qualityModifier -= 0.2 # -20% quality
                else:
                    for chef in chefs:
                        if dish['dish'].cuisine == chef['cuisine']:
                            qualityModifier -= 0.1 * (3 - chef['level']) # 3 is max level

                dish['quality'] = math.floor(averageQuality * qualityModifier)

        return dishList
