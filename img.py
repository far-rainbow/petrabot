import glob
import random
from PIL import Image,ImageDraw

class Img():

    def __init__(self,path):
        self.pics = []
        self.pics = self.loadAllPics(path)
    
    def loadAllPics(self,path):
        picPathes = glob.glob(path+'*.jpg') + glob.glob(path+'*.png')
        pics = []
        for _ in picPathes:
            pics.append(Image.open(_))
            print(f'{pics[-1].filename} {pics[-1].size} {pics[-1].format} loaded...')
        print(f'{len(pics)} pics loaded...')
        return pics
    
    async def getRandomImage(self):
        return random.choice(self.pics)