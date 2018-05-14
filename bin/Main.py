from bin import *
import pickle


class Main:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.game = None

    def LoadAssets(self):
        # Load list of ingredients
        config = configparser.ConfigParser()
        config.read("data/ingredients.rs")
        for section in config.sections():
            name = str(config.get(section, "name"))
            type = str(config.get(section, "type"))
            baseCost = config.getfloat(section, "cost")
            INGREDIENTS_LIST.append(Ingredient(name, type, baseCost))

        # Load list of dishes
        config = configparser.ConfigParser()  # Reinitiate for new file
        config.read("data/dishes.rs")
        for section in config.sections():
            name = str(config.get(section, "name"))
            type = str(config.get(section, "type"))
            cuisine = str(config.get(section, "cuisine"))
            rawIngre = str(config.get(section, "ingredients")).strip()

            ingredients = []
            split = rawIngre.split(', ')
            for ingredient in split:
                noIngredient = True
                for i in INGREDIENTS_LIST:
                    if ingredient == i.name:
                        ingredients.append(i)
                        noIngredient = False
                        break
                if noIngredient:
                    print(ingredient)

            dish = Dish(name, type, cuisine, ingredients)
            DISHES_LIST.append(dish)
            if cuisine == "Western":
                WESTERN_DISHES.append(dish)
            elif cuisine == "Chinese":
                CHINESE_DISHES.append(dish)
            elif cuisine == "Korean":
                KOREAN_DISHES.append(dish)

        print(len(INGREDIENTS_LIST))

    def NewGame(self):
        self.game = Game(evManager)

    def SaveGame(self):
        # TODO : Save the game
        pass

    def Start(self):
        view = View(self.evManager)
        control = Controller(evManager)
        self.NewGame()  # Temporary code for testing

        control.Run()

    def Notify(self, event):
        if isinstance(event, AuthenticatedEvent):
            print(event.user)
            self.LoadAssets()
            self.Start()


if __name__ == '__main__':
    evManager = EventManager()
    #auth = Authentication(evManager)
    main = Main(evManager)
    dateManager = DateManager(evManager)
    main.LoadAssets()
    main.Start()
    #auth.mainloop()
