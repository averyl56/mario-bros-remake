from defaults import scale
import pygame
from entities.EntityBase import EntityBase
from classes.Spritesheet import Itemsheet
from classes.Animation import Animation
from traits.jump import JumpTrait
from classes.Collider import Collider

sprites = Itemsheet()

class CoinParticle(EntityBase):
    def __init__(self, screen, x, y, sound, dashboard):
        super(CoinParticle, self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y,scale,scale)
        self.y = y
        self.screen = screen
        self.fontSize = 8
        self.sound = sound
        self.dashboard = dashboard
        images = [sprites.get("coinParticle1"),sprites.get("coinParticle2"),sprites.get("coinParticle3"),sprites.get("coinParticle4")]
        self.animation = Animation(images,deltaTime=10)
        self.sound_played = False

    def update(self, shift):
        if not self.sound_played:
            self.sound_played = True
            self.sound.play_effect("coin")
        self.animation.update()
        if self.animation.timer < 45:
            if self.animation.timer < 15:
                self.vel.y -= 0.5
                self.rect.y += self.vel.y
            elif self.animation.timer < 45:
                self.vel.y += 0.5
                self.rect.y += self.vel.y
            self.screen.blit(self.animation.image, ((self.getPosIndexAsFloat().x + shift)*32, self.rect.y))
        elif self.animation.timer < 80:
            self.vel.y = -0.75
            self.rect.y += self.vel.y
            self.dashboard.drawText("100", (self.getPosIndexAsFloat().x + shift)*32 +3, self.rect.y, 8)
        else:
            self.alive = False

class BrickParticles(EntityBase):
    def __init__(self,screen,x,y,variant):
        super(BrickParticles,self).__init__(x,y,0)
        self.screen = screen
        self.time = 0
        piece1 = Piece(self.screen,x,y,-1,120,variant)
        piece2 = Piece(self.screen,x,y+16,-1,40,variant)
        piece3 = Piece(self.screen,x+16,y,1,120,variant)
        piece4 = Piece(self.screen,x+16,y+16,1,40,variant)
        self.pieces = [piece1,piece2,piece3,piece4]
        self.time = 0

    def update(self,shift):
        if self.time == 0:
            for piece in self.pieces:
                piece.jumpTrait.jump(True)
        if self.time < 180:
            for piece in self.pieces:
                piece.update(shift,self.time)
        else:
            for piece in self.pieces:
                piece.alive = False
            self.alive = False

class Piece(EntityBase):
    def __init__(self,screen,x,y,direction,jump,variant):
        super(Piece,self).__init__(x,y,0.8)
        self.rect = pygame.Rect(x,y,16,16)
        self.screen = screen
        self.image = sprites.get("brickParticle",variant)
        self.direction = direction
        if direction == -1:
            self.image = pygame.transform.flip(self.image,True,False)
        self.inAir = False
        self.inJump = False
        self.onGround = True
        self.jumpTrait = JumpTrait(self,jump)

    def update(self,shift,time):
        if self.alive:
            self.applyGravity()
            self.draw(shift)
            self.move()
            if time % 15 == 0:
                self.image = pygame.transform.flip(self.image,False,True)
            self.onGround = False

    def move(self):
        self.rect.y += self.vel.y
        self.rect.x += self.direction

    def draw(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))

class KnockedOff(EntityBase):
    def __init__(self,screen,entity,sound,direction=-1):
        super(KnockedOff,self).__init__(entity.rect.x,entity.rect.y,entity.gravity)
        self.screen = screen
        if entity.gravity == 0:
            self.gravity = 1.25
        self.rect = entity.rect
        self.image = entity.image
        self.sound = sound
        self.direction = direction
        self.inAir = False
        self.inJump = False
        self.onGround = True
        self.jumpTrait = JumpTrait(self,60,-6)

    def update(self,shift):
        if self.timer == 0:
            self.sound.play_sfx("kick")
            self.jumpTrait.jump(True)
        if self.timer < 180:
            self.applyGravity()
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
            self.rect.x -= 1
            self.rect.y += self.vel.y
            self.jumpTrait.jump(False)
            self.onGround = False
            if self.timer == 10:
                self.image = pygame.transform.flip(self.image,False,True)
        else:
            self.alive = False
        self.timer += 1

class Stomped(EntityBase):
    def __init__(self,screen,entity):
        super(Stomped,self).__init__(entity.rect.x,entity.rect.y,entity.gravity)
        self.screen = screen
        if entity.gravity == 0:
            self.gravity = 1.25
        self.rect = entity.rect
        self.image = entity.image
        self.timer = 0

    def update(self,shift):
        if self.timer < 180:
            self.applyGravity()
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32, self.rect.y))
            self.rect.y += self.vel.y
        else:
            self.alive = False
        self.timer += 1

class TextBox(EntityBase):
    def __init__(self,screen,dashboard,x,y,text,visible):
        super(TextBox,self).__init__(x,y,0)
        self.screen = screen
        self.text = text
        self.dashboard = dashboard
        self.visible = visible

    def update(self,shift):
        if self.visible:
            self.dashboard.drawText(self.text,(self.getPosIndexAsFloat().x+shift)*32,self.rect.y,scale/2)

class Points(EntityBase):
    def __init__(self,dashboard,x,y,points):
        super(Points,self).__init__(x,y,0)
        self.dashboard = dashboard
        self.points = str(points)

    def update(self,shift):
        if self.timer < self.timeAfterDeath:
            self.dashboard.drawText(self.points, (self.getPosIndexAsFloat().x+shift)*scale, self.rect.y-self.timer*5, 8)
        else:
            self.alive = False
        self.timer += 0.1

class FireBreath(EntityBase):
    def __init__(self,screen,x,y,sound):
        super(FireBreath,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,scale*1.5,scale/2)
        images = [sprites.get("flameBreath1"),sprites.get("flameBreath2")]
        self.animation = Animation(images)
        self.image = self.animation.image
        self.type = "Object"
        self.timer = 0
        self.sound = sound

    def update(self,shift):
        self.image = self.animation.image
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        self.animation.update()
        if self.timer < 480:
            if self.timer == 0:
                self.sound.play_effect("firebreath")
            if self.timer % 2 == 0:
                self.rect.x -= 4
            self.timer += 1
        else:
            self.alive = False

    def collide(self,player,collisionState):
        if player.type == "Player":
            player.damage()

class FireBall(EntityBase):
    def __init__(self,screen,x,y,harmful=True,despawn=False):
        super(FireBall,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,scale/2,scale/2)
        self.type = "Object"
        self.harmful = harmful
        self.despawn = despawn
        self.burst = False
        images = [sprites.get("fireball1"),sprites.get("fireball2"),sprites.get("fireball3"),sprites.get("fireball4")]
        self.animation = Animation(images)
        self.image = self.animation.image
        self.timer = 0
    
    def update(self,shift):
        if self.burst:
            self.vel.x = 0
            self.vel.y = 0
            self.timer +=1
            if self.timer >= 30:
                self.alive = False
        self.image = self.animation.image
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        self.animation.update()

    def explode(self):
        self.type = ""
        self.burst = True
        self.animation = Animation([sprites.get("explosion1"),sprites.get("explosion2"),sprites.get("explosion3")],deltaTime=5)
    
    def collide(self,entity,collisionState):
        hit = False
        if entity.type == "Player":
            if self.harmful:
                entity.damage()
                hit = True
        elif entity.type == "Mob" and not self.harmful:
            try:
                if not entity.fireproof:
                    entity.knockedoff = True
            except:
                entity.knockedoff = True
            points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,100)
            self.levelObj.entities.add(points)
            hit = True
        elif entity.type == "Boss" and not self.harmful:
            entity.damage()
            hit = True
        if self.despawn and hit:
            self.explode()

class PlayerFireBall(FireBall):
    def __init__(self,screen,x,y,level,direction):
        super(PlayerFireBall,self).__init__(screen,x,y,harmful=False,despawn=True)
        self.gravity = 1.25
        self.x = x
        self.levelObj = level
        self.inAir = False
        self.inJump = False
        self.vel.x = 6*direction
        self.collider = Collider(self,self.levelObj)
        self.traits = {"jumpTrait":JumpTrait(self,15)}
        self.timer = 0
        self.checkZone()

    def update(self,shift):
        super().update(shift)
        self.applyGravity()
        self.traits["jumpTrait"].jump(self.onGround)
        self.rect.y += self.vel.y
        self.collider.checkY()
        self.rect.x += self.vel.x
        if self.collider.checkX():
            self.explode()
        if self.timer > 300:
            self.alive = False
        try:
            if self.rect.y > self.zone.y1:
                self.alive = False
        except:
            pass
        if self.rect.x < self.x-scale*12 or self.rect.x > self.x+scale*12:
            self.alive = False
        self.timer += 1

    def collide(self,entity,collisionState):
        super().collide(entity,collisionState)

class Hammer(EntityBase):
    def __init__(self,screen,x,y,variant,direction):
        super(Hammer,self).__init__(x,y,0.8)
        self.screen = screen
        self.vel.x = 3*direction
        images = [sprites.get("hammer1",variant),sprites.get("hammer2",variant),sprites.get("hammer3",variant),sprites.get("hammer4",variant)]
        self.animation = Animation(images,deltaTime=5)
        self.image = self.animation.image
        self.onGround = True
        self.inAir = False
        self.inJump = False
        self.jumpTrait = JumpTrait(self,10)
        self.type = "Object"
        self.jumpTrait.jump(True)

    def update(self,shift):
        if self.timer < 480:
            self.image = self.animation.image
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
            self.animation.update()
            self.applyGravity()
            self.jumpTrait.jump(False)
            self.rect.x += self.vel.x
            self.rect.y += self.vel.y
        else:
            self.alive = False

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            if not entity.star:
                entity.damage()

    def hammerImage(variant):
        return sprites.get("hammer1",variant)
