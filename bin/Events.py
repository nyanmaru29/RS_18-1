class TickEvent:
    def __init__(self):
        self.name = "Tick Event"


class QuitEvent:
    def __init__(self):
        self.name = "Quit Event"


class GameStartedEvent:
    def __init__(self):
        self.name = "Game Started Event"


class NewDayEvent:
    def __init__(self):
        self.name = "New Day Event"


class NewWeekEvent:
    def __init__(self):
        self.name = "New Week Event"


class NewMonthEvent:
    def __init__(self):
        self.name = "New Week Event"


class NewYearEvent:
    def __init__(self):
        self.name = "New year Event"


class AddDishEvent:
    def __init__(self, dish, price):
        self.name = "Add Dish Event"
        self.dish = dish
        self.price = price


class BuyIngredientEvent:
    def __init__(self, ingredient, quality, amount):
        self.name = "Buy Ingredient Event"
        self.ingredient = ingredient
        self.quality = quality
        self.amount = amount


class BatchExpiredEvent:
    def __init__(self, batch):
        self.name = "Batch Expired Event"
        self.batch = batch


class HireChefEvent:
    def __init__(self, level, cuisine):
        self.name = "Hire Chef Event"
        self.level = level
        self.cuisine = cuisine


class HireWaiterEvent:
    def __init__(self):
        self.name = "Hire Waiter Event"

class NoChefEvent:
    def __init__(self):
        self.name = "No Chef Event"

class LeftClickEvent:
    def __init__(self, pos):
        self.name = "Left Click Event"
        self.pos = pos