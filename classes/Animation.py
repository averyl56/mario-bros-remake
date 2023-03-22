'''object to control idle animations of entities'''

class Animation:
    def __init__(self, images, idleSprite=None, airSprite=None, duckSprite=None, specialSprite=None, deltaTime=7):
        self.images = images
        self.timer = 0
        self.index = 0
        self.image = self.images[self.index] #start with first image
        self.idleSprite = idleSprite
        self.airSprite = airSprite
        self.duckSprite = duckSprite
        self.specialSprite = specialSprite
        self.deltaTime = deltaTime #tick interval to change animation frame

    def update(self):
        #normal moving animation
        self.timer += 1
        if self.timer % self.deltaTime == 0:
            if self.index < len(self.images) - 1:
                self.index += 1 #go to next animation frame
            else:
                self.index = 0
        self.image = self.images[self.index]

    def idle(self): 
        #standing still
        self.image = self.idleSprite

    def inAir(self): 
        #jumping or falling
        self.image = self.airSprite

    def duck(self):
        #crouching
        self.image = self.duckSprite

    def special(self):
        #special action such as throwing fireball
        self.image = self.specialSprite
