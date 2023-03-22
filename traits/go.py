'''trait controlling moving left and right physics'''

class GoTrait:
    def __init__(self,ent):
        self.animation = ent.animation
        self.direction = 1
        self.heading = 1
        self.accelVel = 0.4
        self.decelVel = 0.25
        self.maxVel = 3.0
        self.boost = False
        self.jump = True
        self.entity = ent

    def update(self):
        if self.boost:
            self.maxVel = 6.0
            self.animation.deltaTime = 4
        else:
            self.animation.deltaTime = 7
            if abs(self.entity.vel.x) > 3.2:
                self.entity.vel.x = 3.2 * self.heading
            self.maxVel = 3.2
        if self.direction != 0:
            self.heading = self.direction
            if self.heading == 1:
                if self.entity.vel.x < self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading
            else:
                if self.entity.vel.x > -self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading

            if not self.entity.inAir:
                self.animation.update()
            else:
                self.animation.inAir()
        else:
            self.animation.update()
            if self.entity.vel.x >= 0:
                self.entity.vel.x -= self.decelVel
            else:
                self.entity.vel.x += self.decelVel
            if int(self.entity.vel.x) == 0:
                self.entity.vel.x = 0
                if self.entity.inAir:
                    self.animation.inAir()
                else:
                    self.animation.idle()
        self.entity.duck()
        if self.entity.lookingDown:
            if self.entity.powerUpState > 0:
                self.animation.duck()
