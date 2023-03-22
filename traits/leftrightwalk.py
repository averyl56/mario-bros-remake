import random
from classes.Collider import Collider


class LeftRightWalkTrait:
    def __init__(self, entity, level, speed=1, direction=0):
        if direction == 0:
            self.direction = random.choice([-1, 1])
        else:
            self.direction = direction
        self.entity = entity
        self.collDetection = Collider(self.entity, level)
        self.speed = speed
        self.entity.vel.x = self.speed * self.direction
        self.heading = self.direction

    def update(self):
        if self.entity.vel.x == 0:
            self.direction *= -1
        self.entity.vel.x = self.speed * self.direction
        self.heading = self.direction
        self.moveEntity()

    def moveEntity(self):
        if self.entity.type == "Player":
            self.entity.animation.update()
        self.entity.rect.y += self.entity.vel.y
        self.collDetection.checkY()
        self.entity.rect.x += self.entity.vel.x
        self.collDetection.checkX()
