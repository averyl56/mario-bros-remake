from pygame import Rect

class Zone():
    def __init__(self,name,x,y,width,height,theme,music):
        self.name = name
        self.x = x
        self.y = y
        self.x1 = x+width
        self.y1 = y+height
        self.theme = theme
        self.music = music

    def entInZone(self,entity):
        return self.x <= entity.getPosIndexAsFloat().x*32 <= self.x1 and self.y <= entity.getPosIndexAsFloat().y*32 <= self.y1

    def inZone(self,x,y):
        return self.x <= x <= self.x1 and self.y <= y <= self.y1

    def __eq__(self,zone):
        if isinstance(zone,Zone):
            return self.name == zone.name
        return False
