'''Object to read user input in order to command mario'''

import pygame
from pygame.locals import *
import sys


class Input:
    def __init__(self, entity):
        self.entity = entity

    def checkForInput(self):
        '''checks if button is pressed for mario controls'''
        pressedKeys = pygame.key.get_pressed()

        if pressedKeys[K_RSHIFT] and not self.entity.pause:
            self.entity.sound.music_channel.pause()
            self.entity.sound.play_sfx("pause")
            self.entity.pause = True
        elif pressedKeys[K_a] and not pressedKeys[K_d] and not self.entity.lookingDown:
            self.entity.traits["goTrait"].direction = -1
        elif pressedKeys[K_d] and not pressedKeys[K_a] and not self.entity.lookingDown:
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits['goTrait'].direction = 0
        if pressedKeys[K_ESCAPE]:
            self.entity.restart = True
        if pressedKeys[K_COMMA]:
            self.entity.GODMODE(True)
        if pressedKeys[K_PERIOD]:
            self.entity.GODMODE(False)
        isJumping = pressedKeys[K_SPACE]
        self.entity.jump(isJumping)
        self.entity.throw = pressedKeys[K_LSHIFT]
        self.entity.traits['goTrait'].boost = pressedKeys[K_LSHIFT]
        self.entity.traits['jumpTrait'].boost(pressedKeys[K_LSHIFT])
        self.entity.lookingLeft = pressedKeys[K_a]
        self.entity.lookingRight = pressedKeys[K_d]
        self.entity.lookingUp = pressedKeys[K_w]
        self.entity.lookingDown = pressedKeys[K_s]

    def checkForExit(self):
        '''specifically checks if player closes'''
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()