'''Checks if an entity has collided with any non-entity objects'''
import pygame

class Collider:
    def __init__(self, entity, level):
        self.entity = entity
        self.ground = level.ground
        self.levelObj = level
        self.result = []

    def checkX(self):
        try:
            if self.leftLevelBorderReached() or self.rightLevelBorderReached():
                return True
            rows = [
                self.ground[self.entity.getPosIndex().y],
                self.ground[self.entity.getPosIndex().y + 1],
                self.ground[self.entity.getPosIndex().y + 2],
            ]
        except:
            return False
        for row in rows:
            tiles = row[self.entity.getPosIndex().x : self.entity.getPosIndex().x + 2]
            for tile in tiles:
                if tile is not None and not tile.passThrough:
                    if tile.rect.colliderect(self.entity.rect):
                        if self.entity.vel.x > 0:
                            if self.entity.bouncing:
                                self.entity.sound.play_sfx("bump")
                            self.entity.vel.x = 0
                            self.entity.rect.right = tile.rect.left #hit wall on left
                            return True
                        elif self.entity.vel.x < 0:
                            if self.entity.bouncing:
                                self.entity.sound.play_sfx("bump")
                            self.entity.vel.x = 0
                            self.entity.rect.left = tile.rect.right #hit wall on right
                            return True
        return False

    def checkY(self):
        self.entity.onGround = False

        try:
            rows = [
                self.ground[self.entity.getPosIndex().y],
                self.ground[self.entity.getPosIndex().y + 1],
                self.ground[self.entity.getPosIndex().y + 2],
            ]
        except:
            return False
        #add code for death due to pit
        for row in rows:
            tiles = row[self.entity.getPosIndex().x : self.entity.getPosIndex().x + 2]
            for tile in tiles:
                if tile is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.y > 0:
                            self.entity.onGround = True
                            self.entity.rect.bottom = tile.rect.top #entity on ground
                            self.entity.vel.y = 0
                            # reset jump on bottom
                            if self.entity.traits is not None:
                                if "JumpTrait" in self.entity.traits:
                                    self.entity.traits["JumpTrait"].reset()
                                if "bounceTrait" in self.entity.traits:
                                    self.entity.traits["bounceTrait"].reset()
                            return True
                        elif self.entity.vel.y < 0 and not tile.passThrough:
                            self.entity.rect.top = tile.rect.bottom #entity hit ceiling
                            self.entity.vel.y = 0
                            if self.entity.type == "Player":
                                self.entity.sound.play_sfx("bump")
                            return True
        return False

    def rightLevelBorderReached(self):
        if self.entity.rect.right > self.entity.zone.x1-1 and self.entity.vel.x > 0:
            if self.entity.type == "Player":
                self.entity.rect.right = self.entity.zone.x1-1
                self.entity.vel.x = 0
            else:
                self.entity.alive = False
            return True

    def leftLevelBorderReached(self):
        if self.entity.rect.left < self.entity.zone.x and self.entity.vel.x < 0:
            if self.entity.type == "Player":
                self.entity.rect.x = self.entity.zone.x
                self.entity.vel.x = 0
            else:
                self.entity.alive = False
            return True
