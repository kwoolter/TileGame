import os
import pygame
from pygame.locals import *
import random

import audio
import model
import view

class Controller:

    PLAYING = "Playing"

    KEY_PAUSE = K_ESCAPE
    KEY_START = K_SPACE
    KEY_GAME_OVER = K_BACKSPACE
    KEY_QUIT = K_F4
    KEY_SOUND_TOGGLE = K_F5
    KEY_MUSIC_TOGGLE = K_F6

    def __init__(self):

        self.game = model.Game("TileGame")
        self.view = view.MainFrame(self.game, 1250, 800)
        self.audio = audio.AudioManager()

        self.initialise()

    def initialise(self):

        self.game.initialise()
        self.view.initialise()
        self.audio.initialise()

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        self.audio.is_music_on = True
        self.audio.is_sound_on = True

    def run(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 1000)
        pygame.time.set_timer(USEREVENT + 2, 500)
        pygame.event.set_allowed([QUIT, KEYUP, USEREVENT])

        loop = True

        while loop is True:

            # Loop to process game events
            event = self.game.get_next_event()

            while event is not None:

                try:
                    self.game.process_event(event)
                    self.view.process_event(event)
                    self.audio.process_event(event)

                except Exception as err:
                    print(str(err))

                if event.type == model.Game.QUIT:
                    loop = False

                event = self.game.get_next_event()

            # Loop to process pygame events
            for event in pygame.event.get():

                # Process 1 second timer events
                if event.type == USEREVENT + 1:
                    self.game.tick()
                    self.view.tick()

                    try:
                        pass

                    except Exception as err:
                        print(str(err))

                # Process 0.5 second timer events
                elif event.type == USEREVENT + 2:
                    pass

                # Key pressed events
                elif event.type == KEYUP:

                    if self.game.state == model.Game.STATE_PLAYING:

                        try:

                            if event.key == K_HOME:
                                self.view.game_view.set_active()
                            elif event.key == K_RIGHT:
                                self.view.game_view.set_active(1, 0 , relative = True)
                            elif event.key == K_LEFT:
                                self.view.game_view.set_active(-1, 0 , relative = True)
                            elif event.key == K_UP:
                                self.view.game_view.set_active(0, -1 , relative = True)
                            elif event.key == K_DOWN:
                                self.view.game_view.set_active(0, 1 , relative = True)
                            elif event.key == K_INSERT:
                                self.view.game_view.set_view_origin(1, 0 , relative = True)
                            elif event.key == K_DELETE:
                                self.view.game_view.set_view_origin(-1, 0 , relative = True)
                            elif event.key == K_PAGEUP:
                                self.view.game_view.set_view_origin(0, -1 , relative = True)
                            elif event.key == K_PAGEDOWN:
                                self.view.game_view.set_view_origin(0, 1 , relative = True)
                            elif event.key == K_F1:
                                x,y = self.view.game_view.active_xy
                                self.game.add_creation_by_name(model.WorldMap.STRUCTURE_SMALL_HOUSE, x, y)
                            elif event.key == K_F2:
                                x,y = self.view.game_view.active_xy
                                self.game.add_creation_by_name(model.WorldMap.STRUCTURE_BIG_HOUSE, x, y)
                            elif event.key == K_F3:
                                items = (model.WorldMap.STRUCTURE_TENT,
                                         model.WorldMap.STRUCTURE_CAVE,
                                         model.WorldMap.STRUCTURE_FORT,
                                         model.WorldMap.STRUCTURE_MARKET)
                                x,y = self.view.game_view.active_xy
                                self.game.add_creation_by_name(random.choice(items), x, y)
                            elif event.key == K_F4:
                                items = (model.WorldMap.MATERIAL_TREE,
                                         model.WorldMap.MATERIAL_TREE2,
                                         model.WorldMap.MATERIAL_TREE3,
                                         model.WorldMap.MATERIAL_PLANT1,
                                         model.WorldMap.MATERIAL_SCRUB1)
                                x,y = self.view.game_view.active_xy
                                self.game.add_creation_by_name(random.choice(items), x, y)
                            elif event.key == K_F5:
                                items = (model.WorldMap.FOOD_STRAWBERRIES,
                                         model.WorldMap.FOOD_CARROTS)
                                x,y = self.view.game_view.active_xy
                                self.game.add_creation_by_name(random.choice(items), x, y)
                            elif event.key == K_F6:
                                x,y = self.view.game_view.active_xy
                                self.game.add_creation_by_name(model.WorldMap.MATERIAL_TREE, x, y)
                            elif event.key == Controller.KEY_PAUSE:
                                self.game.pause()
                            elif event.key == K_F12:
                                self.game.new_map()
                            elif event.key == Controller.KEY_GAME_OVER:
                                self.game.game_over()

                        except Exception as err:
                            print(str(err))

                    elif self.game.state == model.Game.STATE_PAUSED:
                        if event.key == Controller.KEY_PAUSE:
                            self.game.pause(False)
                        elif event.key == Controller.KEY_SOUND_TOGGLE:
                            self.audio.sound_toggle()
                        elif event.key == Controller.KEY_MUSIC_TOGGLE:
                            self.audio.music_toggle()
                        elif event.key == Controller.KEY_QUIT:
                            loop = False

                    elif self.game.state == model.Game.STATE_READY:
                        if event.key == Controller.KEY_START:
                            self.game.start()
                        elif event.key == Controller.KEY_QUIT:
                            loop = False

                    elif self.game.state == model.Game.STATE_GAME_OVER:
                        if event.key == Controller.KEY_START:
                            self.game.initialise()
                        elif event.key == Controller.KEY_QUIT:
                            loop = False

                # QUIT event
                elif event.type == QUIT:
                    loop = False
            try:
                self.view.draw()
                self.view.update()
            except Exception as err:
                print(str(err))

            FPSCLOCK.tick(50)

        self.view.end()
        self.audio.end()
        self.game.end()
