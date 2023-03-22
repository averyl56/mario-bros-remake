'''loads image files with all sprites and stores it'''
from pygame.constants import RLEACCEL
from defaults import colorkey,scale
import pygame
import json

class Spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename)
            if not self.sheet.get_alpha():
                self.sheet.set_colorkey((0, 0, 0))
        except pygame.error:
            print("Unable to load spritesheet image:", filename)
            raise SystemExit

    def image_at(self, x, y, scalingfactor, colorkey=None, ignoreTileSize=False,
                 xTileSize=16, yTileSize=16):
        if ignoreTileSize:
            rect = pygame.Rect((x, y, xTileSize, yTileSize))
        else:
            rect = pygame.Rect((x * xTileSize, y * yTileSize, xTileSize, yTileSize))
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return pygame.transform.scale(
            image, (xTileSize * scalingfactor, yTileSize * scalingfactor)
        )

class Tilesheet():
    def __init__(self):
        self.sheet = pygame.image.load("./textures/tiles.png")
        tile_num_x = int(self.sheet.get_size()[0]/16)
        tile_num_y = int (self.sheet.get_size()[1]/16)
        self.cut_tiles = []
        for row in range(tile_num_y):
            for col in range(tile_num_x):
                x = col * 16
                y = row * 16
                surf = pygame.Surface((16,16))
                surf.blit(self.sheet,(0,0),pygame.Rect(x,y,16,16))
                surf.set_colorkey(colorkey, RLEACCEL)
                self.cut_tiles.append(surf)
    
    def get(self,id):
        return self.cut_tiles[id]

class Itemsheet():
    def __init__(self):
        with open("./sprites/items.json","r") as file:
            data = json.load(file)
            self.sheet = pygame.image.load(data["spriteSheetURL"])
            self.scale = data["size"]
            self.jump = data["varJump"]
            points = data["sprites"]
        self.sprites = {}
        for sprite in points:
            self.sprites[sprite["name"]] = []
            scaleBy = self.scale[sprite["scale"]]
            for i in range(sprite["vars"]):
                x = sprite["x"]*scaleBy + i*self.jump
                y = sprite["y"]*scaleBy
                width = sprite["width"]*scaleBy
                height = sprite["height"]*scaleBy
                surf = pygame.Surface((width,height))
                surf.blit(self.sheet,(0,0),pygame.Rect(x,y,width,height))
                surf = pygame.transform.scale(surf,((width/16)*scale,(height/16)*scale))
                surf.set_colorkey(colorkey, RLEACCEL)
                self.sprites[sprite["name"]].append(surf)
            
    def get(self,name,var=0):
        sprite = self.sprites[name]
        if len(sprite)-1 < var:
            tile = sprite[0]
        else:
            tile = sprite[var]
        return tile

class MobSheet():
    def __init__(self):
        with open("./sprites/enemies.json","r") as file:
            data = json.load(file)
            self.sheet = pygame.image.load(data["spriteSheetURL"])
            scaleBy = data["size"]
            points = data["sprites"]
            self.sprites = {}
            for sprite in points:
                if sprite["name"] not in self.sprites.keys():
                    self.sprites[sprite["name"]] = []
                x = sprite["x"]*scaleBy
                y = sprite["y"]*scaleBy
                width = sprite["width"]*scaleBy
                height = sprite["height"]*scaleBy
                surf = pygame.Surface((width,height))
                surf.blit(self.sheet,(0,0),pygame.Rect(x,y,width,height))
                newWidth = (width/16)*scale
                newHeight = (height/16)*scale
                surf = pygame.transform.scale(surf,(newWidth,newHeight))
                surf.set_colorkey(colorkey, RLEACCEL)
                self.sprites[sprite["name"]].append(surf)
 
    def get(self,name,var=0):
        sprite = self.sprites[name]
        if len(sprite)-1 < var:
            tile = sprite[0]
        else:
            tile = sprite[var]
        return tile

class PlayerSheet():
    def __init__(self):
        with open("./sprites/player.json","r") as file:
            data = json.load(file)
            self.sheet = pygame.image.load(data["spriteSheetURL"])
            size = data["size"]
            points = data["sprites"]
        self.sprites = {}
        for sprite in points:
            name = sprite["name"]
            x = sprite["x"]*size
            y = sprite["y"]*size
            width = sprite["width"]*size
            height = sprite["height"]*size
            surf = pygame.Surface((width,height))
            surf.blit(self.sheet,(0,0),pygame.Rect(x,y,width,height))
            newWidth = (width/16)*scale
            newHeight = (height/16)*scale
            surf = pygame.transform.scale(surf,(newWidth,newHeight))
            surf.set_colorkey(colorkey, RLEACCEL)
            self.sprites[name] = surf
    
    def get(self,name):
        return self.sprites[name]