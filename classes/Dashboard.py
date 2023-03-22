import pygame
from classes.Font import Font

class Dashboard(Font):
    def __init__(self, filePath, size, screen):
        Font.__init__(self, filePath, size)
        self.state = "menu"
        self.screen = screen
        self.levelName = ""
        self.points = 0
        self.coins = 0
        self.ticks = 0
        self.lives = 0
        self.time = 0
        self.countDown = False
        self.stopTime = False

    def update(self):
        #update the dashboard
        self.draw()
        if not self.stopTime:
            self.updateTime()
    
    def draw(self):
        #draw sprites onto dashboard
        self.drawText("MARIO", 50, 20, 15)
        self.drawText(self.pointString(), 50, 37, 15)

        self.drawText("@x{}".format(self.coinString()), 225, 37, 15)

        self.drawText("WORLD", 380, 20, 15)
        self.drawText(str(self.levelName), 395, 37, 15)

        self.drawText("TIME", 520, 20, 15)
        if self.state != "menu":
            self.drawText(self.timeString(), 535, 37, 15)

    def updateTime(self):
        # update Time
        self.ticks += 1
        if self.ticks == 60:
            self.ticks = 0
            if self.countDown:
                self.time -= 1
            else:
                self.time += 1

    def drawText(self, text, x, y, size):
        #draws text in mario font from spritesheet
        for char in text:
            charSprite = pygame.transform.scale(self.charSprites[char], (size, size))
            self.screen.blit(charSprite, (x, y))
            if char == " ":
                x += size//2
            else:
                x += size

    def coinString(self):
        #number of coins collected
        return "{:02d}".format(self.coins)

    def pointString(self):
        #number of points collected
        return "{:06d}".format(self.points)

    def timeString(self):
        #time passed
        return "{:03d}".format(self.time)
