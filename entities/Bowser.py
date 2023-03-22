from entities.Particles import *
from defaults import scale
from classes.Animation import Animation
from classes.Spritesheet import MobSheet
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from traits.jump import JumpTrait
from traits.leftrightwalk import LeftRightWalkTrait
import random
import pygame

sprites = MobSheet()

class Bowser(EntityBase):
    def __init__(self,screen,x,y,variant,name,level,sound,difficult=False):
        super(Bowser,self).__init__(x,y,0.5)
        self.screen = screen
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x,y-scale,scale*2,scale*2)
        self.images1 = [sprites.get("bowser1",variant),sprites.get("bowser2",variant)]
        self.images2 = [sprites.get("bowser3",variant),sprites.get("bowser4",variant)]
        self.animation = Animation(self.images1,deltaTime=10)
        self.image = self.animation.image
        self.levelObj = level
        self.sound=sound
        self.direction = -1
        self.difficult=difficult
        self.name = name
        self.type = "Boss"
        self.inAir = False
        self.inJump = False
        self.breathingFire = False
        self.throwingHammers = False
        self.jumping = False
        self.walking = False
        self.traits = {"jumpTrait": JumpTrait(self,40,-8)}
        self.timer = 0
        self.coolDown = 0
        self.health = 4
        self.knockedoff = False
        self.collision = Collider(self,self.levelObj)
        self.entityCollider = EntityCollider(self)
        self.allowMovement = True
        self.checkZone()

    def update(self,shift):
        if self.levelObj.mario.rect.x > self.rect.right:
            self.image = pygame.transform.flip(self.animation.image,True,False)
            self.direction = 1
        else:
            self.image = self.animation.image
            self.direction = -1
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        self.animation.update()
        if self.jumping:
            self.onGround = False
            self.traits["jumpTrait"].jump(False)
            if not self.inJump:
                self.jumping = False
                self.coolDown = 120
        if self.breathingFire:
            if self.coolDown > 0:
                self.vel.x = 0
            elif self.coolDown == 0:
                self.breathingFire = False
                self.animation = Animation(self.images1,deltaTime=10)
                self.breatheFire()
                self.coolDown = 180
        if self.throwingHammers:
            if self.coolDown == 50:
                self.onGround = True
                self.traits["jumpTrait"].updateVerticalSpeed(-6)
                self.traits["jumpTrait"].jump(True)
                self.onGround = False
            if self.coolDown > 30:
                self.screen.blit(Hammer.hammerImage(2),((self.getPosIndexAsFloat().x+shift)*scale +8,self.rect.y-scale/2))
            if self.coolDown > 0:
                if self.coolDown % 10 == 0:
                    self.throwHammer()
            elif self.coolDown == 0:
                self.throwingHammers = False
                self.coolDown = 120
        if self.knockedoff:
            self.knockoff()
        if self.timer % 30 == 0 and not self.jumping:
            self._walk()
        if self.timer % 60 and self.coolDown == 0 and self.direction == -1:
            self._action()
        if self.coolDown > 0:
            self.coolDown -= 1
        self.timer += 1
        if self.allowMovement:
            self.applyGravity()
            if self.inAir:
                self.traits["jumpTrait"].jump(False)
            self.rect.x += self.vel.x
            self.collision.checkX()
            self.rect.y += self.vel.y
            self.collision.checkY()
            self.checkEntityCollision()

    def _walk(self):
        if self.rect.right >= self.x+scale*2 and self.walking:
            self.vel.x = -1
        elif self.rect.left <= self.x+scale*5 and self.walking:
            self.vel.x = 1
        chance = random.uniform(0,10)
        if self.rect.right >= self.x+scale:
            self._setMovement(chance,1,5)
        elif self.rect.left <= self.x+scale*3:
            self._setMovement(chance,4,6)
        else:
            self._setMovement(chance,3,6)

    def _action(self):
        chance = random.uniform(0,10)
        if self.difficult:
            if chance < 2:
                self.throwingHammers = True
                self.coolDown = 60
            elif chance < 5:
                self.jumping = True
                self.onGround = True
                self.traits["jumpTrait"].updateVerticalSpeed(-12)
                self.traits["jumpTrait"].jump(True)
            elif chance < 7:
                self.breathingFire = True
                self.animation = Animation(self.images2,deltaTime=10)
                self.coolDown = 30
        else:
            if chance < 3:
                self.jumping = True
                self.onGround = True
                self.traits["jumpTrait"].updateVerticalSpeed(-12)
                self.traits["jumpTrait"].jump(True)
            elif chance < 5:
                self.breathingFire = True
                self.animation = Animation(self.images2,deltaTime=10)
                self.coolDown = 30

    def _setMovement(self,chance,right,none):
        if chance < right:
            self.vel.x = 1
        elif chance >= none:
            self.vel.x = 0
        else:
            self.vel.x = -1

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.entityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Object":
                    ent.collide(self,collisionState)

    def collide(self,player,entityState):
        if player.type == "Player":
            if player.star:
                self.knockedoff = True
                self.levelObj.dashboard.points += 500
            else:
                player.damage()

    def damage(self):
        self.health -=1
        if self.health < 1:
            self.knockedoff = True
    
    def knockoff(self):
        self.image = self.animation.image
        self.alive = False
        self.levelObj.dashboard.points += 10000
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

    def breatheFire(self):
        startY = self.rect.y
        chance = random.choice([1,2,3])
        if chance == 1:
            startY = self.rect.y
        elif chance == 2:
            startY = self.rect.y+scale/2
        elif chance == 3:
            startY = self.rect.y+scale
        self.levelObj.entities.add(FireBreath(self.screen,self.rect.x-scale,startY,self.sound))

    def throwHammer(self):
        self.levelObj.entities.add(Hammer(self.screen,self.rect.x+8,self.rect.y-scale,2,-1))