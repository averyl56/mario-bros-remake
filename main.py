'''Main file for running the game'''

import pygame
import sys
from classes.Dashboard import Dashboard
from classes.Level import Level
from classes.Menu import Menu
from classes.Sound import Sound
from pygame.locals import K_RETURN
from defaults import windowSizeX,windowSizeY

windowSize = windowSizeX,windowSizeY
levelSelect = False

def main():
    global levelSelect
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    screen = pygame.display.set_mode(windowSize)
    max_frame_rate = 60
    dashboard = Dashboard("./textures/font.png", 8, screen)
    sound = Sound()
    level = Level(screen, sound, dashboard)
    menu = Menu(screen, dashboard, level, sound)
 
    if levelSelect:
        menu.chooseLevel()
    while not menu.start: #main menu
        menu.update()
    levelSelect = not level.campaign
    clock = pygame.time.Clock()

    #start level
    while not level.restart(): #while no game over or quit
        pygame.display.set_caption("Super Mario running with {:d} FPS".format(int(clock.get_fps())))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if level.paused():
            level.pause()
            if level.restart():
                break
        else:
            level.drawLevel()
            dashboard.update()
        pygame.display.update()
        clock.tick(max_frame_rate)
    return 'restart'

if __name__ == "__main__":
    exitmessage = 'restart'
    while exitmessage == 'restart':
        exitmessage = main()