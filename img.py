import io
import glob
import random
from PIL import Image,ImageDraw
from astroid.__pkginfo__ import web
from rich import palette

class Img():
    
    MAX_HEIGHT = 1080
    MAX_WIDTH = 1920

    def __init__(self,path):
        self.pics = self.loadAllPics(path)
    
    def loadAllPics(self,path):
        pic_pathes = glob.glob(path+'*.jpg') + glob.glob(path+'*.png')
        pics = list()
        for _ in pic_pathes:
            imgByteArr = io.BytesIO()
            img = Image.open(_)
            print(f'{img.filename} {img.size} {img.format} loaded...')
            imgRGB = img.convert(mode='RGB')
            # TODO: combine ratios
            if imgRGB.height > self.MAX_HEIGHT:
                ratio = 1 / (imgRGB.height / self.MAX_HEIGHT)
                print(f'Too big height. Resize with height {ratio} ratio')
                imgRGB = imgRGB.resize(size=(int(imgRGB.width*ratio),int(imgRGB.height*ratio)))
            if imgRGB.width > self.MAX_WIDTH:
                ratio = 1 / (imgRGB.width / self.MAX_WIDTH)
                print(f'Too big width. Resize with width {ratio} ratio')
                imgRGB = imgRGB.resize(size=(int(imgRGB.width*ratio),int(imgRGB.height*ratio)))
            imgRGB.save(imgByteArr, format='JPEG')
            imgRGB = imgByteArr.getvalue()
            pics.append(imgRGB)
        print(f'{len(pics)} pics loaded...')
        return pics
    
    async def getRandomImage(self):
        return random.choice(self.pics)