from entities.EntityBase import EntityBase
from classes.Animation import Animation
import pygame
from defaults import scale
from classes.Spritesheet import Itemsheet
from traits.leftrightwalk import LeftRightWalkTrait
from entities.ObjectEnemies import *

sprites = Itemsheet()

class Pipe(EntityBase):
    def __init__(self,screen,x,y,name,level,orientation,sound,goTo="",enemy="",variant=0):
        super(Pipe,self).__init__(x,y,0)
        self.screen = screen
        self.xVel = 0
        self.yVel = 0
        if orientation == "down":
            self.rect = pygame.Rect(x,y-1,scale*2,scale*2+1)
            self.yVel = 2
        elif orientation == "up":
            self.rect = pygame.Rect(x,y,scale*2,scale*2+1)
            self.yVel = -2
        elif orientation == "right":
            self.rect = pygame.Rect(x-1,y,scale*2+1,scale*2)
            self.xVel = 2
        elif orientation == "left":
            self.rect = pygame.Rect(x,y,scale*2+1,scale*2)
            self.xVel = -2
        self.name = name
        self.levelObj = level
        self.orientation = orientation
        self.type = "Object"
        self.sound = sound
        self.goTo = goTo
        self.enemy = enemy
        if self.enemy != "":
            self.variant = variant
        if self.enemy == "plant" and self.orientation == "down" or self.orientation == "up":
            self.enemy = PiranhaPlant(self.screen,self.rect.x,self.rect.y,self.variant,self,self.levelObj)
            self.levelObj.entities.add(self.enemy)
        self.timer = 0
        self.destination = -1
        self.side = -1
        self.player = None
        self.entering = False
        self.exiting = False

    def update(self,shift):
        if self.destination != -1 and self.player is not None:
            sides = [self.player.rect.bottom,self.player.rect.top,self.player.rect.right,self.player.rect.left]
            if sides[self.side] != self.destination:
                if self.timer % 2 == 0:
                    if self.entering:
                        self.player.rect.x += self.xVel
                        self.player.rect.y += self.yVel
                    elif self.exiting:
                        self.player.rect.x -= self.xVel
                        self.player.rect.y -= self.yVel
                self.timer += 1
            else:
                self.destination = -1
                self.timer = 0
                if self.entering:
                    self.entering = False
                    for entity in self.levelObj.entities:
                        if isinstance(entity,Pipe) or isinstance(entity,Drop):
                            if entity.name == self.goTo:
                                entity.exit(self.player)
                                self.player = None
                elif self.exiting:
                    self.exiting = False
                    self.player.allowMovement = True
                    self.player.allowInput = True
                    self.player = None

    def enter(self,player):
        self.sound.play_sfx("pipe")
        self.player = player
        player.allowMovement = False
        player.allowInput = False
        self.entering = True
        if self.orientation == "down":
            player.idle()
            player.rect.centerx = self.rect.centerx
            self.destination = self.rect.bottom
            self.side = 0
        elif self.orientation == "up":
            player.idle()
            player.rect.centerx = self.rect.centerx
            self.destination = self.rect.top
            self.side = 1
        elif self.orientation == "right":
            player.rect.bottom = self.rect.bottom
            self.destination = self.rect.right
            self.side = 2
        elif self.orientation == "left":
            player.rect.bottom = self.rect.bottom
            self.destination = self.rect.left
            self.side = 3
            self.timer = 0

    def exit(self,player):
        self.sound.play_sfx("pipe")
        self.player = player
        self.exiting = True
        if self.orientation == "down":
            player.idle()
            player.rect.centerx = self.rect.centerx
            player.rect.top = self.rect.top
            self.destination = self.rect.top
            self.side = 0
        elif self.orientation == "up":
            player.idle()
            player.rect.centerx = self.rect.centerx
            player.rect.top = self.rect.top
            self.destination = self.rect.bottom
            self.side = 1
        elif self.orientation == "left":
            player.rect.left = self.rect.left
            player.rect.bottom = self.rect.bottom
            self.destination = self.rect.right
            self.side = 3
        elif self.orientation == "right":
            player.rect.right = self.rect.right
            player.rect.bottom = self.rect.bottom
            self.destination = self.rect.left
            self.side = 2
            self.timer = 0


    def collide(self,player,collisionState):
        if player.type != "Player" or self.goTo == "":
            return
        if self.orientation == "down":
            if player.lookingDown and player.rect.bottom == self.rect.top+1:
                player.rect.centerx = self.rect.centerx
                self.enter(player)
        elif self.orientation == "up":
            if player.lookingUp and player.rect.top == self.rect.bottom-1:
                player.rect.centerx = self.rect.centerx
                self.enter(player)
        elif self.orientation == "left":
            if player.lookingLeft and player.rect.left == self.rect.right-1:
                self.enter(player)
        elif self.orientation == "right":
            if player.lookingRight and player.rect.right == self.rect.left+1:
                self.enter(player)

class Drop(EntityBase):
    def __init__(self,screen,x,y,width,height,name,level,goTo="",vine=False):
        super(Drop,self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y,width,height)
        self.screen = screen
        self.name = name
        self.levelObj = level
        self.type = "Object"
        self.goTo = goTo
        self.vine = vine

    def exit(self,player):
        player.setPos(self.rect.x,self.rect.y)
        player.allowInput = True
        player.allowMovement = True

    def collide(self,player,collisionState):
        if player.type != "Player" or self.goTo == "":
            return
        if self.vine:
            vineFound = False
            for entity in self.levelObj.entities:
                if entity.type == "Climb" and entity.rect.colliderect(self.rect):
                    vineFound = True
                    break
            if not vineFound:
                return 
        for entity in self.levelObj.entities:
            if isinstance(entity,Pipe) or isinstance(entity,Drop):
                if entity.name == self.goTo:
                    if self.vine:
                        if player.climbing:
                            entity.exit(player)
                    else:
                        entity.exit(player)

class WorldPipe(EntityBase):
    def __init__(self,screen,x,y,level,goToWorld,sound):
        super(WorldPipe,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y-1,scale*2,scale*2+1)
        self.levelObj = level
        self.world = str(goToWorld)
        self.sound = sound
        self.timer = 0
        self.type = "Object"
        self.player = None

    def update(self,shift):
        if self.player is not None:
            if self.player.rect.bottom != self.rect.bottom:
                if self.timer % 2 == 0:
                        self.player.rect.y += 2
                self.timer += 1
            else:
                self.player = None
                self.levelObj.nextLevel(self)

    def enter(self,player):
        self.sound.play_sfx("pipe")
        self.player = player
        player.idle()
        player.allowMovement = False
        player.allowInput = False

    def collide(self,player,collisionState):
        if player.type != "Player":
            return
        if player.lookingDown and player.rect.bottom == self.rect.top+1:
            player.rect.centerx = self.rect.centerx
            self.enter(player)


class EndOfLevel(EntityBase):
    def __init__(self,x,y,sound):
        super(EndOfLevel,self).__init__(x,y,0)
        self.rect = pygame.Rect(x,y,scale,scale)
        self.type = "Object"
        self.player = None
        self.timer = 0
        self.sound = sound

    def update(self,shift):
        if self.player is not None:
            if not self.sound.music_channel.get_busy():
                if (self.player.dashboard.time%100)%11 == 0:
                    if self.timer < 70:
                        if self.timer % 20 == 0:
                            self.sound.play_sfx("fireworks")
                        self.timer += 1
                    else:
                        self.player.levelObj.nextLevel()
                else:
                    self.player.levelObj.nextLevel()
                
    def collide(self,player,state):
        if player.type != "Player":
            return
        self.player = player
        self.player.allowMovement = False

class FlagPole(EntityBase):
    def __init__(self,screen,x,y,height,variant,level,sound):
        super(FlagPole,self).__init__(x,y,0)
        self.screen = screen
        self.rect = pygame.Rect(x,y,scale,height)
        self.flagSprite = sprites.get("flag",variant)
        self.flag = self.flagSprite.get_rect(topleft=(self.rect.centerx-scale,self.rect.y+scale))
        self.sound = sound
        self.player = None
        self.type = "Object"
        self.timer = 0
        self.levelObj = level
        self.reached = False

    def update(self,shift):
        if self.player is not None:
            if self.player.rect.bottom < self.rect.bottom-4:
                if self.timer % 2 == 0:
                    self.player.rect.y += 4
                    if self.flag.bottom < self.rect.bottom-8:
                        self.flag.y += 4
                self.timer += 1
            else:
                self.sound.sfx_channel.stop()
                self.sound.play_music("stage clear",0)
                self.player.traits["goTrait"] = LeftRightWalkTrait(self.player,self.levelObj,direction=1)
                self.player.obeyGravity = True
                self.player.allowMovement = True
                self.player = None
                
        self.screen.blit(self.flagSprite,(((self.flag.x/32)+shift)*32,self.flag.y))

    def collide(self,player,collisionState):
        if player.type != "Player":
            return
        if self.reached:
            return
        self.player = player
        self.player.allowInput = False
        self.player.allowMovement = False
        self.player.image = pygame.transform.flip(self.player.slide(),True,False)
        self.player.rect.x = self.rect.centerx
        self.player.obeyGravity = False
        self.sound.play_sfx("flagpole")
        self.reached = True
        self.levelObj.dashboard.stopTime = True
        for entity in self.levelObj.entities:
            try:
                if entity.type == "Mob":
                    entity.alive = False
            except:
                pass

class NPC(EntityBase):
    def __init__(self,screen,x,y,name,level,sound):
        super(NPC,self).__init__(x,y,0.8)
        self.screen = screen
        self.name = name
        self.levelObj = level
        self.dashboard = self.levelObj.dashboard
        self.sound = sound
        if self.name == "toad":
            self.image = sprites.get("toad")
            self.rect = pygame.Rect(x,y-scale,scale,scale*2)
        elif self.name == "princess":
            self.image = sprites.get("peach1")
            self.rect = pygame.Rect(x,y-scale,scale,scale*2)
        self.reached = False
        self.timer = 0
        self.type = "Object"

    def update(self,shift):
        self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
        if self.reached:
            if self.name == "toad":
                if self.timer < 360:
                    self.dashboard.drawText("THANK YOU MARIO!",(self.getPosIndexAsFloat().x+shift)*32-scale*5,self.rect.y-scale*6,scale/2)
                    self.dashboard.drawText(" BUT OUR PRINCESS IS IN",(self.getPosIndexAsFloat().x+shift)*32-scale*7,self.rect.y-scale*4,scale/2)
                    self.dashboard.drawText(" ANOTHER CASTLE!",(self.getPosIndexAsFloat().x+shift)*32-scale*7,self.rect.y-scale*3,scale/2)
                elif self.timer == 360:
                    self.levelObj.nextLevel()
            elif self.name == "princess":
                if not self.sound.music_channel.get_busy():
                    self.sound.play_music("princess saved",0)
                if self.timer < 820:
                    if self.levelObj.version == 1:
                        self.dashboard.drawText("THANK YOU MARIO!",(self.getPosIndexAsFloat().x+shift)*32-scale*5,self.rect.y-scale*6,scale/2)
                        self.dashboard.drawText(" YOUR QUEST IS OVER.",(self.getPosIndexAsFloat().x+shift)*32-scale*6,self.rect.y-scale*5,scale/2)
                        self.dashboard.drawText(" WE PRESENT YOU A NEW QUEST.",(self.getPosIndexAsFloat().x+shift)*32-scale*8,self.rect.y-scale*4,scale/2)
                        self.dashboard.drawText(" PRESS LSHIFT ON THE MAIN MENU",(self.getPosIndexAsFloat().x+shift)*32-scale*8,self.rect.y-scale*2,scale/2)
                        self.dashboard.drawText(" TO START YOUR NEW ADVENTURE!",(self.getPosIndexAsFloat().x+shift)*32-scale*8,self.rect.y-scale,scale/2)
                    else:
                        pass
                else:
                    self.levelObj.savedPrincess()
            self.timer += 1

    def collide(self,player,collisionState):
        if player.type != "Player":
            return
        if self.reached:
            return
        player.go()
        player.traits["goTrait"].direction = 0
        self.reached = True

class Axe(EntityBase):
    def __init__(self,screen,x,y,variant,name,level,sound):
        super(Axe,self).__init__(x,y,0)
        self.screen = screen
        self.levelObj = level
        self.name = name
        self.sound = sound
        self.triggered = False
        images = [sprites.get("axe1",variant),sprites.get("axe2",variant),sprites.get("axe3",variant),sprites.get("axe4",variant)]
        self.animation = Animation(images,deltaTime=10)
        self.image = self.animation.image
        self.type = "Object"
        self.timer = 0
        self.player = None
        self.bridges = []
        self.bowser = None
        self.counter = -1

    def update(self,shift):
        if self.image != "":
            self.image = self.animation.image
            self.screen.blit(self.image,((self.getPosIndexAsFloat().x+shift)*32,self.rect.y))
            self.animation.update()
        if self.triggered:
            if self.counter > 0:
                if self.timer % 4 == 0:
                    for bridge in self.bridges:
                        if bridge.place == self.counter:
                            self.sound.play_sfx("break")
                            bridge.destroy()
                            self.counter -= 1
                self.timer += 1
            elif self.counter == 0:
                if self.bowser is not None:
                    if self.bowser.alive:
                        self.levelObj.dashboard.points += 10000
                        self.sound.play_sfx("bowser falls")
                        self.bowser.allowMovement = True
                        self.bowser.obeyGravity = True
                    self.bowser = None
                else:
                    if self.player is not None:
                        self.sound.play_music("stage clear",0)
                        self.player.rect.x += 5
                        self.player.traits["goTrait"] = LeftRightWalkTrait(self.player,self.levelObj,direction=1)
                        self.player.allowMovement = True
                        self.player.obeyGravity = True
                        self.player = None
                        self.alive = False

    def collide(self,entity, collisionState):
        if entity.type == "Player" and not self.triggered:
            self.player = entity
            self.player.allowMovement = False
            self.player.allowInput = False
            self.player.obeyGravity = False
            for entity in self.levelObj.entities:
                try:
                    if entity.name == self.name and entity.type != "Object":
                        self.bridges.append(entity)
                    elif entity.name == self.name+"_bowser":
                        self.bowser = entity
                        self.bowser.allowMovement = False
                        self.bowser.obeyGravity = False
                except:
                    pass
            self.counter = len(self.bridges)
            self.image = ""
            self.levelObj.dashboard.stopTime = True
            self.triggered = True

class CastleBridge(EntityBase):
    def __init__(self,x,y,name,tile,spot):
        super(CastleBridge,self).__init__(x,y,0)
        self.name = name
        self.tile = tile
        self.place = spot
        self.type = ""

    def destroy(self):
        self.tile.alive = False
        self.alive = False

