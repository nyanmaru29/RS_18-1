from pygame.locals import *
import pygame


from .Events import *
from .Constants import *

class Controller:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.keepGoing = True

        self.shiftPressed = False
        self.ctrlPressed = False

        self.startTicks = 0

    def Run(self):
        while self.keepGoing:
            ev = TickEvent()
            self.evManager.Post(ev)

            currentTicks = pygame.time.get_ticks()
            if currentTicks - self.startTicks > 60000:
                self.startTicks = currentTicks
                ev = NewDayEvent()
                #self.evManager.Post(ev)

            for event in pygame.event.get():
                ev = None
                if event.type == QUIT:
                    ev = QuitEvent()

                elif event.type == KEYDOWN and event.key == K_e:
                    ev = NewDayEvent()

                elif event.type == KEYDOWN and event.key == K_w:
                    ev = NewGameRequestEvent()

                elif event.type == KEYDOWN and event.key == K_a:
                    ev = LoadGameRequestEvent("save1")

                elif event.type == KEYDOWN and event.key == K_s:
                    ev = SaveGameRequestEvent()

                elif event.type == KEYDOWN and event.key == K_LSHIFT:
                    self.shiftPressed = True
                    self.ctrlPressed = False

                elif event.type == KEYUP and event.key == K_LSHIFT:
                    self.shiftPressed = False

                elif event.type == KEYDOWN and event.key == K_LCTRL:
                    self.ctrlPressed = True
                    self.shiftPressed = False

                elif event.type == KEYUP and event.key == K_LCTRL:
                    self.ctrlPressed = False

                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    (x,y) = pygame.mouse.get_pos()
                    scale = (DRAW_RESOLUTION[0] / DISPLAY_RESOLUTION[0])
                    x *= scale
                    y *= scale
                    pos = (x, y)
                    if self.shiftPressed:
                        ev = ShiftLeftClickEvent(pos)
                    elif self.ctrlPressed:
                        ev = CtrlLeftClickEvent(pos)
                    else:
                        ev = LeftClickEvent(pos)

                if ev:
                    self.evManager.Post(ev)

    def Notify(self, event):
        if isinstance(event, QuitEvent):
            ev = SaveGameRequestEvent()
            self.evManager.Post(ev)

            self.keepGoing = False