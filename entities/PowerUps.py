from classes.Animation import Animation
from entities.EntityBase import EntityBase
from entities.Particles import Points
from traits.leftrightwalk import LeftRightWalkTrait
from traits.jump import JumpTrait
from classes.Spritesheet import Itemsheet
from defaults import *

sprites = Itemsheet()

class Coin(EntityBase):
    def __init__(self, screen, x, y, variant, sound, dashboard):
        super(Coin,self).__init__(x,y,0)
        self.screen = screen
        self.sound = sound
        self.dashboard = dashboard
        self.type = "Item"
        images = [sprites.get("coin1",variant),sprites.get("coin2",variant),sprites.get("coin3",variant),sprites.get("coin4",variant)]
        self.animation = Animation(images,deltaTime=10)
        self.timer = 0
        self.triggered = False

    def update(self,shift):
        if self.alive:
            if self.triggered:
                self.sound.play_effect("coin")
                self.alive = False
            else:
                self.animation.update()
                self.screen.blit(self.animation.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))

    def collide(self,player):
        if not self.triggered:
            if player.type == "Player":
                player.dashboard.coins += 1
                player.dashboard.points += 200
                self.triggered = True

class Mushroom(EntityBase):
    def __init__(self, screen, x, y, variant, level, sound, species, new=False):
        super(Mushroom, self).__init__(x,y,1.25)
        self.screen = screen
        self.image = ""
        if species == 0:
            if new:
                self.image = sprites.get("redMushroomNew")
            else:
                self.image = sprites.get("redMushroom")
        elif species == 1:
            if new:
                self.image = sprites.get("greenMushroomNew",variant)
            else:
                self.image = sprites.get("greenMushroom",variant)
        elif species == 3:
            if new:
                self.image = sprites.get("poisonMushroomNew",variant)
            else:
                self.image = sprites.get("poisonMushroom",variant)
        self.type = "Item"
        self.levelObj = level
        self.sound = sound
        self.species = species # 0 = red, 1 = green, 2 = poison
        self.leftrightTrait = LeftRightWalkTrait(self, level)
        self.timer = 0
        self.triggered = False
        self.spawned = False
        self.start = y

    def spawn(self,shift):
        if self.rect.y > self.start-scale:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
            self.rect.y -= 2
        else:
            self.checkZone()
            self.spawned = True

    def update(self, shift):
        if not self.spawned:
            self.spawn(shift)
        elif not self.triggered:
            self.applyGravity()
            self.draw(shift)
            self.leftrightTrait.update()
        else:
            self.onDead()

    def draw(self, shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x + shift)*32, self.rect.y))

    def onDead(self):
        if self.species != 2:
            points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,1000)
            self.levelObj.entities.add(points)
            self.alive = False
        else:
            self.alive = None

    def collide(self,player):
        if player.type != "Player":
            return
        if self.spawned and not self.triggered:
            if self.species == 0:
                player.powerup(1)
                self.sound.play_effect("powerup")
                self.levelObj.dashboard.points += 1000
            elif self.species == 1:
                self.levelObj.lives += 1
                self.sound.play_effect("oneup")
            elif self.species == 2:
                player.damage()
            self.triggered = True
            
class FireFlower(EntityBase):
    def __init__(self,screen,x,y,variant,level,sound):
        super(FireFlower,self).__init__(x,y,0)
        self.screen = screen
        self.type = "Item"
        images = [sprites.get("flower1",variant),sprites.get("flower2",variant),sprites.get("flower3",variant),sprites.get("flower4",variant)]
        self.animation = Animation(images,deltaTime=10)
        self.image = self.animation.image
        self.levelObj = level
        self.sound = sound
        self.timer = 0
        self.triggered = False
        self.spawned = False
        self.start = y

    def spawn(self,shift):
        if self.rect.y > self.start-scale:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
            self.rect.y -= 2
        else:
            self.checkZone()
            self.spawned = True

    def update(self, shift):
        if not self.spawned:
            self.spawn(shift)
        elif not self.triggered:
            self.draw(shift)
        else:
            self.onDead()

    def draw(self, shift):
        self.animation.update()
        self.image = self.animation.image
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x + shift)*32, self.rect.y))

    def onDead(self):
        points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,1000)
        self.levelObj.entities.add(points)
        self.alive = False

    def collide(self,player):
        if player.type != "Player":
            return
        if self.spawned and not self.triggered:
            player.powerup(2)
            self.sound.play_effect("powerup")
            self.levelObj.dashboard.points += 1000
            self.triggered = True

class Star(EntityBase):
    def __init__(self,screen,x,y,variant,level,sound):
        super(Star,self).__init__(x,y,0.8)
        self.screen = screen
        self.type = "Item"
        images = [sprites.get("star1",variant),sprites.get("star2",variant),sprites.get("star3",variant),sprites.get("star4",variant)]
        self.animation = Animation(images,deltaTime=10)
        self.image = self.animation.image
        self.levelObj = level
        self.sound = sound
        self.timer = 0
        self.inAir = False
        self.inJump = False
        self.triggered = False
        self.spawned = False
        self.start = y
        self.traits = {
            "jumpTrait": JumpTrait(self,60),
            "leftRightWalkTrait": LeftRightWalkTrait(self,level,1)
        }

    def spawn(self,shift):
        if self.rect.y > self.start-scale:
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
            self.rect.y -= 2
        else:
            self.checkZone()
            self.spawned = True

    def update(self, shift):
        if not self.spawned:
            self.spawn(shift)
        elif not self.triggered:
            self.applyGravity()
            self.draw(shift)
            self.traits["jumpTrait"].jump(self.onGround)
            self.updateTraits()
        else:
            self.onDead()

    def draw(self, shift):
        self.animation.update()
        self.image = self.animation.image
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x + shift)*32, self.rect.y))

    def onDead(self):
        points = Points(self.levelObj.dashboard,self.rect.x,self.rect.y,1000)
        self.levelObj.entities.add(points)
        self.alive = False

    def collide(self,player):
        if player.type != "Player":
            return
        if self.spawned and not self.triggered:
            self.sound.play_effect("powerup")
            self.levelObj.dashboard.points += 1000
            player.activateStar()
            self.triggered = True

class Vine(EntityBase):
    def __init__(self,screen,x,y,variant,level,count=0,limit=5):
        super(Vine,self).__init__(x,y,0)
        self.screen = screen
        self.count = count
        self.levelObj = level
        self.sprouted = False
        self.variant = variant
        self.limit = limit
        if self.count == limit or self.y == 0:
            self.image = sprites.get("vine1",variant)
        else:
            self.image = sprites.get("vine2",variant)
        self.timer = 0
        self.type = "Climb"

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        if not self.sprouted and (self.count < self.limit or self.y == 0):
            if self.timer == 10:
                vine = Vine(self.screen,self.rect.x,self.rect.y-scale,self.variant,self.levelObj,self.count+1,self.limit)
                self.levelObj.entities.add(vine)
                self.sprouted = True
                self.timer = 0
            else:
                self.timer += 1
    
    def collide(self,player):
        if player.type == "Player":
            player.climb(self)
