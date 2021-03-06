import logging
import os

import model
from .graphics import *


class ImageManager:
    DEFAULT_SKIN = "default"
    RESOURCES_DIR = os.path.join(os.path.dirname(__file__),"resources")
    TRANSPARENT = (1, 2, 3)

    image_cache = {}
    skins = {}
    sprite_sheets = {}
    initialised = False

    def __init__(self):
        pass

    def initialise(self):
        if ImageManager.initialised is False:
            self.load_skins()
            self.load_sprite_sheets()

    def get_image(self, image_file_name: str, width: int = 0, height: int = 0):

        if image_file_name not in ImageManager.image_cache.keys():

            if image_file_name in self.sprite_sheets.keys():
                file_name, rect = self.sprite_sheets[image_file_name]
                filename = os.path.join(ImageManager.RESOURCES_DIR, file_name)
                logging.info("Loading image {0} from {1} at {2}...".format(image_file_name, filename, rect))

                image_sheet = spritesheet(filename)
                original_image = image_sheet.image_at(rect)
            else:
                filename = os.path.join(ImageManager.RESOURCES_DIR, image_file_name)
                logging.info("Loading image {0}...".format(filename))
                image_sheet = spritesheet(filename)
                original_image = image_sheet.image_at()

            try:
                orig_width = original_image.get_width()
                orig_height = original_image.get_height()

                if height == 0 and width > 0:
                    height = int(orig_height * width / orig_width)

                if height > 0 and width == 0:
                    width = int(orig_width * height / orig_height)

                image = pygame.transform.scale(original_image, (width, height))

                ImageManager.image_cache[image_file_name] = image
                logging.info("Image {0} loaded and scaled to {1}x{2} and cached.".format(filename, width, height))
                print("Image {0} loaded and scaled to {1}x{2} and cached.".format(filename, width, height))

            except Exception as err:
                print(str(err))

        return self.image_cache[image_file_name]

    def load_skins(self):

        new_skin_name = ImageManager.DEFAULT_SKIN
        new_skin = (new_skin_name, {

            model.WorldMap.TILE_GRASS: "3dhexagonLightGreenNew.png",
            model.WorldMap.TILE_SCRUB: "3dhexagonGreenNew.png",
            model.WorldMap.TILE_FOREST: "3dhexagonDarkGreenNew.png",
            model.WorldMap.TILE_SEA: "3dhexagonBlueNew.png",
            model.WorldMap.TILE_DEEP_SEA: "3dhexagonDarkBlueNew.png",
            model.WorldMap.TILE_WHIRLPOOL: "whirlpool.png",
            model.WorldMap.TILE_ABYSS: "3dhexagonDeepBlueNew.png",
            model.WorldMap.TILE_SHALLOWS: "3dhexagonLightBlueNew.png",
            model.WorldMap.TILE_ICE: "3dhexagonGreyNew.png",
            model.WorldMap.TILE_ROCK: "3dhexagonDarkGreyNew.png",
            model.WorldMap.TILE_LAVA: "3dhexagonLava3.png",
            model.WorldMap.TILE_SNOW: "3dhexagonWhiteNew.png",
            model.WorldMap.TILE_EARTH: "3dhexagonBrownNew.png",
            model.WorldMap.TILE_SAND: "3dhexagonYellowNew.png",
            model.WorldMap.TILE_BORDER: "3dhexagonBlack.png",
            GameView.TILE_HIGHLIGHT: "3dhexagonHighlight3.png",
            GameView.TILE_HIGHLIGHT2: "3dhexagonHighlight.png",
            model.WorldMap.STRUCTURE_SMALL_HOUSE: "small_house.png",
            model.WorldMap.STRUCTURE_BIG_HOUSE: "big_house.png",
            model.WorldMap.STRUCTURE_CAVE: "Cave.png",
            model.WorldMap.STRUCTURE_TENT: "Tent.png",
            model.WorldMap.STRUCTURE_FORT: "Fort.png",
            model.WorldMap.STRUCTURE_MARKET: "market.png",
            model.WorldMap.MATERIAL_TREE: "tree.png",
            model.WorldMap.MATERIAL_TREE2: "tree1.png",
            model.WorldMap.MATERIAL_TREE3: "mango_tree.png",
            model.WorldMap.MATERIAL_SCRUB1: "scrub1.png",
            model.WorldMap.MATERIAL_PLANT1: "plant1.png",
            model.WorldMap.FOOD_STRAWBERRIES: "rice.png",
            model.WorldMap.FOOD_CARROTS: "carrots.png",
            model.WorldMap.STRUCTURE_RICE_FIELD: "rice.png",
            model.WorldMap.STRUCTURE_OBELISK: "obelisk.png",
            model.WorldMap.STRUCTURE_TENTACLE: ("tentacle0.png","tentacle1.png")


        })

        ImageManager.skins[new_skin_name] = new_skin

        # Add the skin for Winter graphics
        new_skin_name = model.CurrentSeason.season_number_to_name[model.CurrentSeason.WINTER]
        new_skin = (new_skin_name, {

            model.WorldMap.TILE_FROZEN_WATER: "3dhexagonLightGreyNew.png",
            model.WorldMap.TILE_FOREST: "3dhexagonDarkGreenSnow.png",
            model.WorldMap.TILE_EARTH: "3dhexagonBrownSnow.png",
            model.WorldMap.TILE_ROCK: "3dhexagonDarkGreySnow.png",
            model.WorldMap.TILE_SWAMP: "3dhexagonSwamp2.png",
            model.WorldMap.STRUCTURE_SMALL_HOUSE: "small_house_winter.png",
            model.WorldMap.STRUCTURE_BIG_HOUSE: "big_house_winter.png",

            # model.WorldMap.TILE_ROCK: "3dhexagonGreyNew.png",
            # model.WorldMap.TILE_EARTH: "3dhexagonGreyNew.png",
            # model.WorldMap.TILE_SHALLOWS: "3dhexagonWhiteNew.png",
        })

        ImageManager.skins[new_skin_name] = new_skin

        # Add the skin for Growing graphics
        new_skin_name = model.CurrentSeason.season_number_to_name[model.CurrentSeason.GROWING]
        new_skin = (new_skin_name, {

            # model.WorldMap.TILE_GRASS: "3dhexagonRice.png",

            model.WorldMap.STRUCTURE_RICE_FIELD: "rice2.png",

        })

        ImageManager.skins[new_skin_name] = new_skin

        # Add the skin for Harvesting graphics
        new_skin_name = model.CurrentSeason.season_number_to_name[model.CurrentSeason.HARVESTING]
        new_skin = (new_skin_name, {
            model.WorldMap.TILE_GRASS: "3dhexagonLightGreenSummer.png",
            model.WorldMap.TILE_SCRUB: "3dhexagonGreenSummer.png",
            model.WorldMap.STRUCTURE_RICE_FIELD: "rice2.png",

        })

        ImageManager.skins[new_skin_name] = new_skin

    def get_skin_image(self, tile_name: str, skin_name: str = DEFAULT_SKIN, tick=0, width: int = 0, height: int = 0):

        if skin_name not in ImageManager.skins.keys():
            raise Exception("Can't find specified skin {0}".format(skin_name))

        name, tile_map = ImageManager.skins[skin_name]

        if tile_name not in tile_map.keys():
            name, tile_map = ImageManager.skins[ImageManager.DEFAULT_SKIN]
            if tile_name not in tile_map.keys():
                raise Exception("Can't find tile name '{0}' in skin '{1}'!".format(tile_name, skin_name))

        tile_file_names = tile_map[tile_name]

        image = None

        if tile_file_names is None:
            image = None
        elif isinstance(tile_file_names, tuple):
            if tick == 0:
                tile_file_name = tile_file_names[0]
            else:
                tile_file_name = tile_file_names[tick % len(tile_file_names)]

            if tile_file_name is not None:
                image = self.get_image(image_file_name=tile_file_name, width=width, height=height)

        else:

            image = self.get_image(tile_file_names, width=width, height=height)

        return image

    def load_sprite_sheets(self):

        sheet_file_name = "tentacles_sheet.png"
        for i in range(0, 2):
            self.sprite_sheets["tentacle{0}.png".format(i)] = (sheet_file_name, (i * 128, 0, 128, 152))


class BaseView():
    image_manager = ImageManager()

    def __init__(self, width: int = 0, height: int = 0):
        self.tick_count = 0
        self.height = height
        self.width = width
        self.surface = None

        BaseView.image_manager.initialise()

    def initialise(self):
        pass

    def tick(self):
        self.tick_count += 1

    def process_event(self, new_event: model.Event):
        print("Default BaseView Class event process:{0}".format(new_event))

    def draw(self):
        pass


class MainFrame(BaseView):
    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    TITLE_HEIGHT = 80
    STATUS_HEIGHT = 40

    def __init__(self, model: model.Game, width: int = 800, height: int = 800):

        super(MainFrame, self).__init__(width, height)

        self.game = model

        self.title_bar = TitleBar(width, MainFrame.TITLE_HEIGHT)
        self.status_bar = StatusBar(width, MainFrame.STATUS_HEIGHT)

        play_area_height = height - MainFrame.STATUS_HEIGHT

        self.game_view = GameView(width, play_area_height)
        self.game_ready = GameReadyView(width, play_area_height)
        self.game_over = GameOverView(width, play_area_height)
        self.game_inventory = InventoryView(100, 300)

    def initialise(self):

        super(MainFrame, self).initialise()

        self.surface = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.HWACCEL)
        # self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption(self.game.name)
        filename = MainFrame.RESOURCES_DIR + "icon.png"

        try:
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, (32, 32))
            pygame.display.set_icon(image)
        except Exception as err:
            print(str(err))

        self.title_bar.initialise(self.game)
        self.status_bar.initialise(self.game)
        self.game_ready.initialise(self.game)
        self.game_view.initialise(self.game)
        self.game_over.initialise(self.game)

        self.game_inventory.initialise(self.game)

    def draw(self):

        self.surface.fill(Colours.DARK_GREY)

        pane_rect = self.surface.get_rect()

        self.title_bar.draw()
        self.status_bar.draw()

        x = 0
        y = 0

        self.surface.blit(self.title_bar.surface, (x, y))

        y += MainFrame.TITLE_HEIGHT

        if self.game.state == model.Game.STATE_READY:
            self.game_ready.draw()
            self.surface.blit(self.game_ready.surface, (x, y))
        elif self.game.state in (model.Game.STATE_PLAYING, model.Game.STATE_PAUSED):
            self.game_view.draw()
            self.surface.blit(self.game_view.surface, (x, y))
            self.game_inventory.draw()
            self.surface.blit(self.game_inventory.surface, (0, y))
        elif self.game.state == model.Game.STATE_BATTLE:
            self.battle_view.draw()
            self.surface.blit(self.battle_view.surface, (x, y))
        elif self.game.state == model.Game.STATE_GAME_OVER:
            self.game_over.draw()
            self.surface.blit(self.game_over.surface, (x, y))

        x = 0
        y = pane_rect.bottom - MainFrame.STATUS_HEIGHT

        self.surface.blit(self.status_bar.surface, (x, y))

    def process_event(self, new_event: model.Event):

        # print("MainFrame event process:{0}".format(new_event))

        if self.game.state == model.Game.STATE_READY:
            self.game_ready.process_event(new_event)
        elif self.game.state == model.Game.STATE_PLAYING:
            self.game_view.process_event(new_event)
        elif self.game.state == model.Game.STATE_BATTLE:
            self.battle_view.process_event(new_event)
        elif self.game.state == model.Game.STATE_GAME_OVER:
            self.game_over.process_event(new_event)

        self.status_bar.process_event(new_event)

    def tick(self):

        if self.game.state == model.Game.STATE_READY:
            self.game_ready.tick()
        elif self.game.state == model.Game.STATE_PLAYING:
            self.game_view.tick()
        elif self.game.state == model.Game.STATE_BATTLE:
            self.battle_view.tick()
        elif self.game.state == model.Game.STATE_GAME_OVER:
            self.game_over.tick()

        self.status_bar.tick()

    def update(self):
        pygame.display.update()

    def end(self):
        pygame.quit()


class TitleBar(BaseView):
    FILL_COLOUR = Colours.BLACK
    TEXT_FG_COLOUR = Colours.WHITE
    TEXT_BG_COLOUR = None

    def __init__(self, width: int, height: int):

        super(TitleBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.title = None
        self.title_image = None
        self.game = None

    def initialise(self, game: model.Game):

        super(TitleBar, self).initialise()

        self.game = game
        self.title = game.name

        try:
            filename = MainFrame.RESOURCES_DIR + "banner.jpg"
            image = pygame.image.load(filename)
            self.title_image = pygame.transform.scale(image, (self.surface.get_width(), self.surface.get_height()))
        except Exception as err:
            print(str(err))

    def draw(self):

        super(TitleBar, self).draw()

        self.surface.fill(TitleBar.FILL_COLOUR)

        if self.game is None:
            print("TitleBar.draw() - No game to BaseView")
            return

        if self.title_image is not None:
            self.surface.blit(self.title_image, (0, 0))

        if self.game.state == model.Game.STATE_PLAYING:
            msg = "Playing"
        if self.game.state == model.Game.STATE_BATTLE:
            msg = self.game.battle.battle_floor.name
        elif self.title is not None:
            msg = self.title

        pane_rect = self.surface.get_rect()
        draw_text(self.surface,
                  msg=msg,
                  x=pane_rect.centerx,
                  y=int(pane_rect.height / 2),
                  fg_colour=TitleBar.TEXT_FG_COLOUR,
                  bg_colour=TitleBar.TEXT_BG_COLOUR,
                  size=int(pane_rect.height * 0.75))


class StatusBar(BaseView):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK
    ICON_WIDTH = 40
    PADDING = 40
    STATUS_TEXT_FONT_SIZE = 24
    MESSAGE_TICK_DURATION = 3
    MESSAGE_TICK_LIFE = 2

    def __init__(self, width: int, height: int):

        super(StatusBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.text_box = pygame.Surface((width / 2, height - 4))
        self.status_messages = []
        self.game = None

    def initialise(self, game: model.Game):

        super(StatusBar, self).initialise()

        self.game = game
        self.title = game.name
        self.current_message_number = 0

    def process_event(self, new_event: model.Event):

        self.status_messages.append((new_event.description, StatusBar.MESSAGE_TICK_LIFE))

    def tick(self):

        super(StatusBar, self).tick()

        if self.game.state == model.Game.STATE_PLAYING and self.tick_count % StatusBar.MESSAGE_TICK_DURATION == 0:

            self.current_message_number += 1
            if self.current_message_number >= len(self.status_messages):
                self.current_message_number = 0

            if len(self.status_messages) > 0:
                msg, count = self.status_messages[self.current_message_number]
                if count > 1:
                    self.status_messages[self.current_message_number] = (msg, count - 1)
                else:
                    del self.status_messages[self.current_message_number]
                    print("Deleting msg {0} of {1}".format(self.current_message_number, len(self.status_messages)))

    def draw(self):

        self.surface.fill(StatusBar.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        if self.game.state == model.Game.STATE_PLAYING:

            # Check if there are status messages that we can display
            if len(self.status_messages) == 0 or self.current_message_number >= len(self.status_messages):
                msg = ""
            else:
                msg, count = self.status_messages[self.current_message_number]

            text_rect = pygame.Rect(0, 0, pane_rect.width / 2 - 4, pane_rect.height - 4)

            self.text_box.fill(StatusBar.BG_COLOUR)

            drawText(surface=self.text_box,
                     text=msg,
                     color=StatusBar.FG_COLOUR,
                     rect=text_rect,
                     font=pygame.font.SysFont(pygame.font.get_default_font(), StatusBar.STATUS_TEXT_FONT_SIZE),
                     bkg=StatusBar.BG_COLOUR)

            self.surface.blit(self.text_box, (pane_rect.width / 4, 4))

            # Display other game status info...
            y = int(pane_rect.height / 2)
            x = 10

            msg = "Year {0} ({1} season)".format(self.game.current_year,
                                                 self.game.current_season_name)

            draw_text(self.surface,
                      msg=msg,
                      x=x,
                      y=y,
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

        elif self.game.state == model.Game.STATE_PAUSED:
            msg = "Esc:Resume   F5:Toggle Sound   F6:Toggle Music   F4:Quit   F11:Load   F12:Save"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

            msg = "H:{0} L:{1}".format(self.game.map.summit, self.game.map.abyss)
            draw_text(self.surface,
                      msg=msg,
                      x=pane_rect.width*0.75,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

        elif self.game.state == model.Game.STATE_READY:
            msg = "SPACE:Start   F4:Quit"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

        elif self.game.state == model.Game.STATE_GAME_OVER:
            msg = "SPACE:Continue   F4:Quit"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)


class GameReadyView(BaseView):
    FG_COLOUR = Colours.GOLD
    BG_COLOUR = Colours.DARK_GREY

    def __init__(self, width: int, height: int = 500):
        super(GameReadyView, self).__init__()

        self.game = None
        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):
        self.game = game

    def draw(self):
        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameReadyView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        x = pane_rect.centerx
        y = 20

        msg = "R E A D Y !"

        draw_text(self.surface,
                  msg=msg,
                  x=x,
                  y=y,
                  size=40,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)


class GameView(BaseView):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.DARK_GREY

    TILE_HIGHLIGHT = "Highlight"
    TILE_HIGHLIGHT2 = "Highlight2"

    Y_SQUASH = 1.0

    TILE_ROTATE_ANGLE = 30
    TILE_IMAGE_WIDTH = 128
    CREATION_IMAGE_WIDTH = int(TILE_IMAGE_WIDTH * 1.00)
    TILE_IMAGE_HEIGHT = int(TILE_IMAGE_WIDTH * Y_SQUASH)
    TILE_ALTITUDE_FACTOR = 10
    TILE_ALTITUDE_ALPHA_BASE = 200
    TILE_ALTITUDE_ALPHA_FACTOR = 0

    def __init__(self, width: int, height: int = 500):
        super(GameView, self).__init__()

        self.game = None
        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):

        self.game = game

        # Calculate view dx and dy when moving in those directions
        self.dx = GameView.TILE_IMAGE_WIDTH * 3 / 4
        self.dy = (GameView.TILE_IMAGE_HEIGHT * GameView.Y_SQUASH / 2)

        rect = self.surface.get_rect()

        # Calculate how many tiles we can display
        self.view_tiles_width = int(rect.width / (GameView.TILE_IMAGE_WIDTH * 3 / 4)) + 1
        self.view_tiles_height = int(rect.height / (GameView.TILE_IMAGE_HEIGHT * GameView.Y_SQUASH / 2))

        # Set the view of the model to be at the centre of the map
        self.set_view_origin(int((self.game.map.width - self.view_tiles_width) / 2),
                             int((self.game.map.height - self.view_tiles_height) / 2))
        self.set_active()

    def model_to_view(self, x: int, y: int, z: int = 0, a_override: bool = False, new_a: int = 0):

        if a_override is True:
            a = new_a
        else:
            a = self.game.map.get_altitude(x, y) * GameView.TILE_ALTITUDE_FACTOR

        view_x = int((x - self.view_origin_x) * self.dx - (GameView.TILE_IMAGE_WIDTH * 3 / 4))
        view_y = int((y - self.view_origin_y) * self.dy + ((x % 2) * self.dy / 2) - (z * self.dy) - a)

        return view_x, view_y

    def set_view_origin(self, x: int = 0, y: int = 0, relative: bool = False):

        if relative is False:
            if self.game.map.is_valid_xy(x, y) is False or \
                    self.game.map.is_valid_xy(x + self.view_tiles_width, y + self.view_tiles_height) is False:
                raise Exception(
                    "Trying to set view origin at ({0},{1}) which is out of bounds of the model".format(x, y))
            self.view_origin_x = x
            self.view_origin_y = y
        else:
            if self.game.map.is_valid_xy(self.view_origin_x + x, self.view_origin_y + y) is False or \
                    self.game.map.is_valid_xy(self.view_tiles_width + self.view_origin_x + x,
                                              self.view_tiles_height + self.view_origin_y + y) is False:
                raise Exception(
                    "Trying to set view origin at ({0},{1}) which is out of bounds of the model".format(
                        self.view_origin_x + x,
                        self.view_origin_y + y))
            self.view_origin_x += x
            self.view_origin_y += y

        print("BaseView origin set to ({0},{1})".format(self.view_origin_x, self.view_origin_y))

    def set_active(self, x: int = 0, y: int = 0, relative: bool = False):
        """ Set which tile is the current active selection in the view """

        # Be default set active tile to the one in the middle of the current view
        if (x, y) == (0, 0):
            new_x = int(self.view_origin_x + (self.view_tiles_width - 1) / 2)
            new_y = int(self.view_origin_y + (self.view_tiles_height - 1) / 2)

        # If setting to absolute (non-relative to current active...
        elif relative is False:
            new_x = x
            new_y = y

        # Else set relative to current active
        else:
            new_x = self.active_x + x
            new_y = self.active_y + y

        # If the new active selection is outside of the map then throw exception
        if self.game.map.is_valid_xy(new_x, new_y) is False:
            raise Exception(
                "Trying to set active tile at ({0},{1}) which is out of bounds of the view".format(new_x, new_y))

        # all good so change current active selection to the new one
        self.active_y = new_y
        self.active_x = new_x
        print("Set active tile to ({0},{1})".format(self.active_x, self.active_y))

        # If the current active selection moves to the edges of the current view then
        # Move the view to keep inline with the active selection
        if self.active_x <= self.view_origin_x:
            self.set_view_origin(-1, 0, relative=True)
        elif self.active_x > (self.view_origin_x + self.view_tiles_width - 1):
            self.set_view_origin(1, 0, relative=True)

        if self.active_y < self.view_origin_y:
            self.set_view_origin(0, -1, relative=True)
        elif self.active_y > (self.view_origin_y + self.view_tiles_height - 2):
            self.set_view_origin(0, 1, relative=True)

    @property
    def active_xy(self):
        return (self.active_x, self.active_y)

    def draw(self):
        """" Draw the game view """

        if self.game is None:
            raise ("No Game to view!")

        skin_name = self.game.current_season_name

        self.surface.fill(GameReadyView.BG_COLOUR)

        x = GameView.TILE_IMAGE_WIDTH * 0.25 * 0
        y = int(GameView.TILE_IMAGE_HEIGHT * 1.5)

        # Load in the image to highlight the current active tile
        highlight_image = BaseView.image_manager.get_skin_image(GameView.TILE_HIGHLIGHT,
                                                                width=GameView.TILE_IMAGE_WIDTH,
                                                                height=int(
                                                                    GameView.TILE_IMAGE_HEIGHT * GameView.Y_SQUASH),
                                                                tick=self.tick_count)

        highlight_image.set_alpha(150)

        # Load in the image to highlight the current active tile
        highlight2_image = BaseView.image_manager.get_skin_image(GameView.TILE_HIGHLIGHT2,
                                                                 width=GameView.TILE_IMAGE_WIDTH,
                                                                 height=int(
                                                                     GameView.TILE_IMAGE_HEIGHT * GameView.Y_SQUASH),
                                                                 tick=self.tick_count)

        highlight2_image.set_alpha(150)

        # Loop through the number of row that the view is oging to display
        for tile_y in range(0, self.view_tiles_height):

            # Add the y origin to where we are going to start drawing the model tiles from
            map_y = tile_y + self.view_origin_y

            # Print the two offset x rows
            for i in range(2):

                # print a row of alternate x tiles
                for tile_x in range(0, self.view_tiles_width, 2):

                    # Always draw the tile odd tile first
                    xx = self.view_origin_x % 2 + i

                    # add the x origin to where we are going to start drawing the model from
                    map_x = tile_x + self.view_origin_x + xx

                    # Get the specified tile from the model
                    tile = self.game.map.get(map_x, map_y, theme=skin_name)

                    # Get the image associated with that tile name
                    image = BaseView.image_manager.get_skin_image(tile,
                                                                  width=GameView.TILE_IMAGE_WIDTH,
                                                                  height=int(
                                                                      GameView.TILE_IMAGE_HEIGHT * GameView.Y_SQUASH),
                                                                  tick=self.tick_count,
                                                                  skin_name=skin_name)

                    # Convert the model coords to view coords and blit the tile image at that location
                    view_x, view_y = self.model_to_view(map_x, map_y, a_override=tile in (model.WorldMap.WATER))
                    self.surface.blit(image, (view_x + x, view_y + y - image.get_height()))

                    # If the specified tile is the currently selected active tile...
                    if (map_x, map_y) == (self.active_x, self.active_y):

                        # Draw the tile highlight image over it
                        self.surface.blit(highlight_image, (view_x + x, view_y + y - highlight_image.get_height()))

                        # Draw text in the middle of the tile surface with the tile name
                        tx = view_x + x + int(GameView.TILE_IMAGE_WIDTH / 2)
                        ty = view_y + y - + int(GameView.TILE_IMAGE_HEIGHT * 3 / 4 * GameView.Y_SQUASH)

                        text = "  {0}  ".format(tile)

                        draw_text(self.surface,
                                  msg=text,
                                  x=tx,
                                  y=ty,
                                  size=16,
                                  fg_colour=GameView.FG_COLOUR,
                                  bg_colour=GameView.BG_COLOUR,
                                  centre=True)

                    # If the specified tile is adjacent to the current active tile
                    elif model.HexagonMaths.is_adjacent(self.active_x, self.active_y, map_x, map_y):

                        # Draw the tile highlight image over it
                        self.surface.blit(highlight2_image, (view_x + x, view_y + y - highlight_image.get_height()))

                        # Draw text in the middle of the tile surface with the tile name
                        tx = view_x + x + int(GameView.TILE_IMAGE_WIDTH / 2)
                        ty = view_y + y - + int(GameView.TILE_IMAGE_HEIGHT * 3 / 4 * GameView.Y_SQUASH)

                        text = " " + model.HexagonMaths.get_direction(self.active_x, self.active_y, map_x, map_y) + " "

                        draw_text(self.surface,
                                  msg=text,
                                  x=tx,
                                  y=ty,
                                  size=16,
                                  fg_colour=GameView.FG_COLOUR,
                                  bg_colour=GameView.BG_COLOUR,
                                  centre=True)

                    # See if a creation has been placed at this location...
                    creation = self.game.get_creation(map_x, map_y)
                    if creation is not None:

                        # Get the image for the creation based on its name
                        image = BaseView.image_manager.get_skin_image(creation.name,
                                                                      width=GameView.CREATION_IMAGE_WIDTH,
                                                                      tick=self.tick_count,
                                                                      skin_name=skin_name)

                        # If it is not yet complete then change the image transaprecny based on % complete
                        if creation.is_complete is False:
                            image.set_alpha(150 + creation.percent_complete)
                        else:
                            image.set_alpha(255)

                        # Convert the model coords to view coords and blit the tile image at that location
                        view_x, view_y = self.model_to_view(map_x, map_y, 1)
                        self.surface.blit(image, (
                            view_x + int((GameView.TILE_IMAGE_WIDTH - GameView.CREATION_IMAGE_WIDTH) / 2),
                            view_y + y - image.get_height()))

                        text = ""
                        if creation.is_complete is False:
                            text = "{0} ({1}%)".format(creation.name, creation.percent_complete)

                        elif (map_x, map_y) == (self.active_x, self.active_y):
                            text = "{0}".format(creation.description)

                        if text != "":
                            tx = view_x + x + int(GameView.TILE_IMAGE_WIDTH / 2)
                            ty = view_y + y - image.get_height()

                            draw_text(self.surface,
                                      msg=text,
                                      x=tx,
                                      y=ty,
                                      size=12,
                                      fg_colour=GameView.FG_COLOUR,
                                      bg_colour=GameView.BG_COLOUR,
                                      centre=True)


class GameOverView(BaseView):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.DARK_GREY
    SCORE_TEXT_SIZE = 22

    def __init__(self, width: int, height: int = 500):
        super(GameOverView, self).__init__()

        self.game = None
        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):
        self.game = game

    def draw(self):
        self.surface.fill(GameOverView.BG_COLOUR)

        if self.game is None:
            raise ("No Game to view!")

        pane_rect = self.surface.get_rect()

        y = 20
        x = pane_rect.centerx

        text = "G A M E    O V E R"
        fg_colour = GameOverView.FG_COLOUR

        draw_text(self.surface,
                  msg=text,
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=fg_colour,
                  bg_colour=GameOverView.BG_COLOUR)


class InventoryView(BaseView):
    FILL_COLOUR = Colours.DARK_GREY
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK
    ITEM_TEXT_FONT_SIZE = 16

    def __init__(self, width: int = 100, height: int = 200):
        super(InventoryView, self).__init__(width, height)

        self.game = None

        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):
        self.game = game

    def draw(self):

        super(InventoryView, self).draw()

        self.surface.fill(InventoryView.FILL_COLOUR)

        msg = "Inventory"
        pane_rect = self.surface.get_rect()
        x = pane_rect.centerx
        y = 20

        draw_text(self.surface,
                  msg=msg,
                  x=x,
                  y=y,
                  fg_colour=InventoryView.FG_COLOUR,
                  bg_colour=InventoryView.BG_COLOUR,
                  size=24)

        if self.game is None:
            print("InventoryView.draw() - No game to BaseView")
            return

        inv = self.game.inventory

        for i in inv.resources.keys():

            if i.category == "Material":
                item_count = inv.resources[i]
                y += 16
                msg = "{0} : {1}".format(i.name, item_count)
                draw_text(self.surface,
                          msg=msg,
                          x=x,
                          y=y,
                          fg_colour=InventoryView.FG_COLOUR,
                          bg_colour=InventoryView.BG_COLOUR,
                          size=16)


def draw_icon(surface, x, y, icon_name, count: int = None, tick: int = 0, width=32, height=32):
    image = BaseView.image_manager.get_skin_image(tile_name=icon_name, skin_name="default", tick=tick)
    image = pygame.transform.scale(image, (width, height))
    iconpos = image.get_rect()
    iconpos.left = x
    iconpos.top = y
    surface.blit(image, iconpos)

    if count is not None:
        small_font = pygame.font.Font(None, 20)
        icon_count = small_font.render("{0:^3}".format(count), 1, Colours.BLACK, Colours.WHITE)
        count_pos = icon_count.get_rect()
        count_pos.bottom = iconpos.bottom
        count_pos.right = iconpos.right
        surface.blit(icon_count, count_pos)
