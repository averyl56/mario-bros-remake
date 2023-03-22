from entities.Particles import *
from defaults import scale
from classes.Animation import Animation
from classes.Spritesheet import MobSheet
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from traits.jump import JumpTrait
import random
import pygame

sprites = MobSheet()

class HammerBro(EntityBase):
    def __init__(self,screen,x,y,variant,level,sound,jumpY=-1,dropY=-1,walking=True):
        super(HammerBro,self).__init__(x,y,1.25)
        self.screen = screen
        self.rect = pygame.Rect(x,y+scale/2,scale,scale*1.5)
        self.variant = variant
        self.levelObj = level
        self.sound = sound
        self.jumpY = jumpY
        self.dropY = dropY
        self.allowMovement = walking
        self.jumpable = True
        if jumpY  == -1 or dropY == -1:
            self.jumpable = False
            self.traits = {"jumpTrait": JumpTrait(self,20,-8)}
        self.highPos = False
        self.jumping = False
        self.throwHammer = False
        self.allowCollision = True
        self.inAir = False
        self.inJump = False
        self.direction = -1
        self.heading = -1
        self.type = "Mob"
        self.images1 = [sprites.get("hammerBro1",variant),sprites.get("hammerBro2",variant)]
        self.images2 = [sprites.get("hammerBro3",variant),sprites.get("hammerBro4",variant)]
        self.animation = Animation(self.images1,sprites.get("hammerBro1",variant),deltaTime=10)
        self.x0 = self.x - scale*2
        self.x1 = self.x + scale*3
        self.collider = Collider(self,self.levelObj)
        self.entityCollider = EntityCollider(self)
        self.checkZone()

    def update(self,shift):
        self.image = self.animation.image
        if self.levelObj.mario.rect.x > self.rect.x:
            self.screen.blit(pygame.transform.flip(self.image,True,False),((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
            self.heading = 1
        else:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
            self.heading = -1
        if self.rect.x < self.x0:
            self.direction = 1
        elif self.rect.right > self.x1:
            self.direction = -1
        if self.throwHammer:
            if (self.timer % 150) % 60 == 0:
                self.levelObj.entities.add(Hammer(self.screen,self.rect.x,self.rect.y,self.variant,self.heading))
                chance = random.choice([1,2])
                if chance == 1:
                    self.direction = 1
                else:
                    self.direction = -1
                self.animation.images = self.images1
                self.throwHammer = False
            else:
                self.screen.blit(Hammer.hammerImage(self.variant),((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y-scale/2))
            self.animation.update()
        elif self.jumping:
            if self.jumpable:
                if self.highPos:
                    self.animation.idle()
                    self.jump(False)
                else:
                    self.animation.idle()
                    self.drop(False)
            else:
                self.traits["jumpTrait"].jump(False)
        else:
            self.animation.update()
            if self.jumpable:
                if self.timer == 420:
                    self.jumping = True
                    if self.highPos:
                        self.drop(True)
                        self.allowCollision = False
                        self.highPos = False
                        self.direction = 0
                    else:
                        self.jump(True)
                        self.allowCollision = False
                        self.highPos = True
                        self.direction = 0
            elif self.timer == 450:
                self.onGround = True
                self.jumping = True
                self.traits["jumpTrait"].jump(True)
                self.direction = 0
            if self.timer % 150 == 0:
                self.direction = 0
                self.animation.images = self.images2
                self.throwHammer = True
        self.timer += 1
        self.applyGravity()
        if self.allowMovement:
            self.rect.x += self.direction
        if self.allowCollision:
            self.collider.checkX()
        self.rect.y += self.vel.y
        if self.allowCollision:
            if self.collider.checkY():
                self.inAir = False
                if self.jumping:
                    self.timer = 0
                    self.jumping = False
        self.checkEntityCollision()
        if self.knockedoff:
            self.knockoff()

    def jump(self,jumping):
        if jumping:
            self.vel.y = -8
            self.inAir = True
            self.inJump = True
            self.obeyGravity = False
        if self.inJump:
            if self.rect.y <= self.jumpY-scale:
                self.inJump = False
                self.obeyGravity = True
                self.allowCollision = True

    def drop(self,dropping):
        if dropping:
            self.vel.y = -4
            self.allowCollision = False
            self.inAir = True
        if self.inAir:
            if self.rect.y >= self.dropY:
                self.allowCollision = True

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.entityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Object" or ent.type == "Mob":
                    ent.collide(self,collisionState)

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if entity.star:
                self.knockedoff = True
                self.levelObj.dashboard.points += 500
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
            elif collisionState.isTop:
                self.sound.play_sfx("stomp")
                entity.rect.bottom = self.rect.top
                self.stomp()
                entity.bounce()
            else:
                entity.damage()

    def knockoff(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

    def stomp(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,100)
        self.levelObj.entities.add(points)
        entity = Stomped(self.screen,self)
        self.levelObj.entities.add(entity)