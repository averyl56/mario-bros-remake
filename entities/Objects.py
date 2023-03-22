from defaults import scale
import pygame
from entities.EntityBase import EntityBase
from classes.Spritesheet import Itemsheet
from classes.Animation import Animation
from entities.ObjectEnemies import BulletBill
from entities.PowerUps import *
from entities.Particles import *
import math

sprites = Itemsheet()

class Brick(EntityBase):
    def __init__(self, screen, x, y, variant, sound, level, breakable=False, item="", hitsLeft=1, tile=None):
        super(Brick, self).__init__(x, y, 0)
        self.screen = screen
        self.hitsLeft = hitsLeft
        self.variant = variant
        self.rect = pygame.Rect(x,y,scale,scale+1)
        self.type = "Block"
        self.breakable = breakable
        if item == "" and not self.breakable:
            self.item = "coin"
        else:
            self.item = item
        self.images = {"empty":sprites.get("emptyBlock",variant),"broken":sprites.get("brickBreak",variant)}
        self.sound = sound
        self.triggered = False
        self.newItem = None
        self.bumping = False
        self.breaking = False
        self.isBig = False
        self.time = 0
        self.vel = 1
        self.levelObj = level
        self.tile = tile

    def setTile(self,tile):
        self.tile = tile

    def update(self,shift):
        if self.triggered:
            if not self.breakable:
                self.bumping = True
                if self.hitsLeft > 0:
                    item = CoinParticle(self.screen,self.rect.x,self.rect.y-32,self.sound,self.levelObj.dashboard)
                    self.levelObj.entities.add(item)
                elif self.hitsLeft == 0:
                    if self.item == "fireFlower" or self.item == "redMushroom":
                        if self.isBig:
                            self.newItem = FireFlower(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound)
                        else:
                            self.newItem = Mushroom(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound,0)
                        self.sound.play_effect("powerup appears")
                    elif self.item == "greenMushroom":
                        self.newItem = Mushroom(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound,1)
                        self.sound.play_effect("powerup appears")
                        #self.levelObj.entities.add(item)
                    elif self.item == "poisonMushroom":
                        self.newItem = Mushroom(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound,2)
                        self.sound.play_effect("powerup appears")
                        #self.levelObj.entities.add(item)
                    elif self.item == "star":
                        self.newItem = Star(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound)
                        self.sound.play_effect("powerup appears")
                        #self.levelObj.entities.add(item)
                    elif self.item == "coin":
                        item = CoinParticle(self.screen,self.rect.x,self.rect.y-scale,self.sound,self.levelObj.dashboard)
                        self.levelObj.entities.add(item)
                    elif self.item == "vine":
                        vine = Vine(self.screen,self.rect.x,self.rect.y-scale,self.variant,self.levelObj)
                        self.sound.play_effect("vine")
                        self.levelObj.entities.add(vine)
                    self.item = ""
                    try:
                        self.tile.image = self.images["empty"]
                    except:
                        print(self.x,self.y)
            else:
                if self.hitsLeft == 0:
                    self.sound.play_sfx("break")
                    self.breaking = True
                    self.tile.image = self.images["broken"]
                    piece = BrickParticles(self.screen,self.tile.x,self.tile.y,self.variant)
                    self.levelObj.entities.add(piece)
                    self.bumping = False
                else:
                    self.bumping = True
            self.triggered = False
        if self.hitsLeft < 1 and self.breakable:
            if self.time < 2:
                self.time += 1
            else:
                self.breaking = False
                self.alive = False
                self.tile.alive = False
        elif self.bumping:
            if self.time < 10:
                self.time += 1
                self.tile.rect = pygame.Rect(self.tile.rect.x,self.tile.rect.y-self.vel,self.tile.rect.width,self.tile.rect.height+self.vel)
                self.rect = pygame.Rect(self.rect.x,self.rect.y-2,self.rect.width,self.rect.height)
            elif self.time < 20:
                self.time += 1
                self.tile.rect = pygame.Rect(self.tile.rect.x,self.tile.rect.y+self.vel,self.tile.rect.width,self.tile.rect.height-self.vel)
                self.rect = pygame.Rect(self.rect.x,self.rect.y+2,self.rect.width,self.rect.height)
            else:
                if self.hitsLeft == 0:
                    self.alive = False
                else:
                    self.time = 0
                self.bumping = False
        if self.newItem is not None:
            if self.newItem.spawned:
                self.levelObj.entities.add(self.newItem)
            else:
                self.newItem.update(shift)
                self.screen.blit(self.tile.image,((self.getPosIndexAsFloat().x+shift)*32,self.tile.rect.y))

    def collide(self,entity,collisionState):
        if entity.type != "Player":
            return
        if self.breakable:
            if entity.powerUpState > 0:
                self.hitsLeft -= 1
                entity.dashboard.points += 50
        else:
            if entity.powerUpState > 0:
                self.isBig = True
            if self.hitsLeft > 0:
                self.hitsLeft -= 1
                if self.hitsLeft > 0:
                    self.levelObj.dashboard.coins += 1
                    self.levelObj.dashboard.points += 100
                elif self.hitsLeft == 0:
                    if self.item == "coin":
                        self.levelObj.dashboard.coins += 1
                        self.levelObj.dashboard.points += 100
        self.triggered = True
        self.checkEntityCollision()

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            if ent.type == "Mob":
                if self.rect.x-scale/2 <= ent.rect.x <= self.rect.right+scale/2:
                    if self.rect.y-scale/2 <= ent.rect.bottom <= self.rect.y+scale/2:
                        ent.knockedoff = True

class ItemBlock(EntityBase):
    def __init__(self, screen, x, y, variant, sound, level, hidden=False, item="", hitsLeft=1, tile=None):
        super(ItemBlock, self).__init__(x, y, 0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,scale,scale+1)
        self.images = {"idle":[sprites.get("block1",variant),sprites.get("block2",variant),sprites.get("block3",variant),sprites.get("block4",variant)],
                    "empty":sprites.get("emptyBlock",variant),"hidden":sprites.get("hidden",variant)}
        self.animation = Animation(self.images["idle"],deltaTime=10)
        self.variant = variant
        self.hidden = hidden
        if item == "":
            self.item = "coin"
        else:
            self.item = item
        self.hitsLeft = hitsLeft
        self.triggered = False
        self.bumping = False
        self.isBig = False
        self.type = "Block"
        self.time = 0
        self.newItem = None
        self.sound = sound
        self.vel = 1
        self.levelObj = level
        self.tile = tile

    def setTile(self,tile):
        self.tile = tile

    def update(self,shift):
        if self.triggered:
            if self.hitsLeft == 0:
                if self.item == "fireFlower" or self.item == "redMushroom":
                        if self.isBig:
                            self.newItem = FireFlower(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound)
                        else:
                            self.newItem = Mushroom(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound,0)
                        self.sound.play_effect("powerup appears")
                elif self.item == "greenMushroom":
                    self.newItem = Mushroom(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound,1)
                    self.sound.play_effect("powerup appears")
                    #self.levelObj.entities.add(item)
                elif self.item == "poisonMushroom":
                    self.newItem = Mushroom(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound,2)
                    self.sound.play_effect("powerup appears")
                    #self.levelObj.entities.add(item)
                elif self.item == "star":
                    self.newItem = Star(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,self.sound)
                    self.sound.play_effect("powerup appears")
                    #self.levelObj.entities.add(item)
                elif self.item == "coin":
                    item = CoinParticle(self.screen,self.rect.x,self.rect.y-scale,self.sound,self.levelObj.dashboard)
                    self.levelObj.entities.add(item)
                elif self.item == "vine":
                    vine = Vine(self.screen,self.rect.x,self.rect.y-scale,self.variant,self.levelObj)
                    self.sound.play_effect("vine")
                    self.levelObj.entities.add(vine)
                self.item = ""
            else:
                item = CoinParticle(self.screen,self.rect.x,self.rect.y-scale,self.sound,self.levelObj.dashboard)
                self.levelObj.entities.add(item)
            self.triggered = False
        if self.hitsLeft > 0:
            if self.hidden:
                self.tile.image = self.images["hidden"]
            else:
                self.animation.update()
                self.tile.image = self.animation.image
        else:
            self.tile.image = self.images["empty"]
            self.bumping = True
            if self.time < 10:
                self.time += 1
                self.tile.rect = pygame.Rect(self.tile.rect.x,self.tile.rect.y-self.vel,self.tile.rect.width,self.tile.rect.height+self.vel)
                self.rect = pygame.Rect(self.rect.x,self.rect.y-2,self.rect.width,self.rect.height)
            elif self.time < 20:
                self.time += 1
                self.tile.rect = pygame.Rect(self.tile.rect.x,self.tile.rect.y+self.vel,self.tile.rect.width,self.tile.rect.height-self.vel)
                self.rect = pygame.Rect(self.rect.x,self.rect.y+2,self.rect.width,self.rect.height)
            else:
                self.bumping = False
                self.alive = False
        if self.newItem is not None:
            if self.newItem.spawned:
                self.levelObj.entities.add(self.newItem)
            else:
                self.newItem.update(shift)
                self.screen.blit(self.tile.image,((self.getPosIndexAsFloat().x+shift)*32,self.tile.rect.y))

    def collide(self,entity,collisionState):
        if entity.type != "Player":
            return
        if entity.powerUpState > 0:
            self.isBig = True
        if self.hitsLeft > 0:
            self.hitsLeft -= 1
            if self.hitsLeft > 0:
                self.levelObj.dashboard.coins += 1
                self.levelObj.dashboard.points += 100
            elif self.hitsLeft == 0:
                if self.item == "coin":
                    self.levelObj.dashboard.coins += 1
                    self.levelObj.dashboard.points += 100
            self.triggered = True
            self.checkEntityCollision()

    def checkEntityCollision(self):
        for ent in self.levelObj.entities:
            if ent.type == "Mob":
                if self.rect.x-scale/2 <= ent.rect.x <= self.rect.right:
                    if self.rect.y-scale/2 <= ent.rect.bottom <= self.rect.y+scale/2:
                        ent.knockedoff = True

class Pit(EntityBase):
    def __init__(self,x,y,width):
        super(Pit,self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y,width,scale)
        self.type = "Object"

    def collide(self,ent,collisionState):
        if ent.type == "Player":
            ent.gameOver(pit=True)
        else:
            ent.alive = False
    
class Lava(EntityBase):
    def __init__(self,x,y,width):
        super(Lava,self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y+scale/4,width,scale)
        self.mobs = []
        self.timer = 0
        self.type = "Object"

    def update(self,shift):
        pass

    def collide(self,entity,collisionState):
        if entity.type == "Player":
            entity.gameOver()

class Water(EntityBase):
    def __init__(self,x,y,width,height):
        super(Water,self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y,width,height)
        self.type = "Water"

    def collide(self,entity):
        if entity.type == "Mob" or entity.type == "Player" or entity.type == "Item":
            entity.swim(self)

class FireBar(EntityBase):
    def __init__(self,screen,x,y,level,length=6,clockwise=False):
        super(FireBar,self).__init__(x,y,0)
        self.screen = screen
        self.length = length
        self.clockwise = clockwise
        if clockwise:
            self.direction = 1
        else:
            self.direction = -1
        self.speed = 5
        self.levelObj = level
        start = self.rect.centerx-scale/4
        yPos = self.rect.y+scale/4
        self.fireBalls = []
        for i in range(length):
            fireball = FireBall(self.screen,start,yPos,True)
            self.fireBalls.append(fireball)
            self.levelObj.entities.add(fireball)
            start += scale/2
        self.timer = 0
        self.rad = 0

    def update(self,shift):
        if self.timer % 5 == 0:
            for i in range(len(self.fireBalls)):
                radius = i*(scale/2)
                self.fireBalls[i].rect.centerx = radius*math.cos(self.rad*self.direction)+self.rect.centerx
                self.fireBalls[i].rect.centery = radius*math.sin(self.rad*self.direction)+self.rect.centery
            self.rad += math.pi/24
        self.timer += 1

class Spring(EntityBase):
    def __init__(self,screen,x,y,variant,strong,new=False):
        super(Spring,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,scale,scale*2)
        self.strong = strong
        if self.strong:
            if new:
                self.images = [sprites.get("superSpring1New",variant),sprites.get("superSpring2New",variant),sprites.get("superSpring3New",variant)]
            else:
                self.images = [sprites.get("superSpring1",variant),sprites.get("superSpring2",variant),sprites.get("superSpring3",variant)]
        else:
            if new:
                self.images = [sprites.get("spring1New",variant),sprites.get("spring2New",variant),sprites.get("spring3New",variant)]
            else:
                self.images = [sprites.get("spring1",variant),sprites.get("spring2",variant),sprites.get("spring3",variant)]
        self.image = self.images[0]
        self.player = None
        self.triggered = False
        self.timer = 0
        self.type = "Object"

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*scale,self.rect.y))
        if self.triggered:
            if self.timer < 5:
                self.player.rect.bottom = self.rect.top
            elif self.timer == 5:
                self.image = self.images[1]
                self.rect = pygame.Rect(self.rect.x,self.rect.y+scale/2,scale,scale*1.5)
                self.player.rect.bottom = self.rect.top
            elif self.timer < 15:
                self.player.rect.bottom = self.rect.top
            elif self.timer == 15:
                self.image = self.images[2]
                self.rect = pygame.Rect(self.rect.x,self.rect.y+scale/2,scale,scale)
                self.player.rect.bottom = self.rect.top
            elif self.timer < 25:
                self.player.rect.bottom = self.rect.top
            elif self.timer == 25:
                self.player.allowMovement = True
                self.player.onGround = True
                if self.strong:
                    self.player.traits["jumpTrait"].spring(2)
                else:
                    self.player.traits["jumpTrait"].spring(1)
                self.player.rect.y -= scale+6
                self.player.traits["jumpTrait"].jump(True)
                self.player.allowInput = True
            elif self.timer == 30:
                self.image = self.images[0]
                self.rect = pygame.Rect(self.rect.x,self.rect.y-scale,scale,scale*2)
                self.triggered = False
            self.timer += 1


    def collide(self,entity,collisionState):
        if entity.type == "Player" or entity.type == "Mob":
            if entity.vel.x > 0:
                if entity.bouncing:
                    entity.sound.play_sfx("bump")
                entity.vel.x = 0
                entity.rect.right = self.rect.left
            elif entity.vel.x < 0:
                if entity.bouncing:
                    entity.sound.play_sfx("bump")
                entity.vel.x = 0
                entity.rect.left = self.rect.right
            if entity.vel.y > 0 and not self.triggered:
                entity.onGround = True
                entity.rect.bottom = self.rect.top
                entity.vel.y = 0
                if entity.traits is not None:
                    if "JumpTrait" in entity.traits:
                        entity.traits["JumpTrait"].reset()
                    if "bounceTrait" in entity.traits:
                        entity.traits["bounceTrait"].reset()
                if entity.type == "Player" and not self.triggered:
                    self.player = entity
                    self.player.allowInput = False
                    self.player.allowMovement = False
                    self.timer = 0
                    self.triggered = True

class Gun(EntityBase):
    def __init__(self,screen,x,y,variant,level):
        super(Gun,self).__init__(x,y,0)
        self.screen = screen
        self.variant = variant
        self.levelObj = level
        self.sound = self.levelObj.sound
        self.interval = 360

    def update(self,shift):
        if self.timer % self.interval == 0:
            player = self.levelObj.mario
            if player.rect.x > self.rect.right:
                self.sound.play_effect("fireworks")
                self.levelObj.entities.add(BulletBill(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,1))
            elif player.rect.x < self.rect.x:
                self.sound.play_effect("fireworks")
                self.levelObj.entities.add(BulletBill(self.screen,self.rect.x,self.rect.y,self.variant,self.levelObj,-1))
        self.timer += 1