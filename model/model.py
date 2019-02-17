import collections
import logging
import os
from .utils import Event
from .utils import EventQueue
from .building_blocks import Resource
from .building_blocks import Inventory
from .building_blocks import Creatable
from .building_blocks import ResourceFactory
from .building_blocks import CreatableFactoryXML
from .building_blocks import WorldMap

class Objects:
    EMPTY = "empty"
    TEST = "Q"
    TREE = "tree"
    TILE = "tile"
    TILE2 = "tile2"
    TILE_BASE = "tile_base"
    PLAYER = "player"
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    UP = "up"
    DOWN = "down"


class Game:

    STATE_LOADED = "LOADED"
    STATE_READY = "READY"
    STATE_PLAYING = "PLAYING"
    STATE_BATTLE = "BATTLE"
    STATE_PAUSED = "PAUSED"
    STATE_GAME_OVER = "GAME OVER"
    END = "END"
    TICK = "Tick"
    QUIT = "Quit"

    SAVE_GAME_DIR = os.path.dirname(__file__) + "\\saves\\"
    GAME_DATA_DIR = os.path.dirname(__file__) + "\\data\\"

    def __init__(self, name: str):

        self.name = name
        self._state = Game.STATE_LOADED
        self.tick_count = 0

        self.inventory = None
        self.resources = None
        self.creatables = None
        self.creations = None
        self.map = None

        self.events = EventQueue()
        self.events.add_event(Event("{0} model created!".format(self.name)))

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._old_state = self.state
        self._state = new_state

        self.events.add_event(Event(self._state,
                                    "Game state change from {0} to {1}".format(self._old_state, self._state),
                                    Event.STATE))

    def initialise(self):

        self.state = Game.STATE_READY

        self.inventory = Inventory()
        self.resources = ResourceFactory(Game.GAME_DATA_DIR + "resources.csv")
        self.resources.load()

        self.creatables = CreatableFactoryXML(Game.GAME_DATA_DIR + "creatables.xml")
        self.creatables.load()

        self.map = WorldMap("Kingdom 2", 50, 50)
        self.map.initialise()

        self.creations = []

    def start(self):

        self.state = Game.STATE_PLAYING


    def add_creation(self, new_creation : Creatable):
        self.creations.append(new_creation)

    def new_map(self):
        self.map.generate_topology()

    def tick(self):

        if self.state != Game.STATE_PLAYING:
            return

        self.tick_count += 1

        self.events.add_event(Event(Game.TICK,
                                    "Game ticked to {0}".format(self.tick_count),
                                    Game.TICK))

        for creation in self.creations:
            if self.inventory.is_creatable(creation):
                creation.tick()

    def get_next_event(self):

        next_event = None
        if self.events.size() > 0:
            next_event = self.events.pop_event()

        return next_event

    def process_event(self, new_event):
        print("Default Game event process:{0}".format(new_event))

    def pause(self, is_paused: bool = True):

        if self.state == Game.STATE_PAUSED and is_paused is False:

            self.state = Game.STATE_PLAYING

        else:
            self.state = Game.STATE_PAUSED

    def game_over(self):

        if self._state != Game.STATE_GAME_OVER:
            logging.info("Game Over {0}...".format(self.name))

            self.state = Game.STATE_GAME_OVER

    def end(self):

        logging.info("Ending {0}...".format(self.name))

        self.state = Game.END

    def save(self):
        pass

    def load(self):
        pass

