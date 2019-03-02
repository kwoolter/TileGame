import random

from .StatEngine import *

class KingdomStats(StatEngine):

    # Kindgom level inputs
    INPUT_TICK_COUNT = "Tick Count"
    INPUT_CURRENT_POPULATION = "Current Population"
    INPUT_CURRENT_FOOD = "Current Food"

    # Season level inputs
    INPUT_PEOPLE_DYKE = "People Dyke"
    INPUT_PEOPLE_FIELDS = "People Fields"
    INPUT_PEOPLE_VILLAGES = "People Defend Villages"
    INPUT_RICE_TO_PLANT = "Rice to Plant"

    INPUTS = (INPUT_CURRENT_FOOD, INPUT_CURRENT_POPULATION, INPUT_PEOPLE_DYKE, INPUT_PEOPLE_FIELDS,
              INPUT_PEOPLE_VILLAGES, INPUT_RICE_TO_PLANT, INPUT_TICK_COUNT
              )

    def __init__(self):
        super(KingdomStats, self).__init__("Kingdom")

    def initialise(self):
        # Add the core input stats
        for core_stat_name in KingdomStats.INPUTS:
            self.add_stat(CoreStat(core_stat_name, "INPUTS", 0))

        # Add derived game stats
        self.add_stat(CurrentYear())
        self.add_stat(CurrentSeason())


class CurrentYear(DerivedStat):
    NAME = "Current Year"

    TICKS_PER_YEAR = 15

    def __init__(self):
        super(CurrentYear, self).__init__(CurrentYear.NAME, "GAME")

        self.add_dependency(KingdomStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(KingdomStats.INPUT_TICK_COUNT)

        return ((tick_count) // CurrentYear.TICKS_PER_YEAR) + 1


class CurrentSeason(DerivedStat):
    NAME = "Current Season"

    WINTER = 1
    GROWING = 2
    HARVESTING = 3

    season_number_to_name = {
        WINTER : "Winter",
        GROWING : "Growing",
        HARVESTING : "Harvesting"

    }

    SEASONS = 3

    def __init__(self):
        super(CurrentSeason, self).__init__(CurrentSeason.NAME, "GAME")

        self.add_dependency(KingdomStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(KingdomStats.INPUT_TICK_COUNT)
        current_season = int((tick_count % CurrentYear.TICKS_PER_YEAR) // (CurrentYear.TICKS_PER_YEAR // CurrentSeason.SEASONS))
        if current_season == 0:
            current_season = 3
        return current_season