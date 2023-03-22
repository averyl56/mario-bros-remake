from defaults import scale
import pygame
from entities.EntityBase import EntityBase
from classes.Spritesheet import Itemsheet
from traits.float import FloatTrait

sprites = Itemsheet()

def blitPlatform(surface,image):
    for place in range(surface.get_width()//32):
        surface.blit(image,(place*32,0))
    surface.set_colorkey("black")
    return surface

class MovingPlatform(EntityBase):
    def __init__(self,screen,x,y,width,pos1,pos2,xSpeed,ySpeed,new=False):
        super(MovingPlatform,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,width,scale/2)
        surf = pygame.Surface((width,scale/2))
        if new:
            self.image = blitPlatform(surf,sprites.get("movingPlatform2"))
        else:
            self.image = blitPlatform(surf,sprites.get("movingPlatform"))
        self.type = "Object"
        self.floatTrait = FloatTrait(self,pos1,pos2,xSpeed,ySpeed)

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.floatTrait.update()

    def collide(self,entity,collisionState):
        if entity.type == "Boss":
            return
        entity.onGround = False
        if entity.vel.y > 0:
            entity.onGround = True
            entity.rect.bottom = self.rect.top #entity on ground
            entity.vel.y = 0
            # reset jump on bottom
            if entity.traits is not None:
                if "JumpTrait" in entity.traits:
                    entity.traits["JumpTrait"].reset()
                if "bounceTrait" in entity.traits:
                    entity.traits["bounceTrait"].reset()
        entity.rect.x += self.vel.x*3

class MovingPlatformSpawner(EntityBase):
    def __init__(self,screen,x,y,width,level,speed,interval=100,endPath=-1,new=False):
        super(MovingPlatformSpawner,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,width,scale)
        self.levelObj = level
        self.speed = speed #preferred speed is 4 or -4
        self.interval = interval
        self.endPath = endPath
        self.new = new
        self.timer = 0

    def update(self,shift):
        if self.timer % self.interval == 0:
            platform = SpawnedPlatform(self.screen,self.rect.x,self.rect.y,self.rect.width,self.levelObj,self.speed,self.endPath,self.new)
            self.levelObj.entities.add(platform)
        self.timer += 1


class SpawnedPlatform(EntityBase):
    def __init__(self,screen,x,y,width,level,speed,endPath=-1,new=False):
        super(SpawnedPlatform,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,width,scale/2)
        surf = pygame.Surface((width,scale/2))
        if new:
            self.image = blitPlatform(surf,sprites.get("movingPlatform2"))
        else:
            self.image = blitPlatform(surf,sprites.get("movingPlatform"))
        self.levelObj = level
        self.speed = speed
        self.timer = 0
        self.type = "Object"
        self.endPath = endPath
        self.checkZone()

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        if self.timer % 2 == 0:
            self.rect.y += self.speed
        self.timer += 1
        if self.endPath != -1:
            if self.speed < 0 and self.rect.y < self.endPath:
                self.alive = False
            elif self.speed > 0 and self.rect.y > self.endPath:
                self.alive = False
        else:
            if self.speed < 0 and self.rect.y < self.zone.y-32:
                self.alive = False
            elif self.speed > 0 and self.rect.y > self.zone.y1+32:
                self.alive = False

    def collide(self,entity,collisionState):
        if entity.type == "Boss":
            return
        entity.onGround = False
        if entity.vel.y > 0:
            entity.onGround = True
            entity.rect.bottom = self.rect.top #entity on ground
            entity.vel.y = 0
            # reset jump on bottom
            if entity.traits is not None:
                if "JumpTrait" in entity.traits:
                    entity.traits["JumpTrait"].reset()
                if "bounceTrait" in entity.traits:
                    entity.traits["bounceTrait"].reset()

class SkyPlatform(EntityBase):
    def __init__(self,screen,x,y,width,speed=2):
        super(SkyPlatform,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,width,scale/2)
        surf = pygame.Surface((width,scale/2))
        self.image = blitPlatform(surf,sprites.get("skyPlatform"))
        self.type = "Object"
        self.speed = speed
        self.triggered = False

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        if self.triggered:
            self.rect.x += self.speed

    def collide(self,entity,collisionState):
        if entity.type == "Boss":
            return
        entity.onGround = False
        if entity.vel.y > 0:
            entity.onGround = True
            entity.rect.bottom = self.rect.top #entity on ground
            entity.vel.y = 0
            # reset jump on bottom
            if entity.traits is not None:
                if "JumpTrait" in entity.traits:
                    entity.traits["JumpTrait"].reset()
                if "bounceTrait" in entity.traits:
                    entity.traits["bounceTrait"].reset()
            self.triggered = True
        if entity.rect.x < entity.zone.x1-scale-self.speed*3:
            entity.rect.x += self.speed*3

class DropPlatform(EntityBase):
    def __init__(self,screen,x,y,width,new=False):
        super(DropPlatform,self).__init__(x,y,0)
        self.screen = screen
        self.vel.y = 8
        self.rect = pygame.Rect(x,y,width,scale/2)
        surf = pygame.Surface((width,scale/2))
        if new:
            self.image = blitPlatform(surf,sprites.get("movingPlatform2"))
        else:
            self.image = blitPlatform(surf,sprites.get("movingPlatform"))
        self.type = "Object"

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))

    def collide(self,entity,collisionState):
        if entity.type == "Boss":
            return
        entity.onGround = False
        if entity.vel.y > 0:
            entity.onGround = True
            entity.rect.bottom = self.rect.top
            entity.vel.y = 0
            if entity.traits is not None:
                if "JumpTrait" in entity.traits:
                    entity.traits["JumpTrait"].reset()
                if "bounceTrait" in entity.traits:
                    entity.traits["bounceTrait"].reset()
            if entity.type == "Player":
                self.rect.y += self.vel.y
                entity.rect.bottom = self.rect.top

class Balance(EntityBase):
    def __init__(self,screen,x,y,width,variant,leftDown,rightDown,level,new=False):
        super(Balance,self).__init__(x,y,0.3)
        self.screen = screen
        self.leftDown = leftDown
        self.rightDown = rightDown
        self.height = self.rect.y + max(leftDown+scale,rightDown+scale)
        self.rect = pygame.Rect(x,y,width,self.height)
        self.rectLeft = pygame.Rect(self.rect.left-scale,self.rect.y+leftDown,scale*3,scale/2)
        self.rectRight = pygame.Rect(self.rect.right-scale*2,self.rect.y+rightDown,scale*3,scale/2)
        surf = pygame.Surface((scale*3,scale/2))
        if new:
            self.image = blitPlatform(surf,sprites.get("movingPlatform2"))
        else:
            self.image = blitPlatform(surf,sprites.get("movingPlatform"))
        self.lineImg = sprites.get("lineVertical",variant)
        self.line1 = self.lineImage(self.rectLeft)
        self.line2 = self.lineImage(self.rectRight)
        self.fallen = False
        self.vel.y = 0
        self.type = "Object"
        self.levelObj = level
        self.checkZone()

    def lineImage(self,platform):
        surface = pygame.Surface((scale,platform.y-self.rect.y))
        for place in range(surface.get_height()//32+1):
            surface.blit(self.lineImg,(0,place*scale))
        surface.set_colorkey("black")
        return surface

    def update(self,shift):
        if not self.fallen:
            self.line1 = self.lineImage(self.rectLeft)
            self.line2 = self.lineImage(self.rectRight)
            self.screen.blit(self.line1,((self.rect.x/scale+shift)*scale,self.rect.y))
            self.screen.blit(self.line2,(((self.rect.right-scale)/scale+shift)*scale,self.rect.y))
            self.screen.blit(self.image,((self.rectLeft.x/scale+shift)*scale,self.rectLeft.y))
            self.screen.blit(self.image,((self.rectRight.x/scale+shift)*scale,self.rectRight.y))
            self.height = self.rect.y + max(self.rectLeft.y+scale,self.rectRight.y+scale)
            self.rect = pygame.Rect(self.rect.x,self.rect.y,self.rect.width,self.height)
        elif self.rectLeft.y < self.zone.y1+scale and self.rectRight.y < self.zone.y1+scale:
            self.screen.blit(self.image,((self.rectLeft.x/scale+shift)*scale,self.rectLeft.y))
            self.screen.blit(self.image,((self.rectRight.x/scale+shift)*scale,self.rectRight.y))
            self.rectLeft.y += 12
            self.rectRight.y += 12
        else:
            if self.timer == 300:
                self.fallen = False
                self.vel.y = 0
                self.rectLeft = pygame.Rect(self.rect.left-scale,self.rect.y+self.leftDown,scale*3,scale/2)
                self.rectRight = pygame.Rect(self.rect.right-scale*2,self.rect.y+self.rightDown,scale*3,scale/2)
                self.timer = 0
            else:
                self.timer += 1

    def collide(self,entity,collisionState):
        if self.fallen:
            return
        if self.rectLeft.colliderect(entity.rect):
            entity.onGround = False
            if entity.vel.y > 0:
                entity.onGround = True
                entity.rect.bottom = self.rectLeft.top #entity on ground
                entity.vel.y = 0
                if entity.traits is not None:
                    if "JumpTrait" in entity.traits:
                        entity.traits["JumpTrait"].reset()
                    if "bounceTrait" in entity.traits:
                        entity.traits["bounceTrait"].reset()
                self.rectLeft.y += 2
                self.rectRight.y -= 2
                entity.rect.bottom = self.rectLeft.top
        elif self.rectRight.colliderect(entity.rect):
            entity.onGround = False
            if entity.vel.y > 0:
                entity.onGround = True
                entity.rect.bottom = self.rectRight.top #entity on ground
                entity.vel.y = 0
                if entity.traits is not None:
                    if "JumpTrait" in entity.traits:
                        entity.traits["JumpTrait"].reset()
                    if "bounceTrait" in entity.traits:
                        entity.traits["bounceTrait"].reset()
                self.rectRight.y += 2
                self.rectLeft.y -= 2
                entity.rect.bottom = self.rectRight.top
        if self.rectRight.y < self.rect.y or self.rectLeft.y < self.rect.y:
            self.fallen = True