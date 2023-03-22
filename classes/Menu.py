import json
import sys
import os
import pygame

from classes.Spritesheet import Spritesheet


class Menu:
    def __init__(self, screen, dashboard, level, sound):
        self.screen = screen
        self.sound = sound
        self.start = False
        self.inSettings = False
        self.state = 0
        self.level = level
        self.music = True
        self.sfx = True
        self.currSelectedLevel = 1
        self.levelNames = []
        self.inChoosingLevel = False
        self.dashboard = dashboard
        self.levelCount = 0
        self.spritesheet = Spritesheet("./textures/title_screen.png")
        self.menu_banner = self.spritesheet.image_at(0,60,2,colorkey=[255, 0, 220],ignoreTileSize=True,xTileSize=180,yTileSize=88)
        self.menu_dot = self.spritesheet.image_at(0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True)
        self.menu_dot2 = self.spritesheet.image_at(20, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True)
        self.version = 1
        self.allowVersion2 = False
        self.checkSave()
        self.loadSettings("./settings.json")

    def update(self):
        #updates main menu
        self.checkInput()
        if self.inChoosingLevel:
            return
        self.drawMenuBackground()
        self.dashboard.update()
        if not self.inSettings:
            self.drawMenu()
        else:
            self.drawSettings()

    def drawDot(self):
        #draw cursor dots
        if self.state == 0:
            self.screen.blit(self.menu_dot, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 313))
            self.screen.blit(self.menu_dot2, (145, 353))
            self.screen.blit(self.menu_dot2, (145, 393))
        elif self.state == 1:
            self.screen.blit(self.menu_dot, (145, 313))
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 353))
            self.screen.blit(self.menu_dot2, (145, 393))
        elif self.state == 2:
            self.screen.blit(self.menu_dot, (145, 353))
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 313))
            self.screen.blit(self.menu_dot2, (145, 393))
        elif self.state == 3:
            self.screen.blit(self.menu_dot, (145, 393))
            self.screen.blit(self.menu_dot2, (145, 353))
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 313))

    def checkSave(self):
        #checks if player accessed mario bros 2
        try:
            with open("./saveData.json") as jsonData:
                data = json.load(jsonData)
                return data["allowVersion2"]
        except:
            return False

    def loadSettings(self, url):
        #loads settings
        try:
            with open(url) as jsonData:
                data = json.load(jsonData)
                if data["sound"]:
                    self.music = True
                    self.sound.allow_music = True
                    self.sound.play_music("overworld",-1)
                else:
                    self.sound.allowMusic = False
                    self.music = False
                if data["sfx"]:
                    self.sfx = True
                    self.sound.allowSFX = True
                else:
                    self.sound.allowSFX = False
                    self.sfx = False
        except (IOError, OSError):
            self.sound.allowMusic = False
            self.music = False
            self.sound.allowSFX = False
            self.sfx = False
            self.saveSettings("./settings.json")

    def saveSettings(self, url):
        #saves settings
        data = {"sound": self.music, "sfx": self.sfx}
        with open(url, "w") as outfile:
            json.dump(data, outfile)

    def drawMenu(self):
        #draws text and cursors on menu
        self.drawDot()
        self.dashboard.drawText("START",180,280,24)
        self.dashboard.drawText("CHOOSE LEVEL", 180, 320, 24)
        self.dashboard.drawText("SETTINGS", 180, 360, 24)
        self.dashboard.drawText("EXIT", 180, 400, 24)

    def drawMenuBackground(self, withBanner=True):
        #draws background of menu
        for y in range(0, 13):
            for x in range(0, 20):
                self.screen.blit(self.level.sprites.spriteCollection.get("sky").image,(x * 32, y * 32))
        for y in range(13, 15):
            for x in range(0, 20):
                self.screen.blit(self.level.sprites.spriteCollection.get("ground").image,(x * 32, y * 32))
        if withBanner:
            self.screen.blit(self.menu_banner, (150, 80))
        self.screen.blit(self.level.sprites.spriteCollection.get("mario_idle").image,(2 * 32, 12 * 32))
        self.screen.blit(self.level.sprites.spriteCollection.get("bush_1").image, (14 * 32, 12 * 32))
        self.screen.blit(self.level.sprites.spriteCollection.get("bush_2").image, (15 * 32, 12 * 32))
        self.screen.blit(self.level.sprites.spriteCollection.get("bush_2").image, (16 * 32, 12 * 32))
        self.screen.blit(self.level.sprites.spriteCollection.get("bush_2").image, (17 * 32, 12 * 32))
        self.screen.blit(self.level.sprites.spriteCollection.get("bush_3").image, (18 * 32, 12 * 32))
        self.screen.blit(self.level.sprites.spriteCollection.get("goomba-1").image, (18.5*32, 12*32))

    def drawSettings(self):
        #draw text in settings
        self.drawDot()
        self.dashboard.drawText("MUSIC", 180, 280, 24)
        if self.music:
            self.dashboard.drawText("ON", 340, 280, 24)
        else:
            self.dashboard.drawText("OFF", 340, 280, 24)
        self.dashboard.drawText("SFX", 180, 320, 24)
        if self.sfx:
            self.dashboard.drawText("ON", 340, 320, 24)
        else:
            self.dashboard.drawText("OFF", 340, 320, 24)
        self.dashboard.drawText("RESET GAME", 180, 360, 24)
        self.dashboard.drawText("BACK", 180, 400, 24)

    def chooseLevel(self):
        #go to level select menu
        self.drawMenuBackground(False)
        self.inChoosingLevel = True
        self.levelNames = self.loadAllLevelNames()
        self.drawLevelChooser()

    def startGame(self):
        #starts campaign
        with open("./saveData.json") as jsonData:
            data = json.load(jsonData)
            currentWorld = data["currentWorld"]
        self.dashboard.state = "start"
        self.dashboard.time = 0
        self.level.campaign = True
        self.level.loadLevel(currentWorld+"-1",True)
        self.dashboard.levelName = currentWorld+"-1"
        self.start = True

    def resetGame(self):
        #resets all game progress
        with open("./saveData.json","r") as jsonData:
            data = json.load(jsonData)
        data["currentWorld"] = "1"
        data["completedLevels"] = []
        with open("./saveData.json","w") as jsonData:
            json.dump(data,jsonData)

    def drawBorder(self, x, y, width, height, color, thickness):
        #draws a frame border
        pygame.draw.rect(self.screen, color, (x, y, width, thickness))
        pygame.draw.rect(self.screen, color, (x, y+height, width, thickness))
        pygame.draw.rect(self.screen, color, (x, y, thickness, height))
        pygame.draw.rect(self.screen, color, (x+width, y, thickness, height+thickness))

    def drawLevelChooser(self):
        #draws each level option in the level select
        j = 1
        offset = 80
        textOffset = 90
        col = 0
        for i, levelName in enumerate(self.levelNames):
            if self.currSelectedLevel == i+1:
                color = (255, 255, 255)
            else:
                color = (150, 150, 150)
            self.dashboard.drawText(levelName, 120*(col)+textOffset, 50*j-20, 12)
            self.drawBorder(120*(col)+offset, 50*j-30, 100, 30, color, 5)
            if col == 3:
                j += 1
                col = 0
            else:
                col += 1

    def loadLevelNames(self):
        try:
            with open("./saveData.json") as jsonData:
                data = json.load(jsonData)
                if data["allowVersion2"]:
                    return self.loadAllLevelNames()
                levels = data["completedLevels"]
                levels.sort()
                self.levelCount = len(levels)
                return levels
        except:
            return self.loadAllLevelNames()
    
    def loadAllLevelNames(self):
        #gets all level names for level select, admin only
        res = []
        index = 0
        for r, d, f in os.walk("./levels"):
            for dir in d:
                level = dir
                for r,d,f in os.walk("./levels/"+level):
                    for file in f:
                        if ".json" in file:
                            levelNum = file.strip("level").strip(".json")
                            res.append(str(level)+"-"+levelNum)
            index += 1
        self.levelCount = len(res)
        res.sort()
        return res

    def checkInput(self):
        #checks for player input while in menu
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.inChoosingLevel or self.inSettings:
                        self.inChoosingLevel = False
                        self.inSettings = False
                        self.__init__(self.screen, self.dashboard, self.level, self.sound)
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_w:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel > 4:
                            self.currSelectedLevel -= 4
                            self.drawLevelChooser()
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_s:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel+4 <= self.levelCount:
                            self.currSelectedLevel += 4
                            self.drawLevelChooser()
                    if self.state < 3:
                        self.state += 1
                elif event.key == pygame.K_a:
                    if self.currSelectedLevel > 1:
                        self.currSelectedLevel -= 1
                        self.drawLevelChooser()
                elif event.key == pygame.K_d:
                    if self.currSelectedLevel < self.levelCount:
                        self.currSelectedLevel += 1
                        self.drawLevelChooser()
                elif event.key == pygame.K_RETURN:
                    if self.inChoosingLevel:
                        self.inChoosingLevel = False
                        self.dashboard.state = "start"
                        self.dashboard.time = 0
                        self.level.campaign = False
                        self.level.loadLevel(self.levelNames[self.currSelectedLevel-1])
                        self.dashboard.levelName = self.levelNames[self.currSelectedLevel-1]
                        self.start = True
                        return
                    if not self.inSettings:
                        if self.state == 0:
                            self.startGame()
                        elif self.state == 1:
                            self.chooseLevel()
                            self.state = 0
                        elif self.state == 2:
                            self.inSettings = True
                            self.state = 0
                        elif self.state == 3:
                            pygame.quit()
                            sys.exit()
                    else:
                        if self.state == 0:
                            if self.music:
                                self.sound.music_channel.stop()
                                self.music = False
                            else:
                                self.sound.play_music("overworld",-1)
                                self.music = True
                            self.saveSettings("./settings.json")
                        elif self.state == 1:
                            if self.sfx:
                                self.sound.allowSFX = False
                                self.sfx = False
                            else:
                                self.sound.allowSFX = True
                                self.sfx = True
                            self.saveSettings("./settings.json")
                        elif self.state == 2:
                            self.resetGame()
                        elif self.state == 3:
                            self.inSettings = False
        pygame.display.update()
