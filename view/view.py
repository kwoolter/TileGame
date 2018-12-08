import logging
import os

import pygame

import model
from .graphics import *


class ImageManager:
    DEFAULT_SKIN = "default"
    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"
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

    def get_image(self, image_file_name: str, width: int = 32, height: int = 32):

        if image_file_name not in ImageManager.image_cache.keys():

            if image_file_name in self.sprite_sheets.keys():
                file_name, rect = self.sprite_sheets[image_file_name]
                filename = ImageManager.RESOURCES_DIR + file_name
                logging.info("Loading image {0} from {1} at {2}...".format(image_file_name, filename, rect))

                image_sheet = spritesheet(filename)
                original_image = image_sheet.image_at(rect)
            else:
                filename = ImageManager.RESOURCES_DIR + image_file_name
                logging.info("Loading image {0}...".format(filename))
                image_sheet = spritesheet(filename)
                original_image = image_sheet.image_at()

            try:

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

        })

        ImageManager.skins[new_skin_name] = new_skin

    def get_skin_image(self, tile_name: str, skin_name: str = DEFAULT_SKIN, tick=0, width: int = 32, height: int = 32):

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

        sheet_file_name = "fire.png"
        for i in range(0, 3):
            self.sprite_sheets["fire{0}.png".format(i)] = (sheet_file_name, (i * 32, 0, 32, 32))


class View():
    image_manager = ImageManager()

    def __init__(self, width: int = 0, height: int = 0):
        self.tick_count = 0
        self.height = height
        self.width = width
        self.surface = None

        View.image_manager.initialise()

    def initialise(self):
        pass

    def tick(self):
        self.tick_count += 1

    def process_event(self, new_event: model.Event):
        print("Default View Class event process:{0}".format(new_event))

    def draw(self):
        pass


class MainFrame(View):
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

    def initialise(self):

        super(MainFrame, self).initialise()

        self.surface = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.HWACCEL)
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

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

    def draw(self):

        self.surface.fill(Colours.DARK_GREY)

        pane_rect = self.surface.get_rect()

        self.title_bar.draw()
        self.status_bar.draw()

        x = 0
        y = 0

        self.surface.blit(self.title_bar.surface, (x, y))

        y += MainFrame.TITLE_HEIGHT

        if self.game.state == model.Game.READY:
            self.game_ready.draw()
            self.surface.blit(self.game_ready.surface, (x, y))
        elif self.game.state in (model.Game.PLAYING, model.Game.PAUSED):
            self.game_view.draw()
            self.surface.blit(self.game_view.surface, (x, y))
        elif self.game.state == model.Game.BATTLE:
            self.battle_view.draw()
            self.surface.blit(self.battle_view.surface, (x, y))
        elif self.game.state == model.Game.GAME_OVER:
            self.game_over.draw()
            self.surface.blit(self.game_over.surface, (x, y))

        x = 0
        y = pane_rect.bottom - MainFrame.STATUS_HEIGHT

        self.surface.blit(self.status_bar.surface, (x, y))

    def process_event(self, new_event: model.Event):

        # print("MainFrame event process:{0}".format(new_event))

        if self.game.state == model.Game.READY:
            self.game_ready.process_event(new_event)
        elif self.game.state == model.Game.PLAYING:
            self.game_view.process_event(new_event)
        elif self.game.state == model.Game.BATTLE:
            self.battle_view.process_event(new_event)
        elif self.game.state == model.Game.GAME_OVER:
            self.game_over.process_event(new_event)

        self.status_bar.process_event(new_event)

    def tick(self):

        if self.game.state == model.Game.READY:
            self.game_ready.tick()
        elif self.game.state == model.Game.PLAYING:
            self.game_view.tick()
        elif self.game.state == model.Game.BATTLE:
            self.battle_view.tick()
        elif self.game.state == model.Game.GAME_OVER:
            self.game_over.tick()

        self.status_bar.tick()

    def update(self):
        pygame.display.update()

    def end(self):
        pygame.quit()


class TitleBar(View):
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
            print("TitleBar.draw() - No game to View")
            return

        if self.title_image is not None:
            self.surface.blit(self.title_image, (0, 0))

        if self.game.state == model.Game.PLAYING:
            msg = "Playing"
        if self.game.state == model.Game.BATTLE:
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


class StatusBar(View):

    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK
    ICON_WIDTH = 40
    PADDING = 40
    STATUS_TEXT_FONT_SIZE = 24
    MESSAGE_TICK_DURATION = 10
    MESSAGE_TICK_LIFE = 20

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

        if self.tick_count % StatusBar.MESSAGE_TICK_DURATION == 0:

            self.current_message_number += 1
            if self.current_message_number >= len(self.status_messages):
                self.current_message_number = 0

            if len(self.status_messages) > 0:
                msg, count = self.status_messages[self.current_message_number]
                if count > 1:
                    self.status_messages[self.current_message_number] = (msg, count - 1)
                else:
                    del self.status_messages[self.current_message_number]

    def draw(self):

        self.surface.fill(StatusBar.BG_COLOUR)

        if len(self.status_messages) == 0 or self.current_message_number >= len(self.status_messages):
            msg = "{0}".format(self.game.state)
        else:
            msg, count = self.status_messages[self.current_message_number]

        pane_rect = self.surface.get_rect()

        text_rect = pygame.Rect(0, 0, pane_rect.width / 2 - 4, pane_rect.height - 4)

        self.text_box.fill(StatusBar.BG_COLOUR)

        drawText(surface=self.text_box,
                 text=msg,
                 color=StatusBar.FG_COLOUR,
                 rect=text_rect,
                 font=pygame.font.SysFont(pygame.font.get_default_font(), StatusBar.STATUS_TEXT_FONT_SIZE),
                 bkg=StatusBar.BG_COLOUR)

        self.surface.blit(self.text_box, (pane_rect.width / 4, 4))

        if self.game.state == model.Game.PLAYING:

            y = 8
            x = int(pane_rect.width * 3 / 4)

        elif self.game.state == model.Game.PAUSED:
            msg = "Esc:Resume   F5:Toggle Sound   F5:Toggle Music   F4:Quit"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

        elif self.game.state == model.Game.READY:
            msg = "SPACE:Start   F4:Quit"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)
        elif self.game.state == model.Game.GAME_OVER:
            msg = "SPACE:Continue   F4:Quit"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)


class GameReadyView(View):
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


class GameView(View):
    FG_COLOUR = Colours.GOLD
    BG_COLOUR = Colours.DARK_GREY

    def __init__(self, width: int, height: int = 500):
        super(GameView, self).__init__()

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

        msg = self.game.state

        draw_text(self.surface,
                  msg=msg,
                  x=x,
                  y=y,
                  size=40,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)


class GameOverView(View):
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


def draw_icon(surface, x, y, icon_name, count: int = None, tick: int = 0, width=32, height=32):
    image = View.image_manager.get_skin_image(tile_name=icon_name, skin_name="default", tick=tick)
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
