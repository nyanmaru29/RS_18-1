class AuthenticatedEvent:
    def __init__(self, user):
        self.name = "Authenticated Event"
        self.user = user


class TickEvent:
    def __init__(self):
        self.name = "Tick Event"


class QuitEvent:
    def __init__(self):
        self.name = "Quit Event"


class NewGameRequestEvent:
    def __init__(self):
        self.name = "New Game Request Event"


class SaveGameRequestEvent:
    def __init__(self):
        self.name = "Save Game Request Event"


class SaveGameEvent:
    def __init__(self, game):
        self.name = "Save Game Event"
        self.game = game


class LoadGameRequestEvent:
    def __init__(self, save):
        self.name = "Load Game Request Event"
        self.save = save


class GameStartedEvent:
    def __init__(self, players):
        self.name = "Game Started Event"
        self.players = players


class GameScreenLoadedEvent:
    def __init__(self):
        self.name = "Game Screen Loaded Event"


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
        self.name = "New Year Event"


class SalesReportEvent:
    def __init__(self, player, dishesServed, customers, unfedCustomers, satisfaction):
        self.name = "Sales Report Event"
        self.player = player
        self.dishesServed = dishesServed
        self.customers = customers
        self.unfedCustomers = unfedCustomers
        self.satisfaction = satisfaction


class RequestFinanceWindowEvent:
    def __init__(self, fiscalTerm):
        self.name = "Request Finance Window"
        self.fiscalTerm = fiscalTerm

class UpdateFinanceWindowEvent:
    def __init__(self, cashBook):
        self.name = "Open Finance Window"
        self.cashBook = cashBook


class MenuUpdateEvent:
    def __init__(self, dishes):
        self.name = "Update Menu Event"
        self.dishes = dishes


class AddDishEvent:
    def __init__(self, dish, price):
        self.name = "Add Dish Event"
        self.dish = dish
        self.price = price


class UpdateDishPriceEvent:
    def __init__(self, dish, price):
        self.name = "Update Dish Price Event"
        self.dish = dish
        self.price = price


class RemoveDishEvent:
    def __init__(self, dish):
        self.name = "Remove Dish Event"
        self.dish = dish


class GUICheckDishMenuEvent:
    def __init__(self, dish, container):
        self.name = "Check Dish Menu Event"
        self.dish = dish
        self.container = container


class GUICheckDishMenuResponseEvent:
    def __init__(self, dish, container):
        self.name = "Check Dish Menu Response Event"
        self.dish = dish
        self.container = container


class AddToCartEvent:
    def __init__(self, ingredient, quality, amount):
        self.name = "Add Ingredient To Cart Event"
        self.ingredient = ingredient
        self.quality = quality
        self.amount = amount


class RemoveFromCartEvent:
    def __init__(self, ingredient):
        self.name = "Remove Ingredient From Cart Event"
        self.ingredient = ingredient


class CartUpdateEvent:
    def __init__(self, cart, price):
        self.name = "Cart Update Event"
        self.cart = cart
        self.price = price

class ClearCartEvent:
    def __init__(self):
        self.name = "Clear Cart"


class BuyIngredientsEvent:
    def __init__(self, cart, price):
        self.name = "Buy Ingredients Event"
        self.cart = cart
        self.price = price


class BatchExpiredEvent:
    def __init__(self, batch):
        self.name = "Batch Expired Event"
        self.batch = batch

class InventoryUpdateEvent:
    def __init__(self, inventory):
        self.name = "Inventory Update Event"
        self.inventory = inventory


class RequestIngredientAmountEvent:
    def __init__(self, ingredient):
        self.name = "Update Item Detail"
        self.ingredient = ingredient


class ReturnIngredientAmountEvent:
    def __init__(self, ingredient, amount, expire):
        self.name = "Return Amount Event"
        self.ingredient = ingredient
        self.amount = amount
        self.expire = expire


class GUIOpenHireStaffEvent:
    def __init__(self):
        self.name = "Open Hire Staff Event"

      
class GUIOpenMyStaffEvent:
    def __init__(self):
        self.name = "Open My Staff Event"

        
class GUISelectStaffEvent:
    def __init__(self, staffType):
        self.name = "Select Staff Event"
        self.staffType = staffType


class GUISelectCuisineEvent:
    def __init__(self, cuisine):
        self.name = "Select Cuisine Event"
        self.cuisine = cuisine

class StaffUpdateRequestEvent:
    def __init__(self):
        self.name = "Staff Update Request Event"

class StaffUpdateEvent:
    def __init__(self, chefs, waiters):
        self.name = "Staff Update Event"
        self.chefs = chefs
        self.waiters = waiters


class HireChefEvent:
    def __init__(self, level, cuisine):
        self.name = "Hire Chef Event"
        self.level = level
        self.cuisine = cuisine


class HireWaiterEvent:
    def __init__(self, level):
        self.name = "Hire Waiter Event"
        self.level = level


class FireStaffEvent:
    def __init__(self, staff):
        self.name = "Fire Staff Event"
        self.staff = staff


class NoChefEvent:
    def __init__(self):
        self.name = "No Chef Event"


#UPGRADE RELATED EVENT
class UpgradeLevelEvent:
    def __init__(self):
        self.name = "Upgrade Level Event"


class UpgradeCapacityEvent:
    def __init__(self):
        self.name = "Upgrade Capacity Event"


class RestaurantUpdateEvent:
    def __init__(self, level, capacity, operatingCost, upgrades):
        self.name = "Restaurant Update Event"
        self.level = level
        self.capacity = capacity
        self.operatingCost = operatingCost
        self.upgrades = upgrades


#MARKETING RELATED EVENT
class AddMarketingEvent:
    def __init__(self, bonus):
        self.name = "Add Marketing Event"
        self.bonus = bonus


class MarketingUpdateEvent:
    def __init__(self, bonuses):
        self.name = "Marketing Update Event"
        self.bonuses = bonuses


#Controller Related Event
class LeftClickEvent:
    def __init__(self, pos):
        self.name = "Left Click Event"
        self.pos = pos

        
class CashUpdateEvent:
    def __init__(self, cash):
        self.name = "Cash Flow Update Event"
        self.cash = cash


class ShiftLeftClickEvent:
    def __init__(self, pos):
        self.name = "Shift Left Click Event"
        self.pos = pos


class CtrlLeftClickEvent:
    def __init__(self, pos):
        self.name = "Ctrl Left Click Event"
        self.pos = pos


class MouseHoverEvent:
    def __init__(self, pos):
        self.name = "Mouse Hover Event"
        self.pos = pos


class GUIRequestWindowEvent:
    def __init__(self, window, draw):
        self.name = "GUI Request Window Event"
        self.window = window
        self.draw = draw


class GUIRequestWindowRedrawEvent:
    def __init__(self, window, draw):
        self.name = "GUI Request Window Redraw Event"
        self.window = window
        self.draw = draw


class GUIRequestPopUpEvent:
    def __init__(self, popUp, draw):
        self.name = "GUI Request Pop Up Event"
        self.popUp = popUp
        self.draw = draw


class GUIRequestPopUpRedrawEvent:
    def __init__(self, popUp, draw):
        self.name = "GUI Request Pop Up Redraw Event"
        self.popUp = popUp
        self.draw = draw


class GUICloseWindowEvent:
    def __init__(self, group):
        self.name = "GUI Close Window Event"
        self.group = group


class SetTrendEvent:
    def __init__(self, trend):
        self.name = "Set Trend Event"
        self.trend = trend


class GUITooltipEvent:
    def __init__(self, text):
        self.name = "GUI Tooltip Event"
        self.text = text