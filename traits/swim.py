'''trait controlling moving left and right physics'''

class SwimTrait:
    def __init__(self,ent,water):
        self.entity = ent
        self.animation = self.entity.animation
        self.water = water
        self.direction = 1
        self.heading = 1
        self.boost = False
        self.seaFloor = False
        self.verticalSpeed = -3
        self.jumpHeight = 80
        self.initalHeight = 384
        self.deaccelerationHeight = self.jumpHeight - ((self.verticalSpeed*self.verticalSpeed)/1.6)

    def update(self):
        if not self.seaFloor:
            self.accelVel = 0.2
            self.decelVel = 0.05
            if self.entity.onGround:
                if self.entity.powerUpState == 0:
                    self.entity.updateAnimation(self.entity.smallAnimation)
                elif self.entity.powerUpState == 1:
                    self.entity.updateAnimation(self.entity.bigAnimation)
                elif self.entity.powerUpState == 2:
                    self.entity.updateAnimation(self.entity.fireAnimation)
                self.seaFloor = True
            else:
                self.moveInWater()
        elif self.seaFloor:
            self.accelVel = 0.12
            self.decelVel = 0.08
            self.moveOnSeaFloor()

    def moveOnSeaFloor(self):
        if self.boost:
            self.maxVel = 3
            self.animation.deltaTime = 12
        else:
            self.animation.deltaTime = 15
            if abs(self.entity.vel.x) > 2:
                self.entity.vel.x = 2 * self.heading
            self.maxVel = 2
        if self.direction != 0:
            self.heading = self.direction
            if self.heading == 1:
                if self.entity.vel.x < self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading
            else:
                if self.entity.vel.x > -self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading
            self.animation.update()
        else:
            self.animation.update()
            if self.entity.vel.x >= 0:
                self.entity.vel.x -= self.decelVel
            else:
                self.entity.vel.x += self.decelVel
            if int(self.entity.vel.x) == 0:
                self.entity.vel.x = 0
                self.animation.idle()
        self.entity.duck()
        if self.entity.lookingDown:
            if self.entity.powerUpState > 0:
                self.animation.duck()

    def moveInWater(self):
        if self.boost:
            self.maxVel = 3
            self.animation.deltaTime = 15
        else:
            self.animation.deltaTime = 20
            self.maxVel = 2
        if self.direction != 0:
            self.heading = self.direction
            if self.heading == 1:
                if self.entity.vel.x < self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading
            else:
                if self.entity.vel.x > -self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading
            self.animation.update()
        else:
            if self.entity.vel.x >= 0:
                self.entity.vel.x -= self.decelVel
            else:
                self.entity.vel.x += self.decelVel
            if int(self.entity.vel.x) == 0:
                self.entity.vel.x = 0
        if self.entity.lookingDown:
            if self.entity.vel.y < 4:
                self.entity.vel.y += 0.5
        self.animation.update()

    def jump(self,isJumping):
        if isJumping:
            if not self.entity.sound.sfx_channel.get_busy():
                self.entity.sound.play_sfx("stomp")
            if self.seaFloor:
                if self.entity.powerUpState == 0:
                    self.entity.updateAnimation(self.entity.smallSwim)
                elif self.entity.powerUpState == 1:
                    self.entity.updateAnimation(self.entity.bigSwim)
                elif self.entity.powerUpState == 2:
                    self.entity.updateAnimation(self.entity.fireSwim)
                self.seaFloor = False
            self.entity.vel.y = self.verticalSpeed
            self.entity.inAir = True
            self.initalHeight = self.entity.rect.y
            self.entity.inJump = True
        if self.entity.inJump:
            if (self.initalHeight-self.entity.rect.y) >= self.deaccelerationHeight or self.entity.vel.y == 0 or self.entity.rect.y < self.water.rect.y:
                self.entity.inJump = False
        self.animation.update()