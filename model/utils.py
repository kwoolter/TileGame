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
    def __init__(self):
        self.events = collections.deque()

    def add_event(self, new_event: Event):
        self.events.append(new_event)

    def pop_event(self):
        return self.events.pop()

    def size(self):
        return len(self.events)

    def print(self):
        for event in self.events:
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