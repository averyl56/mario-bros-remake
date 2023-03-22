
windowSizeX = 640 # default:640
windowSizeY = 480 # default:480
indexWidth = 20 # default:20
indexHeight = 15
scale = 32 # default:32, must be greater than 16 and even
colorkey = (24,255,255)

# screen width on 16x16 grid is 320, 
# perfect size for zones that dont move the camera

class Vector2D:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
