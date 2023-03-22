'''object controlling center of view on screen. positioned on player'''

from defaults import Vector2D

class Camera:
    def __init__(self, entity, level, ix=0, ax=10000):
        self.pos = Vector2D(0,0)
        self.entity = entity
        self.levelObj = level
        self.x = self.pos.x * 32
        self.y = self.pos.y * 32
        self.minX = ix
        self.maxX = ax

    def move(self):
        #move camera view
        xPosFloat = self.entity.getPosIndexAsFloat().x
        if self.minX//32 + 10 < xPosFloat < self.maxX//32 - 10:
            self.pos.x = -xPosFloat + 10
        elif self.minX//32 + 10 > xPosFloat:
            self.pos.x = -self.minX//32
        self.x = self.pos.x * 32
        self.y = self.pos.y * 32

    def setZone(self,ix,ax):
        #sets maximum distance left and right camera can move
        self.minX = ix
        self.maxX = ax