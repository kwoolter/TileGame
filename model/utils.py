import collections

class Event():
    # Event Types
    DEFAULT = "default"
    STATE = "state"
    GAME = "game"
    TICK = "Tick"

    def __init__(self, name: str, description: str = None, type: str = DEFAULT):
        self.name = name
        self.description = description
        self.type = type

    def __str__(self):
        return "{0}:{1} ({2})".format(self.name, self.description, self.type)


class EventQueue():

    events = collections.deque()

    @staticmethod
    def add_event(new_event: Event):
        EventQueue.events.append(new_event)

    @staticmethod
    def pop_event():
        return EventQueue.events.pop()

    @staticmethod
    def size():
        return len(EventQueue.events)

    @staticmethod
    def print():
        for event in EventQueue.events:
            print(event)

def is_numeric(s):
    try:
        x = int(s)
    except:
        try:
            x = float(s)
        except:
            x = None
    return x