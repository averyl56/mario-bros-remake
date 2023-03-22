class JumpTrait:
    def __init__(self, entity, jumpHeight=120, ySpeed=-12):
        self.verticalSpeed = ySpeed
        self.entity = entity
        self.jumpHeight = jumpHeight
        self.initalHeight = 384
        self.deaccelerationHeight = self.jumpHeight - ((self.verticalSpeed*self.verticalSpeed)/(2*self.entity.gravity))
        self.fromSpring = False
        self.springStrength = 0

    def jump(self, jumping):
        if jumping:
            if self.entity.onGround:
                if self.entity.bouncing:
                    self.jumpHeight += 100
                else:
                    try:
                        if self.entity.powerUpState == 0:
                            self.entity.sound.play_sfx("small jump")
                        else:
                            self.entity.sound.play_sfx("big jump")
                    except:
                        pass
                self.entity.vel.y = self.verticalSpeed
                self.entity.inAir = True
                self.initalHeight = self.entity.rect.y
                self.entity.inJump = True
                self.entity.obeyGravity = False  # always reach maximum height

        if self.entity.inJump:
            if (self.initalHeight-self.entity.rect.y) >= self.deaccelerationHeight or self.entity.vel.y == 0:
                self.entity.inJump = False
                self.entity.obeyGravity = True
                if self.fromSpring:
                    self.fromSpring = False
                    self.updateJump(self.formerJumpHeight)

    def reset(self):
        self.entity.inAir = False
        if self.entity.bouncing:
            self.jumpHeight -= 100
            self.entity.bouncing = False

    def boost(self,ifBoost):
        if not self.fromSpring:
            if ifBoost:
                if self.entity.powerUpState == 0:
                    self.updateJump(150)
                else:
                    self.updateJump(170)
            else:
                if self.entity.powerUpState == 0:
                    self.updateJump(120)
                else:
                    self.updateJump(140)

    def updateJump(self,height):
        self.jumpHeight = height
        self.deaccelerationHeight = self.jumpHeight - ((self.verticalSpeed*self.verticalSpeed)/(2*self.entity.gravity))

    def updateVerticalSpeed(self,vertSpeed):
        self.verticalSpeed = vertSpeed
        self.deaccelerationHeight = self.jumpHeight - ((self.verticalSpeed*self.verticalSpeed)/(2*self.entity.gravity))

    def spring(self,strength):
        if strength == 1:
            self.fromSpring = True
            self.formerJumpHeight = self.jumpHeight
            self.updateJump(250)
        if strength == 2:
            self.fromSpring = True
            self.formerJumpHeight = self.jumpHeight
            self.updateJump(400)
