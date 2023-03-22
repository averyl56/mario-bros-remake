''' Used to add in all entities to the level '''

from defaults import scale

class EntityAdder:
    def __init__(self,level):
        self.level = level
        self.scale = self.level.scale
        self.screen = self.level.screen
        self.sound = self.level.sound
        self.dashboard = self.level.dashboard
        self.methods = {"pipe":self.addPipe,"drop":self.addDrop,"bridge":self.addBridge,"brick":self.addBrick,"block":self.addBlock,"coin":self.addCoin,
            "goomba":self.addGoomba,"koopa":self.addKoopa,"cheep":self.addCheep,"beetle":self.addBeetle,"blooper":self.addBlooper,"vine":self.addVine,"finish":self.addFinish,
            "spiney":self.addSpiney,"lakitu":self.addLakitu,"gun":self.addBulletBill,"hammerBro":self.addHammerBro,"bowser":self.addBowser,"cheepSpawner":self.addCheepSpawner,
            "lava":self.addLava,"water":self.addWater,"dropPlatform":self.addDropPlatform,"movingPlatform":self.addMovingPlatform,"spring":self.addSpring,"start":self.addStart,
            "movingPlatformSpawner":self.addMovingPlatformSpawner,"platformBalance":self.addBalance,"fireBreath":self.addFireBreath,"fireBar":self.addFireBar,"gun":self.addGun,
            "axe":self.addAxe,"castleBridge":self.addAxeBridge,"worldPipe":self.addWorldPipe,"npc":self.addNPC,"skyPlatform":self.addSkyPlatform,"podoboo":self.addPodoboo,
            "flagpole":self.addFlagpole,"pit":self.addPit,"textbox":self.addTextBox,"bullet":self.addBulletBill}

    def calc(self,value,integer=True):
        '''rescales value to window size'''
        if integer:
            return (value//self.scale)*32
        else:
            return (value/self.scale)*32

    def getEntity(self,data):
        ''' retrieves specified entity from various methods thats called'''
        entity = self.methods[data["type"]](data)
        return entity
    
    def addStart(self,data):
        from entities.Mario import Mario
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        return Mario(x,y,self.level,self.screen,self.dashboard,self.sound,pastPowerUp=self.level.pastPowerUpState)

    def addFinish(self,data):
        from entities.LevelObjects import EndOfLevel
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        return EndOfLevel(x,y,self.sound)

    def addFlagpole(self,data):
        from entities.LevelObjects import FlagPole
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        height = self.calc(data["height"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return FlagPole(self.screen,x,y,height,variant,self.level,self.sound)

    def addPit(self,data):
        from entities.Objects import Pit
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        return Pit(x,y,width)

    def addTextBox(self,data):
        from entities.Particles import TextBox
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        text = ""
        visible = True
        try:
            for property in data["properties"]:
                if property["name"] == "line":
                    text = property["value"]
                elif property["name"] == "visible":
                    visible = property["value"]
        except:
            pass
        return TextBox(self.screen,self.dashboard,x,y,text,visible)
    
    def addBridge(self,data):
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        self.level.ground[y//32][x//32].passThrough = True

    def addPipe(self,data):
        from entities.LevelObjects import Pipe
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        name = data["name"]
        enemy = ""
        orientation = "down"
        goToPipe = ""
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "enemy":
                    enemy = property["value"]
                elif property["name"] == "direction":
                    orientation = property["value"]
                elif property["name"] == "goToPipe":
                    goToPipe = property["value"]
                elif property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Pipe(self.screen,x,y,name,self.level,orientation,self.sound,goToPipe,enemy,variant)

    def addBlock(self,data):
        from entities.Objects import ItemBlock
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        hidden = False
        item = "coin"
        hitsLeft = 1
        try:
            for property in data["properties"]:
                if property["name"] == "hidden":
                    hidden = property["value"]
                elif property["name"] == "hitsLeft":
                    hitsLeft = property["value"]
                elif property["name"] == "item":
                    item = property["value"]
                elif property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        tile = self.level.ground[y//32][x//32]
        return ItemBlock(self.screen,x,y,variant,self.sound,self.level,hidden,item,hitsLeft,tile)

    def addBrick(self,data):
        from entities.Objects import Brick
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        breakable = True
        item = ""
        hitsLeft = 1
        try:
            for property in data["properties"]:
                if property["name"] == "breakable":
                    breakable = property["value"]
                elif property["name"] == "hitsLeft":
                    hitsLeft = property["value"]
                elif property["name"] == "item":
                    item = property["value"]
                elif property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        tile = self.level.ground[y//32][x//32]
        return Brick(self.screen,x,y,variant,self.sound,self.level,breakable,item,hitsLeft,tile)

    def addCoin(self,data):
        from entities.PowerUps import Coin
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Coin(self.screen,x,y,variant,self.sound,self.dashboard)

    def addWater(self,data):
        from entities.Objects import Water
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        height = self.calc(data["height"])
        return Water(x,y,width,height)

    def addLava(self,data):
        from entities.Objects import Lava
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        return Lava(x,y,width)

    def addGoomba(self,data):
        from entities.Goomba import Goomba
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Goomba(self.screen,x,y,variant,self.level,self.sound)

    def addKoopa(self,data):
        from entities.Koopa import Koopa,GreenParatroopa,RedParatroopa
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        winged = False
        try:
            for property in data["properties"]:
                if property["name"] == "winged":
                    winged = property["value"]
                elif property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        if winged:
            if variant == 3:
                koopa = RedParatroopa(self.screen,x,y,self.level,self.sound)
                pass
            else:
                koopa = GreenParatroopa(self.screen,x,y,variant,self.level,self.sound)
                pass
        else:
            koopa = Koopa(self.screen,x,y,variant,self.level,self.sound)
        return koopa

    def addDrop(self,data):
        from entities.LevelObjects import Drop
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        height = self.calc(data["height"])
        name = data["name"]
        goToPipe = ""
        vine = False
        try:
            for property in data["properties"]:
                if property["name"] == "goToPipe":
                    goToPipe = property["value"]
                elif property["name"] == "vine":
                    vine = property["value"]
        except:
            pass
        return Drop(self.screen,x,y,width,height,name,self.level,goToPipe,vine)

    def addGun(self,data):
        from entities.Objects import Gun
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Gun(self.screen,x,y,variant,self.level)

    def addBulletBill(self,data):
        from entities.ObjectEnemies import BulletBill
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        direction = -1
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "direction":
                    direction = property["value"]
        except:
            pass
        return BulletBill(self.screen,x,y,variant,self.level,direction)

    def addCheep(self,data):
        from entities.OceanEnemies import Cheep
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        inWater = True
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "inWater":
                    inWater = property["value"]
        except:
            pass
        return Cheep(self.screen,x,y,variant,self.level)

    def addCheepSpawner(self,data):
        from entities.OceanEnemies import CheepSpawner
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        return CheepSpawner(self.screen,x,y,width,self.level)

    def addBeetle(self,data):
        from entities.Koopa import Beetle
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        onCeiling = False
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "onCeiling":
                    onCeiling = property["value"]
        except:
            pass
        return Beetle(self.screen,x,y,variant,self.level,self.sound)

    def addBlooper(self,data):
        from entities.OceanEnemies import Blooper
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Blooper(self.screen,x,y,variant,self.level)

    def addSpiney(self,data):
        from entities.Lakitu import Spiney
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        return Spiney(self.screen,x,y,self.level)

    def addLakitu(self,data):
        from entities.Lakitu import Lakitu
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Lakitu(self.screen,x,y,variant,self.level,self.sound)

    def addPodoboo(self,data):
        from entities.ObjectEnemies import Podoboo
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        jumpHeight = self.calc(176)
        try:
            for property in data["properties"]:
                if property["name"] == "jumpHeight":
                    jumpHeight = self.calc(property["value"])
        except:
            pass
        return Podoboo(self.screen,x,y,jumpHeight,self.level,self.sound)
        
    def addBowser(self,data):
        from entities.Bowser import Bowser
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        name = data["name"]
        variant = 0
        hard = False
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "hard":
                    hard = property["value"]
        except:
            pass
        return Bowser(self.screen,x,y,variant,name,self.level,self.sound,hard)

    def addHammerBro(self,data):
        from entities.HammerBro import HammerBro
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        jumpY = -1
        dropY = -1
        moving = True
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "jumpY":
                    jumpY = self.calc(property["value"])
                elif property["name"] == "dropY":
                    dropY = self.calc(property["value"])
                elif property["name"] == "moving":
                    moving = (property["value"])
        except:
            pass
        return HammerBro(self.screen,x,y,variant,self.level,self.sound,jumpY,dropY,moving)

    def addVine(self,data):
        from entities.PowerUps import Vine
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Vine(self.screen,x,y,variant,self.level,limit=5)

    def addDropPlatform(self,data):
        from entities.Platforms import DropPlatform
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        new = False
        try:
            for property in data["properties"]:
                if property["name"] == "new":
                    new = property["value"]
        except:
            pass
        return DropPlatform(self.screen,x,y,width,new)

    def addMovingPlatform(self,data):
        from entities.Platforms import MovingPlatform
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        x0 = x
        x1 = 0
        y0 = y
        y1 = 0
        xSpeed = 0
        ySpeed = 0
        new = False
        try:
            for property in data["properties"]:
                if property["name"] == "x0":
                    x0 = self.calc(property["value"])
                elif property["name"] == "y0":
                    y0 = self.calc(property["value"])
                elif property["name"] == "x1":
                    x1 = self.calc(property["value"])
                elif property["name"] == "y1":
                    y1 = self.calc(property["value"])
                elif property["name"] == "xSpeed":
                    xSpeed = property["value"]
                elif property["name"] == "ySpeed":
                    ySpeed = property["value"]
                elif property["name"] == "new":
                    new = property["value"]
        except:
            pass
        return MovingPlatform(self.screen,x,y,width,(x0,y0),(x1,y1),xSpeed,ySpeed,new)

    def addMovingPlatformSpawner(self,data):
        from entities.Platforms import MovingPlatformSpawner
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        interval = 100
        speed = 4
        endPath = -1
        new = False
        try:
            for property in data["properties"]:
                if property["name"] == "interval":
                    interval = property["value"]
                elif property["name"] == "ySpeed":
                    speed = property["value"]
                elif property["name"] == "endPath":
                    endPath = self.calc(property["value"])
                elif property["name"] == "new":
                    new = property["value"]
        except:
            pass
        return MovingPlatformSpawner(self.screen,x,y,width,self.level,speed,interval,endPath,new)

    def addSkyPlatform(self,data):
        from entities.Platforms import SkyPlatform
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        return SkyPlatform(self.screen,x,y,width)

    def addSpring(self,data):
        from entities.Objects import Spring
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        super = False
        variant = 0
        new = False
        try:
            for property in data["properties"]:
                if property["name"] == "super":
                    super = property["value"]
                elif property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "new":
                    new = property["value"]
        except:
            pass
        return Spring(self.screen,x,y,variant,super,new)

    def addFireBreath(self,data):
        from entities.Particles import FireBreath
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        return FireBreath(self.screen,x,y,self.sound)

    def addFireBar(self,data):
        from entities.Objects import FireBar
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        length = 6
        clockwise = False
        try:
            for property in data["properties"]:
                if property["name"] == "length":
                    length = property["value"]
                elif property["name"] == "clockwise":
                    clockwise = property["value"]
        except:
            pass
        return FireBar(self.screen,x,y,self.level,length,clockwise)

    def addBalance(self,data):
        from entities.Platforms import Balance
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        width = self.calc(data["width"])
        leftDown = scale*3
        rightDown = scale*5
        variant = 0
        new = False
        try:
            for property in data["properties"]:
                if property["name"] == "leftDown":
                    leftDown = property["value"]*scale
                elif property["name"] == "yDown":
                    rightDown = property["value"]*scale
                elif property["name"] == "variant":
                    variant = property["value"]
                elif property["name"] == "new":
                    new = property["value"]
        except:
            pass
        return Balance(self.screen,x,y,width,variant,leftDown,rightDown,self.level,new)

    def addAxe(self,data):
        from entities.LevelObjects import Axe
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        name = data["name"]
        variant = 0
        try:
            for property in data["properties"]:
                if property["name"] == "variant":
                    variant = property["value"]
        except:
            pass
        return Axe(self.screen,x,y,variant,name,self.level,self.sound)

    def addAxeBridge(self,data):
        from entities.LevelObjects import CastleBridge
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        name = data["name"]
        spot = 0
        try:
            for property in data["properties"]:
                if property["name"] == "order":
                    spot = property["value"]
        except:
            pass
        tile = self.level.ground[y//32][x//32]
        return CastleBridge(x,y,name,tile,spot)

    def addWorldPipe(self,data):
        from entities.LevelObjects import WorldPipe
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        world = 0
        try:
            for property in data["properties"]:
                if property["name"] == "world":
                    world = property["value"]
        except:
            pass
        return WorldPipe(self.screen,x,y,self.level,world,self.sound)

    def addNPC(self,data):
        from entities.LevelObjects import NPC
        x = self.calc(data["x"])
        y = self.calc(data["y"])
        name = data["name"]
        return NPC(self.screen,x,y,name,self.level,self.sound)