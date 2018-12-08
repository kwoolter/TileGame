import os

import pygame
from pygame.locals import *

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

                if event.type == model.Event.QUIT:
                    loop = False

                event = self.game.get_next_event()

            # Loop to process pygame events
            for event in pygame.event.get():

                # Timer events
                if event.type == USEREVENT + 1:
                    self.game.tick()
                    self.view.tick()

                    try:
                        pass

                    except Exception as err:
                        print(str(err))

                elif event.type == QUIT:
                    loop = False

                # Timer for Computer AI moves
                elif event.type == USEREVENT + 2:
                    pass

                # Key pressed events
                elif event.type == KEYUP:

                    if self.game.state == model.Game.PLAYING:

                        try:

                            if event.key == Controller.KEY_PAUSE:
                                self.game.pause()
                            elif event.key == Controller.KEY_GAME_OVER:
                                self.game.game_over()

                        except Exception as err:
                            print(str(err))

                    elif self.game.state == model.Game.PAUSED:
                        if event.key == Controller.KEY_PAUSE:
                            self.game.pause(False)
                        elif event.key == Controller.KEY_SOUND_TOGGLE:
                            self.audio.sound_toggle()
                        elif event.key == Controller.KEY_MUSIC_TOGGLE:
                            self.audio.music_toggle()

                    elif self.game.state == model.Game.READY:
                        if event.key == Controller.KEY_START:
                            self.game.start()
                        elif event.key == Controller.KEY_QUIT:
                            loop = False

                    elif self.game.state == model.Game.GAME_OVER:
                        if event.key == Controller.KEY_START:
                            self.game.initialise()
                        elif event.key == Controller.KEY_QUIT:
                            loop = False

            self.view.draw()
            self.view.update()

            FPSCLOCK.tick(50)

        self.view.end()
        self.audio.end()
        self.game.end()

