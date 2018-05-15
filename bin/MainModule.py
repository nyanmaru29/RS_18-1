from bin import *
import pickle
import os


class MainModule:
    def __init__(self, evManager):
        globals()
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        if not os.path.exists("../users"):
            os.makedirs("../users")

        self.folder = ""

    def NewGame(self):
        saves = [x[0] for x in os.walk(self.folder)] # Return child directories ... first entry is self.folder
        newSave = self.folder + "/save" + str(len(saves))
        os.makedirs(newSave)

        return newSave

    def StartGame(self, new=None, save=None):
        if new:
            folder = self.NewGame()
            with Game(folder, self.evManager) as game:
                pass

        elif save:
            with open(self.folder+"/"+save+"/game.save", "rb") as file:
                import pickle
                game = pickle.load(file)
                ev = GameStartedEvent(game.players)
                self.evManager.Post(ev)
                print("yes")

    def SaveGame(self, game):
        import pickle
        with open(game.folder + "/game.save", "wb") as file:
            pickle.dump(game, file)

    def Start(self):
        view = View(self.evManager)
        control = Controller(self.evManager)
        control.Run()

    def Notify(self, event):
        if isinstance(event, AuthenticatedEvent):
            self.folder = "../users/" + event.user
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

            self.Start()

        elif isinstance(event, NewGameRequestEvent):
            self.StartGame(new=True)

        elif isinstance(event, LoadGameRequestEvent):
            self.StartGame(save=event.save)

        elif isinstance(event, SaveGameEvent):
            self.SaveGame(event.game)


def main():
    Main.evManager = EventManager()
    print(Main.evManager)
    auth = Authentication(Main.evManager)
    mainModule = MainModule(Main.evManager)

    auth.mainloop()

if __name__ == "__main__":
    main()

