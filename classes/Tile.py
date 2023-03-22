'''Object for unmoving ground piece'''

import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self,image, x, y, size):
        super().__init__()
        self.x = x
        self.y = y
        self.alive = True
        self.image = pygame.transform.scale(image,(size,size))
        self.rect = self.image.get_rect(topleft=(self.x,self.y))
        self.passThrough = False

    def draw(self,x,screen):
        dimensions = (x * 32, self.rect.y)
        screen.blit(self.image, dimensions)

