import pygame
from classes.Animation import Animation
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from entities.EntityBase import EntityBase
from traits.float import FloatTrait
from traits.leftrightwalk import LeftRightWalkTrait
from traits.jump import JumpTrait
from entities.Particles import KnockedOff,Points
from defaults import scale
from classes.Spritesheet import MobSheet

sprites = MobSheet()

class Koopa(EntityBase):
    def __init__(self, screen, x, y, variant, level, sound):
        super(Koopa, self).__init__(x, y, 1.25)
        self.rect = pygame.Rect(x,y-scale/2,scale,scale*1.5)
        images = [sprites.get("koopa1",variant),sprites.get("koopa2",variant)]
        self.shellImage = sprites.get("koopaD",variant)
        self.crawlImage = sprites.get("koopaD2",variant)
        self.animation = Animation(images)
        self.image = self.animation.image
        self.screen = screen
        self.leftrightTrait = LeftRightWalkTrait(self, level, direction=-1)
        self.timer = 0
        self.timeAfterDeath = 50
        self.type = "Mob"
        self.collision = Collider(self, level)
        self.EntityCollider = EntityCollider(self)
        self.levelObj = level
        self.sound = sound
        self.variant = variant
        self.checkZone()

    def update(self, shift):
        if self.alive and self.active:
            self.updateAlive(shift)
            self.checkEntityCollision()
        elif self.alive and not self.active and not self.bouncing:
            self.sleepingInShell(shift)
            self.checkEntityCollision()
        elif self.bouncing:
            self.shellBouncing(shift)
        if self.knockedoff:
            self.knockoff()

    def drawKoopa(self, shift):
        if self.leftrightTrait.direction == -1:
            self.screen.blit(self.image, ((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        else:
            self.screen.blit(pygame.transform.flip(self.image, True, False),
                ((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        self.animation.update()
        self.image = self.animation.image

    def shellBouncing(self, shift):
        self.leftrightTrait.speed = 4
        self.applyGravity()
        self.image = self.shellImage
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        self.leftrightTrait.update()

    def sleepingInShell(self, shift):
        if self.timer < self.timeAfterDeath:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
            if self.timer == 40:
                self.image = self.crawlImage
            self.timer += 0.1
        else:
            self.leftrightTrait.speed = 1
            self.rect = pygame.Rect(self.rect.x,self.rect.y-scale/2,scale,scale*1.5)
            self.active = True
            self.bouncing = False
            self.timer = 0

    def updateAlive(self, shift):
        self.applyGravity()
        self.drawKoopa(shift)
        self.leftrightTrait.update()
        if self.variant == 3:
            self.checkEdges(shift)

    def checkEdges(self,shift):
        if self.onGround:
            if self.leftrightTrait.direction == -1:
                detector = pygame.Rect(self.rect.x-scale/2,self.rect.bottom-1,scale/2,scale/2)
            else:
                detector = pygame.Rect(self.rect.right,self.rect.bottom-1,scale/2,scale/2)
            ground = self.levelObj.ground[self.getPosIndex().y+2][self.getPosIndex().x-2:self.getPosIndex().x+2]
            gap = True
            for tile in ground:
                if tile is not None:
                    if detector.colliderect(tile.rect):
                        gap = False
            if gap:
                self.leftrightTrait.direction *= -1

    def knockoff(self):
        self.bouncing = False
        self.alive = False
        self.image = self.shellImage
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
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
            elif self.active:
                if collisionState.isTop:
                    self.sound.play_sfx("stomp")
                    self.active = False
                    self.rect = pygame.Rect(self.rect.x,self.rect.y+scale/2,scale,scale)
                    self.image = self.shellImage
                    entity.rect.bottom = self.rect.top
                    entity.bounce()
                else:
                    entity.damage()
            elif self.bouncing:
                if collisionState.isTop:
                    self.bouncing = False
                    self.vel.x = 0
                    self.timer = 0
                    self.sound.play_sfx("stomp")
                    entity.bounce()
                else:
                    entity.damage()
            elif not self.active and not self.bouncing:
                if collisionState.isTop:
                    self.sound.play_sfx("stomp")
                    entity.bounce()
                    self.timer = 0
                else:
                    if self.rect.x < entity.rect.x:
                        self.leftrightTrait.direction = -1
                        self.rect.x -= 16
                        self.sound.play_sfx("kick")
                        self.bouncing = True
                    else:
                        self.rect.x += 16
                        self.leftrightTrait.direction = 1
                        self.sound.play_sfx("kick")
                        self.bouncing = True
        elif entity.type == "Mob":
            if entity.bouncing:
                self.knockedoff = True
            if self.bouncing:
                entity.knockedoff = True


class GreenParatroopa(EntityBase):
    def __init__(self, screen, x, y, variant, level, sound):
        super(GreenParatroopa, self).__init__(x,y,0.5)
        self.screen = screen
        self.rect = pygame.Rect(x,y-scale/2,scale,scale*1.5)
        images = [sprites.get("koopaWinged1",variant),sprites.get("koopaWinged2",variant)]
        self.animation = Animation(images)
        self.image = self.animation.image
        self.inAir = False
        self.inJump = False
        self.traits = {
            "jumpTrait": JumpTrait(self,80,-8),
            "leftRightWalkTrait": LeftRightWalkTrait(self,level,direction=-1)
        }
        self.type = "Mob"
        self.variant = variant
        self.collision = Collider(self, level)
        self.EntityCollider = EntityCollider(self)
        self.levelObj = level
        self.sound = sound
        self.checkZone()

    def update(self, shift):
        self.applyGravity()
        self.drawKoopa(shift)
        self.traits["jumpTrait"].jump(self.onGround)
        self.updateTraits()
        self.checkEntityCollision()
        if self.knockedoff:
            self.knockoff()

    def drawKoopa(self, shift):
        if self.traits["leftRightWalkTrait"].direction == -1:
            self.screen.blit(self.image, ((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        else:
            self.screen.blit(pygame.transform.flip(self.image, True, False),
                ((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        self.animation.update()
        self.image = self.animation.image

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Mob" or ent.type == "Object":
                    ent.collide(self, collisionState)
                elif ent.type == "Player":
                    ent.collide(self)

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if collisionState.isTop:
                self.sound.play_sfx("stomp")
                self.alive = False
                entity.bounce()
                self.levelObj.dashboard.points += 100
                itself = Koopa(self.screen,self.rect.x,self.rect.y+32,self.variant,self.levelObj,self.sound)
                itself.onGround = False
                itself.active = True
                self.levelObj.entities.add(itself)
            elif entity.star:
                self.levelObj.dashboard.points += 400
                points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                self.levelObj.entities.add(points)
                entity = KnockedOff(self.screen,self,self.sound)
                self.levelObj.entities.add(entity)
                self.alive = False
            else:
                entity.damage()

    def knockoff(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        entity.gravity = 0.8
        self.levelObj.entities.add(entity)

class RedParatroopa(EntityBase):
    def __init__(self, screen, x, y, level, sound):
        super(RedParatroopa, self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y-scale/2,scale,scale*1.5)
        images = [sprites.get("koopaWinged1",3),sprites.get("koopaWinged2",3)]
        self.animation = Animation(images)
        self.image = self.animation.image
        self.travelDist = 192
        self.screen = screen
        point1 = (x,y)
        point2 = (x,y+self.travelDist)
        self.floatTrait = FloatTrait(self,point1,point2,xVel=0,yVel=1)
        self.type = "Mob"
        self.EntityCollider = EntityCollider(self)
        self.levelObj = level
        self.sound = sound

    def update(self, shift):
        self.drawKoopa(shift)
        self.moveKoopa()
        self.floatTrait.update()
        self.checkEntityCollision()
        if self.knockedoff:
            self.knockoff()

    def drawKoopa(self, shift):
        self.screen.blit(self.image, ((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        self.animation.update()
        self.image = self.animation.image
    
    def moveKoopa(self):
        self.rect.y += self.vel.y
        self.rect.x += self.vel.x

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
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
            elif collisionState.isTop:
                self.sound.play_sfx("stomp")
                self.alive = False
                entity.bounce()
                self.levelObj.dashboard.points += 100
                itself = Koopa(self.screen,self.rect.x,self.rect.y+32,3,self.levelObj,self.sound)
                itself.onGround = False
                itself.active = True
                self.levelObj.entities.add(itself)
            else:
                entity.damage()

    def knockoff(self):
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

class Beetle(EntityBase):
    def __init__(self, screen, x, y, variant, level, sound):
        super(Beetle, self).__init__(x, y, 1.25)
        images = [sprites.get("beetle1",variant),sprites.get("beetle2",variant)]
        self.shellImage = sprites.get("beetleD",variant)
        self.animation = Animation(images)
        self.image = self.animation.image
        self.screen = screen
        self.leftrightTrait = LeftRightWalkTrait(self, level, direction=-1)
        self.timer = 0
        self.timeAfterDeath = 50
        self.type = "Mob"
        self.collision = Collider(self, level)
        self.EntityCollider = EntityCollider(self)
        self.levelObj = level
        self.sound = sound
        self.variant = variant
        self.fireproof = True
        self.checkZone()

    def update(self, shift):
        if self.alive and self.active:
            self.updateAlive(shift)
            self.checkEntityCollision()
        elif self.alive and not self.active and not self.bouncing:
            self.sleepingInShell(shift)
            self.checkEntityCollision()
        elif self.bouncing:
            self.shellBouncing(shift)
        if self.knockedoff:
            self.knockoff()

    def drawBeetle(self, shift):
        if self.leftrightTrait.direction == -1:
            self.screen.blit(self.image, ((self.getPosIndexAsFloat().x+shift)*scale, self.rect.y))
        else:
            self.screen.blit(pygame.transform.flip(self.image, True, False),
                ((self.getPosIndexAsFloat().x+shift)*scale, self.rect.y))
        self.animation.update()
        self.image = self.animation.image

    def shellBouncing(self, shift):
        self.leftrightTrait.speed = 4
        self.applyGravity()
        self.image = self.shellImage
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        self.leftrightTrait.update()

    def sleepingInShell(self, shift):
        if self.timer < self.timeAfterDeath:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale, self.rect.y))
            self.timer += 0.1
        else:
            self.leftrightTrait.speed = 1
            self.active = True
            self.bouncing = False
            self.timer = 0

    def updateAlive(self, shift):
        self.applyGravity()
        self.drawBeetle(shift)
        self.leftrightTrait.update()

    def knockoff(self):
        self.bouncing = False
        self.alive = False
        self.image = self.shellImage
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
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
            elif self.active:
                if collisionState.isTop:
                    self.sound.play_sfx("stomp")
                    self.active = False
                    self.image = self.shellImage
                    entity.rect.bottom = self.rect.top
                    entity.bounce()
                else:
                    entity.damage()
            elif self.bouncing:
                if collisionState.isTop:
                    self.bouncing = False
                    self.vel.x = 0
                    self.timer = 0
                    self.sound.play_sfx("stomp")
                    entity.bounce()
                else:
                    entity.damage()
            elif not self.active and not self.bouncing:
                if collisionState.isTop:
                    self.sound.play_sfx("stomp")
                    entity.bounce()
                    self.timer = 0
                else:
                    if self.rect.x < entity.rect.x:
                        self.leftrightTrait.direction = -1
                        self.rect.x -= 16
                        self.sound.play_sfx("kick")
                        self.bouncing = True
                    else:
                        self.rect.x += 16
                        self.leftrightTrait.direction = 1
                        self.sound.play_sfx("kick")
                        self.bouncing = True
        elif entity.type == "Mob":
            if entity.bouncing:
                self.knockedoff = True
            if self.bouncing:
                entity.knockedoff = True