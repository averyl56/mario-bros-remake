from entities.Particles import KnockedOff,Stomped,Points
from classes.Spritesheet import MobSheet
from classes.Animation import Animation
from classes.EntityCollider import EntityCollider
from entities.EntityBase import EntityBase
from traits.jump import JumpTrait
from classes.EntityCollider import EntityCollider
import pygame
import random
from defaults import scale

sprites = MobSheet()

class Cheep(EntityBase):
    def __init__(self,screen,x,y,variant,level):
        super(Cheep,self).__init__(x,y,0)
        self.screen = screen
        self.levelObj = level
        self.variant = variant
        images = [sprites.get("cheep1",variant),sprites.get("cheep2",variant)]
        self.animation = Animation(images,deltaTime=12)
        self.image = self.animation.image
        self.type = "Mob"
        if self.variant == 3:
            self.vel.x = -3
            self.moveTime = 4
        else:
            self.vel.x = -2
            self.moveTime = 8
        self.shifting = False
        chance = random.choice([1,2,3])
        if chance == 3:
            self.shifting = True
        if self.shifting:
            self.vel.y = 1
        self.initialHeight = self.rect.y
        self.EntityCollider = EntityCollider(self)

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        self.animation.update()
        self.image = self.animation.image
        if self.shifting:
            self.shift()
        if self.timer % 2 == 0:
            self.rect.x += self.vel.x
        if self.timer % self.moveTime == 0:
            self.rect.y += self.vel.y
        self.checkEntityCollision()
        self.timer += 1
        if self.knockedoff:
            self.knockoff()

    def shift(self):
        if self.rect.y <= self.initialHeight-scale:
            self.vel.y = 1
        elif self.rect.y >= self.initialHeight+scale:
            self.vel.y = -1

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Mob" or ent.type == "Object":
                    ent.collide(self, collisionState)

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if entity.star:
                self.levelObj.dashboard.points += 400
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
                self.knockedoff = True
            else:
                entity.damage()

    def knockoff(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.levelObj.sound,False)
        self.levelObj.entities.add(entity)

class Blooper(EntityBase):
    def __init__(self,screen,x,y,variant,level):
        super(Blooper,self).__init__(x,y,0.01)
        self.screen = screen
        self.levelObj = level
        self.rect = pygame.Rect(x,y,scale,scale*1.5)
        self.animation = Animation([sprites.get("blooper1",variant),sprites.get("blooper2",variant)],sprites.get("blooper1",variant),deltaTime=30)
        self.image = self.animation.image
        self.type = "Mob"
        self.sound = self.levelObj.sound
        self.checkZone()
        self.top = self.zone.y
        self.EntityCollider = EntityCollider(self)
        self.jumpTime = 120
        self.velYTimer = 0
        self.initialHeight = self.rect.y
        self.descending = False
        self.stomped = False
    
    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        self.image = self.animation.image
        player = self.levelObj.mario
        if (self.rect.y < self.initialHeight - scale*2 or self.rect.y < self.top+scale) and self.vel.y < 0:
            self.timer = 0
            self.vel.x = 0
            self.vel.y = 1
        if self.timer < self.jumpTime:
            self.animation.update()
            self.timer += 1
        elif self.rect.x < player.rect.x + scale*10:
            if self.descending:
                self.animation.idle()
                if self.rect.bottom > player.rect.y or self.rect.x < player.rect.x-scale*2 or self.rect.x > player.rect.x+scale*3:
                    self.descending = False
            elif self.rect.bottom < player.rect.y + scale*3 and self.vel.y >= 0 and player.rect.x-scale*2 <= self.rect.x <= player.rect.x+scale*3:
                self.descending = True
                self.vel.x = 0
                self.vel.y = 1
            elif self.vel.x == 0:
                self.animation.idle()
                chance = random.randint(1,6)
                if chance == 6:
                    self.randomBounce()
                else:
                    self.initialHeight = self.rect.y
                    self.vel.y = -3
                    if player.rect.x > self.rect.x:
                        self.vel.x = 2
                    else:
                        self.vel.x = -2
            if self.rect.y > player.rect.bottom + scale:
                self.jumpTime = 90
            else:
                self.jumpTime = 120
        else:
            self.randomBounce()
        self.rect.x += self.vel.x
        if self.velYTimer % 2 == 0:
            self.rect.y += self.vel.y
        self.checkEntityCollision()
        self.velYTimer += 1
        if self.knockedoff:
            self.knockoff()

    def randomBounce(self):
        self.initialHeight = self.rect.y
        self.vel.y = -3
        chance = random.choice([1,2])
        if chance == 1:
            self.vel.x = -2
        else:
            self.vel.x = 2

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Mob" or ent.type == "Object":
                    ent.collide(self, collisionState)
                elif ent.type == "Water":
                    self.top = ent.rect.y
                    self.swimming = True

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if entity.star:
                self.levelObj.dashboard.points += 400
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
                self.knockedoff = True
            elif entity.rect.y <= self.rect.y-4 and not self.swimming:
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

class CheepSpawner(EntityBase):
    def __init__(self,screen,x,y,width,level):
        super(CheepSpawner,self).__init__(x,y,0)
        self.screen = screen
        self.stopX = self.x+width
        self.rect = pygame.Rect(x,y,width,scale)
        self.levelObj = level

    def update(self,shift):
        player = self.levelObj.mario
        if self.rect.x < player.rect.x < self.rect.right and self.timer == 0:
            limits = self.getRange(player)
            xPos = random.randint(limits[0],limits[1])
            speed = random.randint(1,6)
            height = random.randint(200,500)
            cheep = JumpingCheep(self.screen,xPos,self.rect.y,height,self.levelObj,speed)
            self.levelObj.entities.add(cheep)
            self.timer = random.choice([30,60,60,60,120,120,180])
        if self.timer > 0:
            self.timer -= 1

    def getRange(self,player):
        x0 = player.rect.x-scale*8
        if x0 < self.rect.x:
            x0 = self.rect.x
        x1 = player.rect.x+scale*4
        if x1 > self.rect.right:
            x1 = self.rect.right
        return (x0,x1)


class JumpingCheep(EntityBase):
    def __init__(self,screen,x,y,jumpHeight,level,xVel):
        super(JumpingCheep,self).__init__(x,y,0.5)
        self.screen = screen
        self.levelObj = level
        self.animation = Animation([sprites.get("cheep1",3),sprites.get("cheep2",3)],deltaTime=12)
        self.image = self.animation.image
        self.sound = self.levelObj.sound
        self.vel.x = xVel
        self.type = "Mob"
        self.inAir = False
        self.inJump = False
        self.onGround = True
        self.stomped = False
        self.jumpTrait = JumpTrait(self,jumpHeight)
        self.EntityCollider = EntityCollider(self)
        self.jumpTrait.jump(True)

    def update(self,shift):
        self.image = self.animation.image
        self.screen.blit(pygame.transform.flip(self.image,True,False),((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        self.animation.update()
        self.jumpTrait.jump(not self.inAir)
        self.applyGravity()
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.checkEntityCollision()
        if self.knockedoff:
            self.knockoff()
        
    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Mob" or ent.type == "Object":
                    ent.collide(self, collisionState)
    
    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if entity.star:
                self.levelObj.dashboard.points += 400
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
                self.knockedoff = True
            elif collisionState.isTop or entity.rect.bottom <= self.rect.y-8:
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