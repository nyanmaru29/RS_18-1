from .Events import *
from .Main import *

class EventManager:
    # responsible for coordinating most communication
    # between the Model, View, and Controller
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    def RegisterListener(self, listener):
        try:
            self.listeners[listener] = 1
        except AttributeError:
            pass

    def UnregisterListener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def Post(self, event):
        keys = list(self.listeners.keys())
        for listener in keys:
            listener.Notify(event)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        pass
