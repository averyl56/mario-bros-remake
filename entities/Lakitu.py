from classes.Animation import Animation
from classes.EntityCollider import EntityCollider
from entities.EntityBase import EntityBase
from traits.leftrightwalk import LeftRightWalkTrait
from traits.jump import JumpTrait
from entities.Particles import KnockedOff,Stomped,Points
from classes.Spritesheet import MobSheet
from defaults import scale
import pygame

sprites = MobSheet()

class Lakitu(EntityBase):
    def __init__(self,screen,x,y,variant,level,sound):
        super(Lakitu,self).__init__(x,y,0)
        self.screen = screen
        self.levelObj = level
        self.sound = sound
        self.rect = pygame.Rect(x,y,scale,scale*1.5)
        self.activeImg = sprites.get("lakitu1",variant)
        self.duckImg = sprites.get("lakitu2",variant)
        self.image = self.activeImg
        self.type = "Mob"
        self.vel.x = -2
        self.active = False
        self.entityCollider = EntityCollider(self)

    def update(self,shift):
        player = self.levelObj.mario
        dontMove = False
        for ent in self.levelObj.entities:
            if isinstance(ent,Lakitu) and self.rect.x != ent.rect.x:
                if ent.active:
                    dontMove = True
        if not player.allowMovement:
            dontMove = True
        if dontMove:
            self.active = False
            return
        else:
            self.active = True
        if self.vel.x < 0:
            self.screen.blit(pygame.transform.flip(self.image,True,False),((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        else:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        if self.rect.x > player.rect.x + scale*5:
            if player.vel.x < -4:
                self.vel.x = -5
            else:
                self.vel.x = -2
        elif player.vel.x > 4:
            if self.rect.x < player.rect.x+scale*3:
                self.vel.x = 6
            else:
                self.vel.x = player.vel.x
        elif self.rect.x > player.rect.x + scale*5:
            self.vel.x = -2
        elif self.rect.x < player.rect.x - scale*4:
            self.vel.x = 4
        else:
            if self.rect.x > player.rect.x + scale*4:
                self.vel.x = -1
            elif self.rect.x < player.rect.x - scale*3:
                self.vel.x = 1
        if self.timer == 240:
            self.image = self.duckImg
        elif self.timer == 300:
            self.image = self.activeImg
            if self.rect.x < player.rect.x:
                direction = 1
            else:
                direction = -1
            self.levelObj.entities.add(Spiney(self.screen,self.rect.centerx,self.rect.y,self.levelObj,direction))
            self.timer = 0
        self.timer += 1
        self.rect.x += self.vel.x
        self.checkEntityCollision()
        if self.knockedoff:
            self.knockoff()

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.entityCollider.check(ent)
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
            elif collisionState.isTop:
                self.sound.play_sfx("stomp")
                entity.rect.bottom = self.rect.top
                self.stomp()
                entity.bounce()
            else:
                entity.damage()

    def stomp(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,100)
        self.levelObj.entities.add(points)
        self.image = self.duckImg
        entity = Stomped(self.screen,self)
        self.levelObj.entities.add(entity)

    def knockoff(self):
        self.image = self.animation.image
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

class Spiney(EntityBase):
    def __init__(self,screen,x,y,level,thrownDir=0):
        super(Spiney,self).__init__(x,y,0.8)
        self.screen = screen
        self.levelObj = level
        self.sound = self.levelObj.sound
        self.type = "Mob"
        self.direction = -1
        self.inAir = False
        self.inJump = False
        if thrownDir != 0:
            self.active = False
            self.animation = Animation([sprites.get("spineyBall1"),sprites.get("spineyBall2")],deltaTime=10)
            self.direction = thrownDir
        else:
            self.active = True
            self.animation = Animation([sprites.get("spiney1"),sprites.get("spiney2")],deltaTime=10)
        self.image = self.animation.image
        self.walkTrait = LeftRightWalkTrait(self,self.levelObj,direction=-self.direction)
        self.jumpTrait = JumpTrait(self,10)
        self.jumpTrait.verticalSpeed = -5
        self.entityCollider = EntityCollider(self)
        self.checkZone()
        if not self.active:
            self.vel.x = self.direction*2
            self.onGround = True
            self.jumpTrait.jump(True)

    def update(self,shift):
        self.image = self.animation.image
        if not self.active:
            self.jumpTrait.jump(False)
            if self.walkTrait.collDetection.checkY():
                self.jumpTrait.reset()
                self.animation = Animation([sprites.get("spiney1"),sprites.get("spiney2")],deltaTime=10)
                self.active = True
                self.image = self.animation.image
                self.vel.x = 0
                self.vel.y = 0
            else:
                self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
                self.animation.update()
                self.applyGravity()
                self.rect.x += self.vel.x
                self.rect.y += self.vel.y
        else:
            if self.walkTrait.direction == 1:
                self.screen.blit(pygame.transform.flip(self.image,True,False),((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
            else:
                self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
            self.applyGravity()
            self.walkTrait.update()
            self.checkEntityCollision()
            if self.knockedoff:
                self.knockoff()

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.entityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Mob" or ent.type == "Object":
                    ent.collide(self, collisionState)

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if entity.star:
                self.knockedoff = True
                self.levelObj.dashboard.points += 400
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
            else:
                entity.damage()

    def knockoff(self):
        self.image = self.animation.image
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)
