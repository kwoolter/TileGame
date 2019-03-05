import copy
import csv
import logging
import random
from xml.dom.minidom import *
from .utils import EventQueue
from .utils import Event
from operator import itemgetter

import numpy

from .utils import is_numeric


class Resource:
    CATEGORY_DEFAULT = "default"

    def __init__(self, name: str, description: str, category: str = CATEGORY_DEFAULT, graphic: str = None):
        self.name = name
        self.description = description
        self.category = category
        self.graphic = graphic

    def __str__(self):
        _str = "{0} ({3}): {1} ({2})".format(self.name, self.description, self.category, self.graphic)
        return _str


class Creatable():

    def __init__(self, name: str, description: str, ticks_required: int = 10):
        self.name = name
        self.description = description
        self.pre_requisites = {}
        self.ticks_done = 0
        self.ticks_required = ticks_required
        self.output = {}

    def __str__(self):

        _str = "{0} ({1}) {2}% complete".format(self.name, self.description, self.percent_complete)

        if len(self.pre_requisites.keys()) > 0:
            _str += "\n\tPre-requisites:"
            for k, v in self.pre_requisites.items():
                _str += "\n\t\t- {0}:{1}".format(k, v)

        if len(self.output.keys()) > 0:
            _str += "\n\tOutputs:"
            for k, v in self.output.items():
                _str += "\n\t\t- {0}:{1}".format(k, v)

        return _str

    @property
    def is_complete(self):
        return self.ticks_done >= self.ticks_required

    @property
    def percent_complete(self):
        try:
            percent_complete = int(min(100, self.ticks_done * 100 / self.ticks_required))
        except Exception as err:
            print("{0}/{1}".format(self.ticks_done, self.ticks_required))
            print(str(err))
            percent_complete = 0

        return percent_complete

    def add_pre_requisite(self, new_resource_name: str, item_count: int = 1):

        if new_resource_name not in self.pre_requisites.keys():
            self.pre_requisites[new_resource_name] = 0

        self.pre_requisites[new_resource_name] += item_count

    def add_output(self, new_resource_name: str, item_count: int = 1):

        if new_resource_name not in self.output.keys():
            self.output[new_resource_name] = 0

        self.output[new_resource_name] += item_count

    def tick(self):
        if self.is_complete is False:
            self.ticks_done += 1
            if self.is_complete is True:
                self.do_complete()

    def do_complete(self):
        print("Construction complete for {0}!".format(self.name))


class Inventory():

    FAIL = "Inventory action fail"

    CHANGE_CREDIT = 1
    CHANGE_DEBIT = -1
    CHANGE_NO_CHANGE = 0

    def __init__(self):

        self.resources = {}

    @property
    def resource_type_count(self):
        return len(self.resources.keys())

    # Add a specified quantity of a resource to teh inventory
    def add_resource(self, new_resource: Resource, item_count: int = 1):

        if new_resource not in self.resources.keys():
            self.resources[new_resource] = 0

        self.resources[new_resource] += item_count

    # Assign inventory resources to a specified creatable
    def assign_resources(self, new_creatable : Creatable, change : int = CHANGE_NO_CHANGE):

        # If you are trying to something a resource but don't have enough resources...
        if change == Inventory.CHANGE_DEBIT and self.is_creatable(new_creatable) is False:
            print("Fail")
            EventQueue.add_event(Event(Inventory.FAIL,
                                       "Insufficient resources in inventory to create {0}!".format(new_creatable.name),
                                       Inventory.FAIL))
        else:
            for resource_name, count in new_creatable.pre_requisites.items():
                pre_req = ResourceFactory.get_resource(resource_name)
                self.add_resource(pre_req, count * change)
                print("Using {0} x {1} to create {2}".format(count,pre_req,new_creatable.name))

    # Have we got the required resources to creat a specified creatable?
    def is_creatable(self, new_creatable: Creatable):

        is_creatable = True

        for pre_req_name, count in new_creatable.pre_requisites.items():
            pre_req = ResourceFactory.get_resource(pre_req_name)
            if pre_req not in self.resources.keys():
                is_creatable = False
                break
            else:
                inv_count = self.resources[pre_req]
                if count > inv_count:
                    is_creatable = False
                    break

        return is_creatable

    def print(self):
        if len(self.resources.keys()) > 0:
            _str = "Inventory ({0} resource types)".format(self.resource_type_count)
            for k, v in self.resources.items():
                _str += "\n\t{0} ({1}) : {2}".format(k.name, k.description, v)
        else:
            _str = "No resources in your inventory!"

        print(_str)


class ResourceFactory:
    resources = {}

    def __init__(self, file_name: str):

        self.file_name = file_name

    @staticmethod
    def get_resource(name: str):
        resource = None

        if name in ResourceFactory.resources.keys():
            resource = ResourceFactory.resources[name]

        return resource

    @staticmethod
    def get_resource_copy(name: str):
        resource = None

        if name in ResourceFactory.resources.keys():
            resource = copy.deepcopy(ResourceFactory.resources[name])

        return resource

    @staticmethod
    def get_resource_types():

        return list(ResourceFactory.resources.keys())

    def load(self):

        print("\nLoading resources...")

        # Attempt to open the file
        with open(self.file_name, 'r') as object_file:

            # Load all rows in as a dictionary
            reader = csv.DictReader(object_file)

            # For each row in the file....
            for row in reader:
                name = row.get("Name")
                description = row.get("Description")
                category = row.get("Category")
                graphic = row.get("Graphic")
                if graphic == "":
                    graphic = None

                new_resource = Resource(name, description, category, graphic)
                ResourceFactory.resources[new_resource.name] = new_resource

                print(str(new_resource))

            # Close the file
            object_file.close()

        print("\n{0} resources loaded.".format(len(self.resources.keys())))


class CreatableFactoryXML(object):
    '''
    Load some creatables from an XML file and store them in a dictionary
    '''

    def __init__(self, file_name: str):

        self.file_name = file_name
        self._dom = None
        self._creatables = {}

    @property
    def count(self):
        return len(self._creatables)

    @property
    def names(self):
        return list(self._creatables.keys())

    # Load in the quest contained in the quest file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "creatables"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all quests
        creatables = self._dom.getElementsByTagName("creatable")

        # for each quest...
        for creatable in creatables:

            # Get the main tags that describe the quest
            name = self.xml_get_node_text(creatable, "name")
            desc = self.xml_get_node_text(creatable, "description")
            ticks_required = self.xml_get_node_value(creatable, "ticks_required")

            # ...and create a basic creatable object
            new_creatable = Creatable(name=name, description=desc, ticks_required=ticks_required)

            logging.info("%s.load(): Loading Creatable '%s'...", __class__, new_creatable.name)

            # Next get a list of all of the pre-requisites
            pre_requisites = creatable.getElementsByTagName("pre_requisites")[0]
            resources = pre_requisites.getElementsByTagName("resource")

            # For each pre-requisite resource...
            for resource in resources:
                # Get the basic details of the resource
                name = self.xml_get_node_text(resource, "name")
                count = self.xml_get_node_value(resource, "count")

                new_creatable.add_pre_requisite(name, count)

                logging.info("{0}.load(): adding pre-req {1} ({2})".format(__class__, name, count))

            # Next get a list of all of the outputs
            pre_requisites = creatable.getElementsByTagName("outputs")[0]
            resources = pre_requisites.getElementsByTagName("resource")

            # For each output resource...
            for resource in resources:

                # Get the basic details of the resource
                name = self.xml_get_node_text(resource, "name")
                count = self.xml_get_node_value(resource, "count")
                action = self.xml_get_node_text(resource, "action")
                if action is not None:
                    action = "replace"
                else:
                    action = "inventory"

                new_creatable.add_output(name, count)

                logging.info("{0}.load(): adding output {1} ({2})".format(__class__, name, count))

            logging.info("{0}.load(): Creatable '{1}' loaded".format(__class__, new_creatable.name))
            print(str(new_creatable))

            # Add the new creatable to the dictionary
            self._creatables[new_creatable.name] = new_creatable

        self._dom.unlink()

    # From a specified node get the data value
    def xml_get_node_text(self, node, tag_name: str):

        tag = node.getElementsByTagName(tag_name)

        # If the tag exists then get the data value
        if len(tag) > 0:
            value = tag[0].firstChild.data
        # Else use None
        else:
            value = None

        return value

    def xml_get_node_value(self, node, tag_name: str):

        value = self.xml_get_node_text(node, tag_name)

        return is_numeric(value)

    def print(self):
        for creatable in self._creatables.values():
            print(creatable)

    def get_creatable(self, name: str):

        return self._creatables[name]

    def get_creatable_copy(self, name: str):
        return copy.deepcopy(self._creatables[name])


class WorldMap:

    # Topo generation controls
    MAX_ALTITUDE = 10.0  # Highest Altitude
    MAX_SLOPE = MAX_ALTITUDE * 0.15  # Maximum slope
    MIN_SLOPE = MAX_SLOPE * -1.0  # Minimum slope is the negative of maximum slope
    MAX_SLOPE_DELTA = MAX_SLOPE * 2.0  # How much can the slope change
    MIN_ALTITUDE_CLIP_FACTOR = -1.0 # How many STDEV from the mean do we create a floor
    ALTITUDE_OFFSET = 0.0
    MIN_ALTITUDE = 0.0  # Lowest Altitude

    # Tiles used for the map hexagons
    TILE_GRASS = "Grass"
    TILE_SEA = "Sea"
    TILE_DEEP_SEA = "Deep Sea"
    TILE_SHALLOWS = "Shallows"
    TILE_SNOW = "Snow"
    TILE_ICE = "Ice"
    TILE_EARTH = "Earth"
    TILE_SAND = "Sand"
    TILE_ROCK = "Rock"
    TILE_FOREST = "Forest"
    TILE_SCRUB = "Scrub"
    TILE_BORDER = "Border"

    WATER = (TILE_SEA, TILE_DEEP_SEA, TILE_SHALLOWS)

    # Map of altitude to tile zone

    THEME_DEFAULT = "Default"
    THEME_WINTER = "Winter"
    THEME_GROWING = "Growing"
    THEME_HARVEST = "Harvesting"
    topo_zone_themes = {}

    # Define the topo zones for the Default theme
    # Numbers are in stdevs away from the mean
    topo_zones = {

        TILE_DEEP_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.6,
        TILE_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.25,
        TILE_SHALLOWS: MIN_ALTITUDE_CLIP_FACTOR * 1.0,
        TILE_SAND: MIN_ALTITUDE_CLIP_FACTOR * 0.7,
        TILE_GRASS: 0.4,
        TILE_SCRUB: 0.9,
        TILE_FOREST: 1.2,
        TILE_EARTH: 1.5,
        TILE_ROCK: 1.8,
        TILE_ICE: 2.1,
        TILE_SNOW: 2.2

    }

    topo_zone_themes[THEME_DEFAULT] = topo_zones

    # Define the topo zones for the Growing Season theme
    topo_zones = {

        TILE_DEEP_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.6,
        TILE_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.25,
        TILE_SHALLOWS: MIN_ALTITUDE_CLIP_FACTOR * 1.0,
        TILE_SAND: MIN_ALTITUDE_CLIP_FACTOR * 0.7,
        TILE_GRASS: 0.4,
        TILE_SCRUB: 0.9,
        TILE_FOREST: 1.2,
        TILE_EARTH: 1.5,
        TILE_ROCK: 1.8,
        TILE_ICE: 2.0,
        TILE_SNOW: 2.2

    }

    topo_zone_themes[THEME_GROWING] = topo_zones


    # Define the topo zones for the Harvesting season
    topo_zones = {

        TILE_DEEP_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.7,# Sea level falls
        TILE_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.45,# Sea level falls
        TILE_SHALLOWS: MIN_ALTITUDE_CLIP_FACTOR * 1.1, # Sea level falls
        TILE_SAND: MIN_ALTITUDE_CLIP_FACTOR * 0.7,
        TILE_GRASS: 0.4,
        TILE_SCRUB: 0.9,
        TILE_FOREST: 1.2,
        TILE_EARTH: 1.5,
        TILE_ROCK: 1.9, # Ice level rises
        TILE_ICE: 2.2, # Ice level rises
        TILE_SNOW: 2.3 # Snow level rises

    }

    topo_zone_themes[THEME_HARVEST] = topo_zones

    # Define the topo zones for the Winter season
    topo_zones = {

        TILE_DEEP_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.5,# Sea level rises
        TILE_SEA: MIN_ALTITUDE_CLIP_FACTOR * 1.2,# Sea level rises
        TILE_SHALLOWS: MIN_ALTITUDE_CLIP_FACTOR * 0.8,# Sea level rises
        TILE_SAND: MIN_ALTITUDE_CLIP_FACTOR * 0.7,
        TILE_GRASS: 0.4,
        TILE_SCRUB: 0.9,
        TILE_FOREST: 1.2,
        TILE_EARTH: 1.5,
        TILE_ROCK: 1.6,
        TILE_ICE: 1.75, # Ice level lowers
        TILE_SNOW: 1.98 # Snow level lowers

    }

    topo_zone_themes[THEME_WINTER] = topo_zones

    # Creations
    STRUCTURE_SMALL_HOUSE = "Small Wooden House"
    STRUCTURE_BIG_HOUSE = "Large Wooden House"
    STRUCTURE_CAVE = "Cave"
    STRUCTURE_TENT = "Tent"
    STRUCTURE_MARKET = "Market"
    STRUCTURE_FORT = "Fort"

    MATERIAL_TREE = "Trees"
    MATERIAL_TREE2 = "Mango Tree"
    MATERIAL_TREE3 = "Tree3"
    MATERIAL_PLANT1 = "Plant1"
    MATERIAL_SCRUB1 = "Scrub1"

    FOOD_STRAWBERRIES = "Strawberries"
    FOOD_CARROTS = "Carrots"

    def __init__(self, name: str, width: int = 50, height: int = 50):
        self.name = name
        self._width = width
        self._height = height
        self.map = []
        self.maps_by_theme = {}
        self.topo_model_pass2 = []

    def initialise(self):

        # Generate a random topology model for the map
        self.generate_topology()

        # Pass 1: Set tile contents based on height range
        print("Pass 1: Setting tile based on altitude...")

        for theme in WorldMap.topo_zone_themes.keys():
            self.altitude_to_tile(theme)

        print("Altitude Data: mean:{0:.3f} stdev:{1:.3f} min:{2:.3f} max:{3:.3f}".format(self.altitude_mean,
                                                          self.altitude_std,
                                                          self.altitude_min,
                                                          self.altitude_max))

        print("Pass 2: Altering altitudes...")
        #self.set_sea_level()

        print("New altitude Data: mean:{0:.3f} stdev:{1:.3f} min:{2:.3f} max:{3:.3f}".format(self.altitude_mean,
                                                          self.altitude_std,
                                                          self.altitude_min,
                                                          self.altitude_max))

    def altitude_to_tile(self, theme : str = THEME_DEFAULT):
        """Build a maps of tiles using a specified theme to determine what tile should be in each altitude range"""

        # If we don't recognise the specified theme then just use the default
        if theme not in WorldMap.topo_zone_themes.keys():
            theme = WorldMap.THEME_DEFAULT
            print("theme {0} not recognised so using default".format(theme))

        # Clear the map squares
        map = [[WorldMap.TILE_EARTH for y in range(0, self._height)] for x in range(0, self._width)]

        # Get the topo zones associated with the specified theme and create a list sorted by lowest zone first
        topo_zone = []
        for key, value in WorldMap.topo_zone_themes[theme].items():
            topo_zone.append((key,value))
        topo_zone.sort(key=itemgetter(1))

        print(theme, str(topo_zone))

        # Initialise a dictionary to keep track of how many tiles for each zone be assign
        tile_counts = {}
        tiles = list(WorldMap.topo_zone_themes[theme].keys())
        tiles.append(WorldMap.TILE_BORDER)

        for tile in tiles:
            tile_counts[tile] = 0

        # Get the mean and stdev of the all altitudes
        a_mean = self.altitude_mean
        a_std = self.altitude_std

        # loop through all points on the map
        for y in range(0, self.height):
            for x in range(0, self._width):

                # Get the altitude at the selected point on the map
                a = self.get_altitude(x, y)

                # If this is the edge of the map set to a border
                if x == 0 or x == (self.width - 1) or y == 0 or y == (self.height - 1):
                    tile = WorldMap.TILE_BORDER

                # Else use topo zones to place a point in a zone based on its altitude
                else:
                    for tile, altitude in topo_zone:
                        # If the altitude is less than the zone then use the zone and break.
                        if a < (a_mean + (a_std * altitude)):
                            break

                map[x][y] = tile

                tile_counts[tile] += 1

        # Store the tile map in the map to theme dictionary
        self.maps_by_theme[theme] = map

        print("Theme {0}:Tiles assigned (count={1}: {2})".format(theme, sum(tile_counts.values()),tile_counts))

        return

    def set_sea_level(self):

        print("Pass 2: Altering altitudes...")
        # loop through all points on the map...
        for y in range(0, self.height):
            for x in range(0, self._width):
                # For all border tiles set altitude to max
                if self.get(x,y) == WorldMap.TILE_BORDER:
                    self.set_altitude(self.altitude_max, x, y)

                # # For all altitudes less than zero (underwater) set to zero to create flat sea surface
                # elif self.get_altitude(x, y) <= 0:
                #     self.set_altitude(0, x, y)

    def generate_topology(self):
        """Build a random map of altitudes using a multi-pass algorithm"""

        # Clear the topo model
        topo_model_pass1 = [[None for y in range(0, self._height)] for x in range(0, self._width)]
        self.topo_model_pass2 = [[None for y in range(0, self._height)] for x in range(0, self._width)]

        # Create an initial topography using altitudes and random slope changes
        print("Pass 1: generate altitudes and slopes...")

        # Set the first square to be a random altitude with slopes in range
        topo_model_pass1[0][0] = (random.uniform(WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE),
                                  random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE),
                                  random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE))

        for y in range(0, self._height):
            for x in range(0, self._width):
                if y == 0:
                    north_slope = random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)
                    north_altitude = random.uniform(WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE)
                else:
                    north_altitude, tmp, north_slope = topo_model_pass1[x][y - 1]

                if x == 0:
                    west_slope = random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)
                    west_altitude = random.uniform(WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE)
                else:
                    west_altitude, west_slope, tmp = topo_model_pass1[x - 1][y]

                clip = lambda n, minn, maxn: max(min(maxn, n), minn)

                altitude = ((north_altitude + north_slope) + (west_altitude + west_slope)) / 2
                altitude = clip(altitude, WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE)

                east_slope = west_slope + ((random.random() * WorldMap.MAX_SLOPE_DELTA) - WorldMap.MAX_SLOPE_DELTA / 2)
                east_slope = clip(east_slope, WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)

                south_slope = north_slope + (
                            (random.random() * WorldMap.MAX_SLOPE_DELTA) - WorldMap.MAX_SLOPE_DELTA / 2)
                south_slope = clip(south_slope, WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)

                topo_model_pass1[x][y] = (altitude, east_slope, south_slope)


        # Perform second pass averaging based on adjacent altitudes to smooth out topography
        print("Pass 2: averaging out using neighbouring points...")

        # Iterate through each point in the map
        for y in range(0, self._height):
            for x in range(0, self._width):

                # Get the height of the current point
                local_altitude_total, es, ss = topo_model_pass1[x][y]
                local_altitude_points = 1

                # Get the list of adjacent tiles
                adjacent = HexagonMaths.adjacent(x,y)

                # Get the heights of the surrounding points
                for tx, ty in adjacent:
                    if self.is_valid_xy(tx,ty) is False:
                        pass
                    else:
                        local_altitude, es, ss = topo_model_pass1[tx][ty]
                        local_altitude_total += local_altitude
                        local_altitude_points += 1

                average_altitude = (local_altitude_total / local_altitude_points)

                # Record the average altitude in a new array
                self.topo_model_pass2[x][y] = average_altitude

        # Perform 3rd pass shifting altitude to create floors in the topology at level 0
        a = numpy.array(self.topo_model_pass2)
        avg = numpy.mean(a)
        std = numpy.std(a)
        threshold = avg + (std * WorldMap.MIN_ALTITUDE_CLIP_FACTOR)
        print("Pass 3: applying altitude floor of {0:.3}...".format(threshold))
        a[a != 0] -= threshold
        self.topo_model_pass2 = a.tolist()


    @property
    def width(self):
        return self._width
        #return len(self.maps_by_theme[WorldMap.THEME_DEFAULT])

    @property
    def height(self):
        return self._height
        #return len(self.maps_by_theme[WorldMap.THEME_DEFAULT])

    # Are the specified coordinates within the area of the map?
    def is_valid_xy(self, x: int, y: int):

        result = False

        if x >= 0 and x < self._width and y >= 0 and y < self._height:
            result = True

        return result

    # Get a map square at the specified co-ordinates
    def get(self, x: int, y: int, theme : str = THEME_DEFAULT):

        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to get tile at ({0},{1}) which is outside of the world!".format(x, y))

        if theme not in WorldMap.topo_zone_themes.keys():
            theme = WorldMap.THEME_DEFAULT

        map = self.maps_by_theme[theme]

        return map[x][y]

    def get_range(self, x: int, y: int, width: int, height: int):

        a = numpy.array(self.topo_model_pass2, order="F")
        b = a[x:x + width, y:y + height]

        return b.tolist()

    # Set a map square at the specified co-ordinates with the specified object
    def set(self, x: int, y: int, c):

        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to set tile at ({0},{1}) which is outside of the world!".format(x, y))

        self.map[x][y] = c

    # Get the altitude at the specified co-ordinates
    def get_altitude(self, x: int, y: int):
        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to get altitude at ({0},{1}) which is outside of the world!".format(x, y))
        return self.topo_model_pass2[x][y]

    # Set the altitude at the specified co-ordinates
    def set_altitude(self, new_altitude: float, x: int, y: int):
        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to set altitude at ({0},{1}) which is outside of the world!".format(x, y))
        self.topo_model_pass2[x][y] = new_altitude

    @property
    def altitude_min(self):
        return numpy.min(self.topo_model_pass2)

    @property
    def altitude_max(self):
        return numpy.max(self.topo_model_pass2)

    @property
    def altitude_mean(self):
        return numpy.mean(self.topo_model_pass2)

    @property
    def altitude_std(self):
        return numpy.std(self.topo_model_pass2)

    # Add objects to random tiles
    def add_objects(self, object_type, count: int = 20):

        for i in range(0, count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.set(x, y, object_type)


class HexagonMaths:
    """ Helper class to navigate hexagon vectors to XY vectors"""

    # Define the names of the Hexagon vectors
    NORTH = "N"
    SOUTH = "S"
    NORTH_EAST = "NE"
    SOUTH_EAST = "SE"
    NORTH_WEST = "NW"
    SOUTH_WEST = "SW"

    # Hexagon vectors to dx,dy vectors dictionaries
    # Even X values have different vectors to odd X values
    HEX_TO_XY_EVEN = {

        NORTH : (0,-1),
        SOUTH: (0,1),
        SOUTH_EAST: (1,0),
        SOUTH_WEST:(-1,0),
        NORTH_EAST:(1,-1),
        NORTH_WEST:(-1,-1)
    }

    HEX_TO_XY_ODD = {

        NORTH : (0,-1),
        SOUTH: (0,1),
        NORTH_EAST: (1,0),
        NORTH_WEST:(-1,0),
        SOUTH_EAST:(1,1),
        SOUTH_WEST:(-1,1)
    }

    @staticmethod
    def adjacent(x : int, y : int):
        """ Return list of tiles adjacent to the specified tile"""
        adjacent_tiles = []

        if x % 2 == 0:
            vectors = HexagonMaths.HEX_TO_XY_EVEN.values()
        else:
            vectors = HexagonMaths.HEX_TO_XY_ODD.values()

        for dx,dy in vectors:
            adjacent_tiles.append(((x+dx), (y+dy)))

        return adjacent_tiles

    @staticmethod
    def is_adjacent(ax : int, ay : int, bx : int, by:int):
        " Is a specified position (ax,ay) adjacent to (bx,by)?"

        return (bx,by) in HexagonMaths.adjacent(ax, ay)

    @staticmethod
    def move_hex(origin_x : int, origin_y : int, direction : str):
        """ Return a target (x,y) position based on a origin and Hexagaon direction vector """

        if direction not in HexagonMaths.HEX_TO_XY.keys():
            raise Exception("{0}.move(): {0} is not a valid direction!".format(direction))

        if origin_x % 2 == 0:
            vectors = HexagonMaths.HEX_TO_XY_EVEN
        else:
            vectors = HexagonMaths.HEX_TO_XY_ODD

        dx,dy = vectors[direction]

        return (origin_x+dx), (origin_y+dy)

    @staticmethod
    def get_direction(origin_x : int, origin_y, target_x : int, target_y):
        """ Return the hexagon vector name from an origin to a target"""

        # If the origin and the target are not adjacent then raise an exception
        if HexagonMaths.is_adjacent(origin_x, origin_y, target_x, target_y) is False:
            raise Exception("Origin and target are not adjacent!")

        if origin_x % 2 == 0:
            vectors = HexagonMaths.HEX_TO_XY_EVEN
        else:
            vectors = HexagonMaths.HEX_TO_XY_ODD

        # Calculate the xy vector to get to the target from the origin
        dx = target_x - origin_x
        dy = target_y - origin_y

        # If the xy vector in the Hex to xy dictionary...
        if (dx,dy) in vectors.values():

            # Find the xy vector in the look-up dictionary and return the Hex vector name
            pos = list(vectors.values()).index((dx, dy))
            return list(vectors.keys())[pos]

        # Else we couldn't find a bame for this vector
        else:
            return "???"
