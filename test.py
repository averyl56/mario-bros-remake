from classes.Spritesheet import Itemsheet

sprites = Itemsheet()
image = sprites.get("movingPlatform")
image2 = sprites.get("lineVertical")

def blitPlatform(surface):
    for place in range(surface.get_height()//32+1):
        surface.blit(image2,(0,place*32))
    return surface

# Import and initialize the pygame library
import pygame
import glob
from classes.Spritesheet import Tilesheet,MobSheet
'''
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([500, 1000])
tiles = Tilesheet()
mobs = MobSheet()

surf = pygame.Surface((32,100))
surf = blitPlatform(surf)
rect = surf.get_rect()
rect.x = 100
rect.y = 100
timer = 0
speed = -5
# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))
    screen.blit(surf,(rect.x,rect.y))
    screen.blit(sprites.get("lineVertical"),(200,100))
    # Flip the display
    pygame.display.update()

# Done! Time to quit.
pygame.quit()
'''

for name in glob.glob("levels/*[1-8]"):
    print(name[len(name)-1:])
    for name2 in glob.glob(name+"/*"):
        print(name2)