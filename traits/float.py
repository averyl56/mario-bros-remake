class FloatTrait:
    def __init__(self,entity,pos1,pos2,xVel=0,yVel=0):
        self.entity = entity
        self.point1 = pos1
        self.point2 = pos2
        self.xSpeed = xVel
        self.ySpeed = yVel
        self.finishedPath = False
        self.goBack = False
        if xVel > 0 or yVel < 0:
            self.goBack = True
            self.xSpeed = -self.xSpeed
            self.ySpeed = -self.ySpeed
        self.timer = 0

    #if horizontal, always make point1 greater than point2
    #if vertical, always make point2 greater than point1

    def update(self): 
        if self.finishedPath:
            if self.timer == 20:
                self.timer = 0
                self.finishedPath = False
            else:
                self.timer += 1
        elif self.goBack:
            if self.entity.rect.x < self.point1[0] or self.entity.rect.y > self.point1[1]:
                if self.timer % 10 == 0:
                    self.entity.vel.y = -self.ySpeed
                    self.entity.vel.x = -self.xSpeed
                self.timer += 1
            else:
                self.entity.vel.y = 0
                self.entity.vel.x = 0
                self.timer = 0
                self.goBack = False
                self.finishedPath = True
        elif not self.goBack:
            if self.entity.rect.x > self.point2[0] or self.entity.rect.y < self.point2[1]:
                if self.timer % 10 == 0:
                    self.entity.vel.y = self.ySpeed
                    self.entity.vel.x = self.xSpeed
                self.timer += 1
            else:
                self.entity.vel.y = 0
                self.entity.vel.x = 0
                self.timer = 0
                self.goBack = True
                self.finishedPath = True