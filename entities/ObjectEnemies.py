from entities.EntityBase import EntityBase
from classes.Spritesheet import MobSheet
from defaults import scale
from classes.Animation import Animation
from classes.EntityCollider import EntityCollider
from traits.jump import JumpTrait
from entities.Particles import KnockedOff,Points,Stomped
import pygame

sprites = MobSheet()

class PiranhaPlant(EntityBase):
    def __init__(self,screen,x,y,variant,pipe,level):
        super(PiranhaPlant,self).__init__(x,y,0)
        self.screen = screen
        self.pipe = pipe
        self.rect = pygame.Rect(x,y,scale,scale*1.5)
        self.rect.centerx = self.pipe.rect.centerx
        if self.pipe.orientation == "down":
            self.direction = 1
            images = [sprites.get("plant1",variant),sprites.get("plant2",variant)]
            self.rect.bottom = self.pipe.rect.bottom
            self.index = 0
            self.index2 = 1
        elif self.pipe.orientation == "up":
            self.direction = -1
            images = [pygame.transform.flip(sprites.get("plant1",variant),False,True),pygame.transform.flip(sprites.get("plant2",variant),False,True)]
            self.rect.top = self.pipe.rect.top
            self.index = 1
            self.index2 = 0
        self.animation = Animation(images,deltaTime=10)
        self.image = self.animation.image
        self.levelObj = level
        self.type = "Mob"
        self.timer = 0
        self.freeze = False
        self.finishedLoop = False
        self.EntityCollider = EntityCollider(self)

    def update(self,shift):
        base = [self.rect.bottom,self.rect.top]
        destination = [self.pipe.rect.bottom,self.pipe.rect.top]
        if self.pipe.player is not None or self.pipe.rect.colliderect(self.pipe.levelObj.mario.rect):
            base[self.index] = destination[self.index]
            self.timer = 0
            return
        if not self.finishedLoop and base[self.index] != destination[self.index2]-self.direction:
            self.rect.y -= self.direction
        elif base[self.index] == destination[self.index2]-self.direction and not self.finishedLoop:
            if self.timer < 120:
                self.timer += 1
            elif self.timer == 120:
                self.finishedLoop = True
                self.timer = 0
        elif self.finishedLoop and base[self.index] != destination[self.index]:
            self.rect.y += self.direction
        else:
            if self.pipe.player is not None or self.pipe.rect.colliderect(self.pipe.levelObj.mario.rect):
                self.timer = 0
            else:
                if self.timer < 180:
                    self.timer += 1
                elif self.timer == 180:
                    self.finishedLoop = False
                    self.timer = 0
        self.animation.update()
        self.image = self.animation.image
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        self.checkEntityCollision()
        if self.knockedoff:
            self.levelObj.dashboard.points += 100
            points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,100)
            self.levelObj.entities.add(points)
            self.levelObj.sound.play_sfx("kick")
            self.alive = False

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Object":
                    ent.collide(self, collisionState)

    def collide(self,player,collisionState):
        if player.type == "Player":
            if player.star:
                self.knockedoff = True
                self.levelObj.dashboard.points += 400
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
            else:
                player.damage()

class BulletBill(EntityBase):
    def __init__(self,screen,x,y,variant,level,direction):
        super(BulletBill,self).__init__(x,y,0)
        self.screen = screen
        self.vel.x = 3*direction
        if direction == 1:
            self.image = pygame.transform.flip(sprites.get("bullet",variant),True,False)
        else:
            self.image = sprites.get("bullet",variant)
        self.type = "Mob"
        self.levelObj = level
        self.sound = self.levelObj.sound
        self.fireproof = True

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        self.rect.x += self.vel.x
        if self.knockedoff:
            self.knockoff()

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


class Podoboo(EntityBase):
    def __init__(self,screen,x,y,jumpHeight,level,sound):
        super(Podoboo,self).__init__(x,y,0.8)
        self.screen = screen
        self.startPos = y
        self.image = sprites.get("fire1")
        self.type = "Object"
        self.inAir = False
        self.inJump = False
        self.onGround = True
        self.obeyGravity = False
        self.levelObj = level
        self.sound = sound
        self.timer = 0
        self.jumpTrait = JumpTrait(self,jumpHeight)

    def update(self,shift):
        if self.vel.y > 0:
            self.screen.blit(pygame.transform.flip(self.image,False,True),((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        else:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        if self.knockedoff:
            self.knockoff()
        if self.timer == 0:
            self.jumpTrait.jump(self.onGround)
        self.onGround = not self.inAir
        if self.rect.y >= self.startPos and self.inAir and not self.inJump:
            self.jumpTrait.reset()
            self.onGround = True
            self.rect.y = self.startPos
            self.timer = 180
            self.vel.y = 0
            self.obeyGravity = False
        if self.timer > 0:
            self.timer -= 1
        self.applyGravity()
        self.rect.y += self.vel.y

    def knockoff(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if entity.star:
                self.knockedoff = True
                self.levelObj.dashboard.points += 500
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
            else:
                entity.damage()
