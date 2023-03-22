class ClimbTrait:
    def __init__(self,ent,vine=None):
        self.animation = ent.animation
        self.direction = -1
        self.heading = 1
        self.speed = 2
        self.boost = False
        self.entity = ent
        self.entity.obeyGravity = False
        self.entity.onGround = True
        self.vine = vine

    def update(self):
        self.entity.onGround = True
        if self.boost:
            self.speed = 4
            self.animation.deltaTime = 4
        else:
            self.animation.deltaTime = 7
            self.speed = 2
        if self.direction != 0:
            self.heading = -self.direction
            if self.direction == 1:
                self.entity.rect.x = self.vine.rect.centerx
            elif self.direction == -1:
                self.entity.rect.x = self.vine.rect.centerx-self.entity.rect.width
            self.animation.update()
        elif self.entity.lookingUp:
            self.entity.vel.y = -self.speed
            self.animation.update()
        elif self.entity.lookingDown:
            self.entity.vel.y = self.speed 
            self.animation.update()
        elif not self.entity.inJump:
            self.entity.vel.x = 0
            self.entity.vel.y = 0
            self.animation.idle()

    def setVine(self,vine):
        self.vine = vine

    def reset(self):
        self.entity.onGround = False
        self.entity.obeyGravity = True
        self.entity.climbing = False
        self.entity.go()

    