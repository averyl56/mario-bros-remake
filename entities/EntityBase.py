'''Base class for all entities'''

import pygame
from defaults import Vector2D,scale

class EntityBase(pygame.sprite.Sprite):
    def __init__(self, x, y, gravity):
        super().__init__()
        self.x = x
        self.y = y
        self.vel = Vector2D(0,0)
        self.rect = pygame.Rect(x, y, scale, scale)
        self.gravity = gravity
        self.traits = None
        self.alive = True
        self.active = True
        self.bouncing = False
        self.swimming = False
        self.timeAfterDeath = 5
        self.timer = 0
        self.type = ""
        self.zone = ""
        self.onGround = False
        self.obeyGravity = True
        self.knockedoff = False
        
    def applyGravity(self):
        #accelerate fall due to gravity
        if self.obeyGravity:
            if self.swimming:
                if self.vel.y < 2:
                    self.vel.y += self.gravity
            else:
                self.vel.y += self.gravity

    def updateTraits(self):
        #update current action of entity
        for trait in self.traits.values():
            try:
                trait.update()
            except:
                pass

    def checkZone(self):
        for zone in self.levelObj.zones:
            if zone.entInZone(self):
                if self.zone != zone:
                    self.zone = zone

    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def getPosIndex(self):
        #get position of entity on grid as int
        return Vector2D((self.rect.x // scale), (self.rect.y // scale))

    def getPosIndexAsFloat(self):
        #get position of entity on grid as float
        return Vector2D(self.rect.x / scale, self.rect.y / scale)

    def update(self,shift):
        pass
    
    def swim(self,water):
        pass