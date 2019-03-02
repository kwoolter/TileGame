import logging
import os
import random

from .building_blocks import Creatable
from .building_blocks import CreatableFactoryXML
from .building_blocks import Inventory
from .building_blocks import ResourceFactory
from .building_blocks import WorldMap
from .utils import Event
from .utils import EventQueue
from .StatEngine import *
from .game_stats import *


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

    EVENT_ACTION_FAIL = "Action failed"

    SAVE_GAME_DIR = os.path.join(os.path.dirname(__file__), "saves")
    GAME_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def __init__(self, name: str):

        self.name = name
        self._state = Game.STATE_LOADED
        self.tick_count = 0

        self.stats = KingdomStats()
        self.inventory = None
        self.resources = None
        self.creatables = None
        self.creations = None
        self.map = None

        EventQueue.add_event(Event("{0} model created!".format(self.name)))

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._old_state = self.state
        self._state = new_state

        EventQueue.add_event(Event(self._state,
                                   "Game state change from {0} to {1}".format(self._old_state, self._state),
                                   Event.STATE))

    @property
    def current_year(self):
        return self.stats.get_stat(CurrentYear.NAME).value

    @property
    def current_season_name(self):
        season =  int(self.stats.get_stat(CurrentSeason.NAME).value)
        return CurrentSeason.season_number_to_name[season]

    def initialise(self):

        self.state = Game.STATE_READY

        self.stats.initialise()

        self.inventory = Inventory()
        self.resources = ResourceFactory(os.path.join(Game.GAME_DATA_DIR, "resources.csv"))
        self.resources.load()

        self.creatables = CreatableFactoryXML(os.path.join(Game.GAME_DATA_DIR, "creatables.xml"))
        self.creatables.load()

        self.map = WorldMap("Kingdom 2", 100, 100)
        self.map.initialise()

        resource_types = ResourceFactory.get_resource_types()

        for type in resource_types:
            new_resource = ResourceFactory.get_resource(type)
            self.inventory.add_resource(new_resource, random.randint(100020, 1000160))

        self.creations = {}
        self.add_initial_creations()

    def start(self):

        self.state = Game.STATE_PLAYING

    def add_initial_creations(self):

        tile_to_creation = {
            WorldMap.TILE_FOREST: (WorldMap.MATERIAL_TREE, WorldMap.MATERIAL_TREE2),
            WorldMap.TILE_SCRUB: WorldMap.MATERIAL_SCRUB1,
            WorldMap.TILE_BORDER: WorldMap.TILE_BORDER
        }

        for y in range(0, self.map.height):
            for x in range(0, self.map.width):
                tile = self.map.get(x, y)
                if tile == WorldMap.TILE_BORDER:
                    pass
                    #self.add_creation_by_name(tile, x, y, change=Inventory.CHANGE_NO_CHANGE)
                elif tile in tile_to_creation.keys() and random.randint(0, 10) > 9:
                    tiles = tile_to_creation[tile]
                    if isinstance(tiles, tuple) is True:
                        new_creation = random.choice(tiles)
                    else:
                        new_creation = tiles
                    self.add_creation_by_name(new_creation, x, y, change=Inventory.CHANGE_NO_CHANGE)

    # Add a new creation to the world
    def add_creation(self, new_creation: Creatable, x: int = 0, y: int = 0, change: int = Inventory.CHANGE_DEBIT):

        success = False

        # Check if a creation can be built on the current tile...
        tile = self.map.get(x, y)
        if self.map.get(x, y) in (WorldMap.TILE_SHALLOWS,
                                  WorldMap.TILE_SEA,
                                  WorldMap.TILE_DEEP_SEA,
                                  WorldMap.TILE_BORDER):

            EventQueue.add_event(Event(Game.EVENT_ACTION_FAIL,
                                       "Can't build creations on {0}!".format(tile),
                                       Game.EVENT_ACTION_FAIL))

        # Check if the current tile is not already occupied...
        elif (x, y) in self.creations.keys():
            creation = self.get_creation(x, y)
            EventQueue.add_event(Event(Game.EVENT_ACTION_FAIL,
                                       "Already a creation {2} at ({0},{1})!".format(x, y, creation.name),
                                       Game.EVENT_ACTION_FAIL))

        # Check if the new creation can be built from current resources..
        elif change == Inventory.CHANGE_DEBIT and self.inventory.is_creatable(new_creation) is False:
            EventQueue.add_event(Event(Game.EVENT_ACTION_FAIL,
                                       "Insufficient resources in inventory to create {0}!".format(
                                           new_creation.name),
                                       Game.EVENT_ACTION_FAIL))

        else:
            # If it can then assign the required resources and add the creation to the world
            self.inventory.assign_resources(new_creation, change=change)
            self.creations[(x, y)] = new_creation
            print("Added creation {0} at ({1},{2})".format(new_creation.name, x, y))
            success = True

        return success

    def delete_creation(self, x: int = 0, y: int = 0):
        creation = self.get_creation(x, y)
        if creation is not None:
            self.inventory.assign_resources(creation, change=Inventory.CHANGE_CREDIT)
            del self.creations[(x, y)]

    def add_creation_by_name(self, new_creation_name: str, x: int = 0, y: int = 0, change=Inventory.CHANGE_DEBIT):
        new_creation = self.creatables.get_creatable_copy(new_creation_name)
        return self.add_creation(new_creation, x, y, change)

    def get_creation(self, x: int, y: int):
        if (x, y) in self.creations.keys():
            return self.creations[(x, y)]
        else:
            return None

    def new_map(self):
        self.creations = {}
        self.map.initialise()

    def tick(self):

        if self.state != Game.STATE_PLAYING:
            return

        self.tick_count += 1

        self.stats.update_stat(KingdomStats.INPUT_TICK_COUNT, self.tick_count)

        EventQueue.add_event(Event(Game.TICK,
                                   "Game ticked to {0}".format(self.tick_count),
                                   Game.TICK))

        for creation in self.creations.values():
            creation.tick()
            if self.inventory.is_creatable(creation):
                creation.tick()

    def get_next_event(self):

        next_event = None
        if EventQueue.size() > 0:
            next_event = EventQueue.pop_event()

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
