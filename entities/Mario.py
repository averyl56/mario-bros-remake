import pygame
from classes.Animation import Animation
from classes.Camera import Camera
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from classes.Input import Input
from entities.EntityBase import EntityBase
from entities.Particles import PlayerFireBall
from traits.bounce import bounceTrait
from traits.go import GoTrait
from traits.jump import JumpTrait
from traits.climb import ClimbTrait
from traits.swim import SwimTrait
from classes.Pause import Pause
from defaults import scale,colorkey
from classes.Spritesheet import PlayerSheet

sprites = PlayerSheet()

basicColors = {
    "normal": {1:(181,49,32),2:(107,109,0),3:(234,157,34)},
    "fire": {1:(247,215,165),2:(181,49,32),3:(234,157,34)},
}
starOverworld = {
    0:{1:(12,147,0),2:(234,157,34),3:(255,254,255)},
    1:{1:(181,49,32),2:(234,157,34),3:(255,254,255)},
    2:{1:(0,0,0),2:(153,79,0),3:(254,204,197)}
}
starUnderground = {
    0:{1:(0,125,141),2:(153,79,0),3:(254,204,197)},
    1:{1:(181,49,32),2:(234,157,34),3:(255,254,255)},
    2:{1:(0,64,77),2:(0,125,141),3:(181,235,242)}
}
starCastle = {
    0:{1:(0,125,141),2:(153,79,0),3:(254,204,197)},
    1:{1:(181,49,32),2:(234,157,34),3:(255,254,255)},
    2:{1:(102,102,102),2:(173,173,173),3:(255,254,255)}
}
starUnderwater = {
    0:{1:(173,173,173),2:(234,157,34),3:(255,254,255)},
    1:{1:(181,49,32),2:(234,157,34),3:(255,254,255)},
    2:{1:(0,0,0),2:(234,157,34),3:(255,254,255)}
}


class Mario(EntityBase):
    def __init__(self, x, y, level, screen, dashboard, sound, gravity=0.8, pastPowerUp=0):
        super(Mario, self).__init__(x, y, gravity)
        self.rect = pygame.Rect(x,y,scale-2,scale)
        self.sound = sound
        self.levelObj = level
        self.screen = screen
        self.dashboard = dashboard
        self.input = Input(self)
        self.inAir = False
        self.inJump = False
        self.type = "Player"
        self.powerUpState = 0
        self.invincibilityFrames = 0
        self.allowInput = True
        self.allowMovement = True
        self.camera = Camera(self, level)

        self.smallAnimation = Animation(
            [sprites.get("small-mario-run-1"),
            sprites.get("small-mario-run-2"),
            sprites.get("small-mario-run-3")],
            sprites.get("small-mario-idle"),
            sprites.get("small-mario-jump"))

        self.smallClimb = Animation(
            [sprites.get("small-mario-climb-1"),
            sprites.get("small-mario-climb-2")],
            sprites.get("small-mario-climb-1"),
            sprites.get("small-mario-jump"))

        self.smallSwim = Animation(
            [sprites.get("small-mario-swim-1"),
            sprites.get("small-mario-swim-2"),
            sprites.get("small-mario-swim-3"),
            sprites.get("small-mario-swim-4")],
            sprites.get("small-mario-swim-idle"),
            sprites.get("small-mario-jump"))

        self.bigAnimation = Animation(
            [sprites.get("big-mario-run-1"),
            sprites.get("big-mario-run-2"),
            sprites.get("big-mario-run-3")],
            sprites.get("big-mario-idle"),
            sprites.get("big-mario-jump"),
            sprites.get("mario-duck"))

        self.bigClimb = Animation(
            [sprites.get("big-mario-climb-1"),
            sprites.get("big-mario-climb-2")],
            sprites.get("big-mario-climb-1"),
            sprites.get("big-mario-jump"))

        self.bigSwim = Animation(
            [sprites.get("big-mario-swim-1"),
            sprites.get("big-mario-swim-2"),
            sprites.get("big-mario-swim-3"),
            sprites.get("big-mario-swim-4"),
            sprites.get("big-mario-swim-5")],
            sprites.get("big-mario-swim-idle"),
            sprites.get("big-mario-jump"))

        self.fireAnimation = Animation(
            [sprites.get("fire-run-1"),
            sprites.get("fire-run-2"),
            sprites.get("fire-run-3")],
            sprites.get("fire-idle"),
            sprites.get("fire-jump"),
            sprites.get("fire-duck"),
            sprites.get("fire-throw"))

        self.fireClimb = Animation(
            [sprites.get("fire-climb-1"),
            sprites.get("fire-climb-2")],
            sprites.get("fire-climb-1"),
            sprites.get("fire-jump"))

        self.fireSwim = Animation(
            [sprites.get("fire-swim-1"),
            sprites.get("fire-swim-2"),
            sprites.get("fire-swim-3"),
            sprites.get("fire-swim-4"),
            sprites.get("fire-swim-5")],
            sprites.get("fire-swim-idle"),
            sprites.get("fire-jump"),
            specialSprite=sprites.get("fire-throw"))

        self.animation = self.smallAnimation
        self.image = self.animation.image
        self.traits = {
            "jumpTrait": JumpTrait(self),
            "goTrait": GoTrait(self),
            "bounceTrait": bounceTrait(self),
        }
        self.collision = Collider(self, level)
        self.powerup(pastPowerUp)
        self.invincibilityFrames = 0
        self.EntityCollider = EntityCollider(self)
        self.restart = False
        self.pause = False
        self.pauseObj = Pause(screen, self, dashboard)
        self.zone = ""
        self.lookingLeft = False
        self.lookingRight = False
        self.lookingUp = False
        self.lookingDown = False
        self.climbing = False
        self.star = False
        self.throw = False #throwing fireballs
        self.godMode = False
        self.starTimer = 0
        self.starColor = 0

    def update(self):
        if self.invincibilityFrames > 0:
            if self.timer % 2 == 0:
                self.invincibilityFrames -= 1
            self.timer += 1
            if self.invincibilityFrames == 0:
                self.timer = 0
        self.checkZone()
        self.updateTraits()
        self.throwFireball()
        self.starPower()
        self.camera.move()
        if (self.invincibilityFrames//2) % 2 == 0:
            self.drawEntity()
        if self.allowMovement:
            self.image = self.animation.image
            self.moveMario()
            self.applyGravity()
            self.checkEntityCollision()
        else:
            self.vel.x = 0
            self.vel.y = 0
        self.checkStats()
        if self.allowInput:
            self.input.checkForInput()

    def moveMario(self):
        self.rect.y += self.vel.y
        self.collision.checkY()
        self.rect.x += self.vel.x
        self.collision.checkX()

    def drawEntity(self):
        #draws mario sprite
        if self.traits["goTrait"].heading == 1:
            self.screen.blit(self.image, self.getPos())
        elif self.traits["goTrait"].heading == -1:
            self.screen.blit(pygame.transform.flip(self.image, True, False), self.getPos())

    def duck(self):
        if self.lookingDown and self.rect.height == scale*2:
            self.rect = pygame.Rect(self.rect.x,self.rect.y+scale/2,self.rect.width,scale*1.5)
        elif not self.lookingDown and self.rect.height == scale*1.5:
            self.rect = pygame.Rect(self.rect.x,self.rect.y,self.rect.width,scale*2)
            self.collision.checkY()

    def updateAnimation(self, animation):
        self.animation = animation
        self.traits["goTrait"].animation = animation

    def checkZone(self):
        for zone in self.levelObj.zones:
            if zone.entInZone(self):
                if self.zone != zone:
                    self.zone = zone
                    self.camera.setZone(zone.x,zone.x1)
                    if zone.music != "":
                        if self.star:
                            self.sound.play_music("invincible",0)
                        else:
                            self.sound.play_music(zone.music,-1)

    def checkEntityCollision(self):
        hitBlock = False
        vine = False
        swim = False
        for ent in self.levelObj.entities:
            collisionState = self.EntityCollider.check(ent)
            if self.rect.colliderect(ent.rect):
                if ent.type == "Item":
                    ent.collide(self)
                elif ent.type == "Block" and not hitBlock:
                    ent.collide(self, collisionState)
                    hitBlock = True
                elif ent.type == "Mob" or ent.type == "Boss" or ent.type == "Object":
                    ent.collide(self, collisionState)
                elif ent.type == "Climb":
                    vine = True
                    ent.collide(self)
                elif ent.type == "Water":
                    swim = True
                    ent.collide(self)
        if vine == False and self.climbing:
            self.traits["goTrait"].reset()
        if swim == False and self.swimming:
            self.swimming = False
            self.go()

    def bounce(self):
        self.onGround = True
        self.bouncing = True
        self.traits["bounceTrait"].jump = True

    def damage(self):
        if self.invincibilityFrames == 0 and not self.star and not self.godMode and self.allowInput:
            if self.powerUpState > 1:
                self.invincibilityFrames = 20
                self.powerUpState = 1
                if self.swimming and not self.onGround:
                    self.updateAnimation(self.bigSwim)
                else:
                    self.updateAnimation(self.bigAnimation)
                self.sound.play_effect("pipe")
            elif self.powerUpState == 1:
                self.invincibilityFrames = 20
                self.powerUpState = 0
                if self.swimming and not self.onGround:
                    self.updateAnimation(self.smallSwim)
                else:
                    self.updateAnimation(self.smallAnimation)
                self.rect = pygame.Rect(self.rect.x,self.rect.y+scale,scale-4,scale)
                self.traits["jumpTrait"].jumpHeight = 120
                self.sound.play_effect("pipe")
            elif self.powerUpState == 0:
                self.gameOver()

    def gameOver(self,pit=False):
        self.allowMovement = False
        if not pit:
            self.image = sprites.get("mario-death")
            self.levelObj.drawLevel()
        srf = pygame.Surface((640, 480))
        srf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        srf.set_alpha(128)
        self.sound.music_channel.stop()
        self.sound.play_sfx("death")

        for i in range(500, 20, -2):
            srf.fill((0, 0, 0))
            pygame.draw.circle(
                srf,
                (255, 255, 255),
                (int(self.camera.x + self.rect.x) + 16, self.rect.y + 16),i)
            self.screen.blit(srf, (0, 0))
            pygame.display.update()
            self.input.checkForExit()
        while self.sound.music_channel.get_busy():
            pygame.display.update()
            self.input.checkForExit()
        self.powerUpState = 0
        self.levelObj.lives -= 1
        if self.levelObj.lives > 0:
            self.levelObj.resetLevel()
        else:
            self.restart = True

    def getPos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.checkZone()
        
    def powerup(self, powerupID):
            if powerupID == 1: #red mushroom
                if self.powerUpState == 0:
                    self.powerUpState = 1
                    if self.swimming and not self.onGround:
                        self.updateAnimation(self.bigSwim)
                    else:
                        self.updateAnimation(self.bigAnimation)
                    self.rect = pygame.Rect(self.rect.x, self.rect.y-scale, scale-4, scale*2)
                    self.traits["jumpTrait"].jumpHeight = 140
                    self.invincibilityFrames = 20
            elif powerupID == 2: #fire flower
                if self.powerUpState != 2:
                    self.powerUpState = 2
                    if self.swimming and not self.onGround:
                        self.updateAnimation(self.fireSwim)
                    else:
                        self.updateAnimation(self.fireAnimation)
                    self.rect = pygame.Rect(self.rect.x, self.rect.y-scale, scale-4, scale*2)
                    self.traits["jumpTrait"].jumpHeight = 140
                    self.throwCooldown = 0
                    self.fireBalls = []
                    self.invincibilityFrames = 20
                    self.running = False

    def checkStats(self):
        if self.dashboard.coins == 100:
            self.levelObj.lives += 1
            self.sound.play_effect("oneup")
            self.dashboard.coins = 0
        if self.dashboard.countDown:
            if self.dashboard.time == 0:
                self.gameOver()
            elif self.dashboard.time == 99:
                self.sound.play_effect("warning")

    def throwFireball(self):
        if self.powerUpState != 2 or self.climbing:
            return
        if self.throwCooldown > 0:
            if self.throwCooldown > 15:
                self.animation.special()
            self.throwCooldown -= 1
        if self.throw:
            if self.throwCooldown == 0 and len(self.fireBalls) < 4 and not self.running:
                self.animation.special()
                if self.traits["goTrait"].heading == 1:
                    fireball = PlayerFireBall(self.screen,self.rect.x+self.rect.width,self.rect.centery,self.levelObj,1)
                elif self.traits["goTrait"].heading == -1:
                    fireball = PlayerFireBall(self.screen,self.rect.x,self.rect.centery,self.levelObj,-1)
                self.levelObj.entities.add(fireball)
                self.fireBalls.append(fireball)
                self.throwCooldown = 30
                self.running = True
        else:
            self.running = False
        for i in range(len(self.fireBalls)):
            try:
                if not self.fireBalls[i].alive:
                    self.fireBalls.pop(i)
                    if i > 0:
                        i -= 1
            except:
                break

    def activateStar(self):
        self.star = True
        self.starTimer = 900
        self.starColor = 0
        self.sound.play_music("invincible",0)

    def starPower(self):
        if self.star:
            if self.starTimer > 0:
                surf = pygame.Surface((self.rect.width+4,self.rect.height))
                surf.fill(colorkey)
                surf.blit(self.image,(0,0))
                surf.set_colorkey(colorkey)
                mario = pygame.PixelArray(surf)
                if self.zone.theme == "overworld":
                    mario = self._setColor(mario,starOverworld)
                    if self.starTimer % 3 == 0:
                        mario = self._changeColor(mario,starOverworld)
                elif self.zone.theme == "underground":
                    mario = self._setColor(mario,starUnderground)
                    if self.starTimer % 3 == 0:
                        mario = self._changeColor(mario,starUnderground)
                elif self.zone.theme == "castle":
                    mario = self._setColor(mario,starCastle)
                    if self.starTimer % 3 == 0:
                        mario = self._changeColor(mario,starCastle)
                elif self.zone.theme == "underwater":
                    mario = self._setColor(mario,starUnderwater)
                    if self.starTimer % 3 == 0:
                        mario = self._changeColor(mario,starUnderwater)
                self.image = mario.surface
                self.starTimer -= 1
            else:
                self.star = False
                self.starColor = 0
                self.sound.play_music(self.zone.music,-1)

    def _setColor(self,mario,starColors):
        if self.powerUpState == 2:
            colors = basicColors["fire"]
        else:
            colors = basicColors["normal"]
        mario.replace(colors[1],starColors[self.starColor][1])
        mario.replace(colors[2],starColors[self.starColor][2])
        mario.replace(colors[3],starColors[self.starColor][3])
        return mario

    def _changeColor(self,mario,starColors):
        lastColor = self.starColor
        if self.starColor == 2:
            self.starColor = 0
        else:
            self.starColor += 1
        mario.replace(starColors[lastColor][1],starColors[self.starColor][1])
        mario.replace(starColors[lastColor][2],starColors[self.starColor][2])
        mario.replace(starColors[lastColor][3],starColors[self.starColor][3])
        return mario

    def jump(self,isJumping):
        if self.swimming:
            self.traits["goTrait"].jump(isJumping)
        else:
            self.traits['jumpTrait'].jump(isJumping)

    def slide(self):
        if self.powerUpState == 0:
            return sprites.get("small-mario-climb-1")
        elif self.powerUpState == 1:
            return sprites.get("big-mario-climb-1")
        elif self.powerUpState == 2:
            return sprites.get("fire-climb-1")
    
    def idle(self):
        if self.powerUpState == 0:
            self.image = sprites.get("small-mario-idle")
        elif self.powerUpState == 1:
            if self.rect.height == scale*1.5:
                self.rect = pygame.Rect(self.rect.x, self.rect.y-scale,self.rect.width,scale*2)
            self.image =  sprites.get("big-mario-idle")
        elif self.powerUpState == 2:
            if self.rect.height == scale*1.5:
                self.rect = pygame.Rect(self.rect.x, self.rect.y-scale,self.rect.width,scale*2)
            self.image = sprites.get("fire-idle")

    def go(self):
        self.gravity = 0.8
        self.traits["goTrait"] = GoTrait(self)
        if self.powerUpState == 0:
            self.updateAnimation(self.smallAnimation)
            self.traits["jumpTrait"].jumpHeight = 120
        elif self.powerUpState == 1:
            self.updateAnimation(self.bigAnimation)
            self.traits["jumpTrait"].jumpHeight = 140
        elif self.powerUpState == 2:
            self.updateAnimation(self.fireAnimation)
            self.traits["jumpTrait"].jumpHeight = 140

    def climb(self,vine):
        if not self.climbing and (self.lookingUp or self.lookingDown):
            self.climbing = True
            self.rect.x = vine.rect.centerx-self.rect.width
            self.traits["goTrait"] = ClimbTrait(self,vine)
            if self.powerUpState == 0:
                self.updateAnimation(self.smallClimb)
            elif self.powerUpState == 1:
                self.updateAnimation(self.bigClimb)
            elif self.powerUpState == 2:
                self.updateAnimation(self.fireClimb)
            if self.lookingUp:
                self.rect.y -= 5
            elif self.lookingDown:
                self.rect.y += 5
        elif self.climbing:
            self.traits["goTrait"].setVine(vine)
            self.onGround = True

    def swim(self,water):
        if not self.swimming:
            self.swimming = True
            self.gravity = 0.2
            self.traits["goTrait"] = SwimTrait(self,water)
            if self.powerUpState == 0:
                self.updateAnimation(self.smallSwim)
            elif self.powerUpState == 1:
                self.updateAnimation(self.bigSwim)
            elif self.powerUpState == 2:
                self.updateAnimation(self.fireSwim)









    def GODMODE(self,god):
        #only used for play testing, delete later
        self.godMode = god
        if self.godMode:
            print("God Mode Activated")
        else:
            print("God Mode Deactivated")