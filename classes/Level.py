'''Object controlling the layout of each level'''

import json
import pygame
import csv
from defaults import *
from classes.Sprites import Sprites
from classes.Spritesheet import Tilesheet
from classes.Zone import Zone
from classes.Tile import Tile
from classes.EntityAdder import EntityAdder

themes = ["overworld","underground","castle","underwater"]
defaultLives = 3
currentLives = 3

class Level:
    def __init__(self, screen, sound, dashboard):
        self.sprites = Sprites() #all from spritesheet, change later 
        self.dashboard = dashboard #stats at top of screen
        self.tiles = Tilesheet()
        self.lives = defaultLives
        self.sound = sound #sounds
        self.screen = screen #display screen
        self.pastPowerUpState = 0
        self.world = 0 #world
        self.level = 0 #level
        self.entities = pygame.sprite.Group()
        self.width = 0 #width of level pixels
        self.height = 0 #height of level pixels
        self.scale = 0 #rect multiplier to fit screen
        self.backgroundColor = ''
        self.mario = ""
        self.camera = ""
        self.zones = []
        self.sky = []
        self.background = []
        self.ground = []
        self.top = []
        self.campaign = False #False = levelSelect, True = go to next level
        self.version = 1

    def restart(self):
        return self.mario.restart

    def paused(self):
        return self.mario.pause

    def pause(self):
        self.mario.pauseObj.update()

    def resetLevel(self):
        '''resets the level from the beginning'''
        self.mario = ""
        self.camera = ""
        self.zones = []
        self.sky = []
        self.background = []
        self.ground = []
        self.top = []
        self.entities = pygame.sprite.Group()
        levelname = "{}-{}".format(self.world,self.level)
        self.loadLevel(levelname,self.campaign)

    def preLevel(self):
        '''shows pre level screen if on campaign'''
        timer = 0
        mario = self.sprites.spriteCollection.get("mario_idle").image
        while timer < 90:
            self.screen.fill("black")
            self.dashboard.drawText("WORLD {}-{}".format(self.world,self.level),windowSizeX/2-scale*4,windowSizeY/2-scale*2,scale)
            self.screen.blit(mario,(windowSizeX/2-scale*2, windowSizeY/2))
            self.dashboard.drawText("x {}".format(self.lives),windowSizeX/2,windowSizeY/2,scale)
            self.dashboard.draw()
            pygame.display.update()
            timer += 1

    def loadLevel(self, levelname, version=1):
        '''loads all parts of level from json file'''
        self.sound.music_channel.stop()
        world, level = levelname.split("-") #formatted world-level
        self.world = world
        self.level = level
        self.dashboard.levelName = levelname
        if self.campaign:
            self.preLevel()
        else:
            self.lives = 1
        self.dashboard.lives = self.lives
        with open("./levels/{}/level{}.json".format(world,level)) as jsonData:
            data = json.load(jsonData)
            self.width = data["width"]
            self.height = data["height"]
            self.scale = data["tileScale"]
            self.backgroundColor = data["backgroundColor"]
            if "time" in data:
                self.dashboard.countDown = True
                self.dashboard.time = data["time"]
            else:
                self.dashboard.countDown = False
                self.dashboard.time = 0
            self.loadZones(data)
            self.loadSky(data)
            self.loadBackground(data)
            self.loadGround(data)
            self.loadTop(data)
            self.loadEntities(data)
            self.dashboard.stopTime = False

    def calc(self,value,integer=True):
        '''rescales value to window size'''
        if integer:
            return (value//self.scale)*32
        else:
            return (value/self.scale)*32

    def checkZone(self,x,y):
        for zone in self.zones:
            if zone.inZone(x,y):
                return zone

    def loadZones(self,data):
        #loads all zones in
        for zone in data["zones"]:
            newZone = Zone(zone["name"],self.calc(zone["x"]),self.calc(zone["y"]),self.calc(zone["width"]),self.calc(zone["height"]),zone["theme"],zone["music"])
            self.zones.append(newZone)

    def loadEntities(self,data):
        #loads all entities
        adder = EntityAdder(self)
        entities = data["spawns"]
        for entity in entities:
            object = adder.getEntity(entity)
            if object is not None:
                if object.type == "Player":
                    self.mario = object
                    self.camera = self.mario.camera
                else:
                    self.entities.add(object)

    def loadSky(self, data):
        #loads sky sprites
        terrain_map = []
        with open(data["sky"]) as file:
            level = csv.reader(file)
            for row in level:
                terrain_map.append(list(row))
        self.sky = self.getTiles(terrain_map)

    def loadBackground(self, data):
        #loads background sprites
        terrain_map = []
        with open(data["background"]) as file:
            level = csv.reader(file)
            for row in level:
                terrain_map.append(list(row))
        self.background = self.getTiles(terrain_map)
                
    def loadGround(self, data):
        #loads ground sprites
        terrain_map = []
        with open(data["ground"]) as file:
            level = csv.reader(file)
            for row in level:
                terrain_map.append(list(row))
        self.ground = self.getTiles(terrain_map)

    def loadTop(self,data):
        #loads sprites that display on top of player
        terrain_map = []
        with open(data["renderOnTop"]) as file:
            level = csv.reader(file)
            for row in level:
                terrain_map.append(list(row))
        self.top = self.getTiles(terrain_map)

    def getTiles(self,terrain_map):
        #creates Tiles by parsing sprites from the tile spritesheet
        sprites = []
        for i,row in enumerate(terrain_map):
            line = []
            for j,id in enumerate(row):
                if id != "-1":
                    x = j*32
                    y = i*32
                    image = self.tiles.get(int(id))
                    sprite = Tile(image,x,y,32)
                    line.append(sprite)
                else:
                    line.append(None)
            sprites.append(line)
        return sprites
    
    def drawEntities(self,shift):
        #draw all entities in camera view
        for entity in self.entities:
            if not entity.alive:
                self.entities.remove(entity)
            elif -10 - int(shift + 1) <= entity.getPosIndexAsFloat().x <= 25 - int(shift - 1):
                entity.update(shift)

    def drawLevel(self):
        #draws all sprites in level
        self.screen.fill(self.backgroundColor)
        shift = self.camera.pos.x
        self.drawSky(shift)
        self.drawBackground(shift)
        self.drawGround(shift)
        self.drawEntities(shift)
        self.mario.update()
        self.drawTop(shift)

    def drawSky(self,shift):
        try:
            for y in range(0, len(self.sky)):
                for x in range(0 - int(shift + 1), 20 - int(shift - 1)):
                    if self.sky[y][x] is not None:
                        self.sky[y][x].draw(x + shift,self.screen)
        except IndexError:
            return

    def drawBackground(self,shift):
        try:
            for y in range(0, len(self.background)):
                for x in range(0 - int(shift + 1), 20 - int(shift - 1)):
                    if self.background[y][x] is not None:
                        self.background[y][x].draw(x + shift,self.screen)
        except IndexError:
            return

    def drawGround(self,shift):
        try:
            for y in range(0, len(self.ground)):
                for x in range(0 - int(shift + 1), 20 - int(shift - 1)):
                    if self.ground[y][x] is not None:
                        if not self.ground[y][x].alive:
                            self.ground[y][x] = None
                        else:
                            self.ground[y][x].draw(x + shift,self.screen)
        except IndexError:
            return

    def drawTop(self,shift):
        try:
            for y in range(0, len(self.top)):
                for x in range(0 - int(shift + 1), 20 - int(shift - 1)):
                    if self.top[y][x] is not None:
                        self.top[y][x].draw(x + shift,self.screen)
        except IndexError:
            return

    def nextLevel(self,worldPipe=None):
        '''goes to the next level if current level is beaten'''
        if not self.campaign:
            self.mario.restart = True
            return
        if worldPipe is not None:
            world = worldPipe.world
            level = "1"
        else:
            if self.level == "4":
                world = str(int(self.world)+1)
                level = "1"
            else:
                world = self.world
                level = str(int(self.level)+1)
            if self.world == "9":
                self.mario.restart = True
                return
        try:
            file = open("./levels/{}/level{}.json".format(world,level))
            file.close()
        except:
            self.mario.restart = True
            return
        self.pastPowerUpState = self.mario.powerUpState
        self.mario = ""
        self.camera = ""
        self.zones = []
        self.sky = []
        self.background = []
        self.ground = []
        self.top = []
        self.entities = pygame.sprite.Group()
        self.updateSave(world)
        self.world = world
        self.level = level
        levelname = "{}-{}".format(self.world,self.level)
        self.loadLevel(levelname)

    def savedPrincess(self):
        self.mario.restart = True
        if self.version == 1:
            world = self.world
            self.updateSave(world,True)
            self.mario.restart = True

    def updateSave(self,world,completed=False):
        with open("./saveData.json","r") as jsonData:
            data = json.load(jsonData)
        levelname = "{}-{}".format(self.world,self.level)
        if levelname not in data["completedLevels"]:
            data["completedLevels"].append(levelname)
        data["completedLevels"].sort()
        if completed:
            data["allowVersion2"] = True
        if world != self.world:
            data["currentWorld"] = world
        with open("./saveData.json","w") as jsonData:
            json.dump(data,jsonData)