from classes.Animation import Animation
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from entities.EntityBase import EntityBase
from traits.leftrightwalk import LeftRightWalkTrait
from entities.Particles import KnockedOff,Points
from classes.Spritesheet import MobSheet

sprites = MobSheet()

class Goomba(EntityBase):
    def __init__(self, screen, x, y, variant, level, sound):
        super(Goomba, self).__init__(x,y,1.25)
        self.screen = screen
        images = [sprites.get("goomba1",variant),sprites.get("goomba2",variant)]
        self.animation = Animation(images)
        self.squishedImage = sprites.get("goombaD",variant)
        self.leftrightTrait = LeftRightWalkTrait(self, level, direction=-1)
        self.type = "Mob"
        self.collision = Collider(self, level)
        self.EntityCollider = EntityCollider(self)
        self.levelObj = level
        self.stomped = False
        self.sound = sound
        self.checkZone()

    def update(self, shift):
        if self.stomped:
            self.stomp(shift)
        elif self.knockedoff:
            self.knockoff()
        elif self.alive:
            self.applyGravity()
            self.drawGoomba(shift)
            self.leftrightTrait.update()
            self.checkEntityCollision()

    def drawGoomba(self, shift):
        self.screen.blit(self.animation.image, ((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        self.animation.update()

    def stomp(self, shift):
        if self.timer == 0:
            points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,100)
            self.levelObj.entities.add(points)
        if self.timer < self.timeAfterDeath:
            self.screen.blit(self.squishedImage,((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
        else:
            self.alive = False
        self.timer += 0.1
    
    def knockoff(self):
        self.image = self.animation.image
        self.alive = False
        self.levelObj.dashboard.points += 100
        entity = KnockedOff(self.screen,self,self.sound)
        self.levelObj.entities.add(entity)
    
    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Mob" or ent.type == "Object":
                    ent.collide(self, collisionState)

    def collide(self,player,collisionState):
        if not(self.stomped or self.knockedoff):
            if player.type == "Player":
                if collisionState.isTop:
                    self.sound.play_sfx("stomp")
                    player.rect.bottom = self.rect.top
                    player.bounce()
                    self.stomped = True
                    self.levelObj.dashboard.points += 100
                elif player.star:
                    self.knockedoff = True
                    self.levelObj.dashboard.points += 400
                    points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,500)
                    self.levelObj.entities.add(points)
                else:
                    player.damage()