import io
import glob
import random
from PIL import Image,ImageDraw,ImageFont
from picture import Picture 

class Img():
    
    MAX_HEIGHT = 1080
    MAX_WIDTH = 1920

    def __init__(self,path):
        self.pics = self.loadAllPics(path)
        self.font = ImageFont.truetype("BadScript-Regular.ttf", 16)
    
    def loadAllPics(self,path):
        pic_pathes = glob.glob(path+'*.jpg') + glob.glob(path+'*.png')
        pics = list()
        for _ in pic_pathes:
            img = Picture()
            img = Image.open(_)
            print(f'{img.filename} {img.size} {img.format} loaded...')
            # TODO: combine ratios
            if img.height > self.MAX_HEIGHT:
                img.height_ratio = 1 / (img.height / self.MAX_HEIGHT)
                print(f'Too big height. Resize with height {img.height_ratio} ratio')
                img = img.resize(size=(int(img.width*img.height_ratio),int(img.height*img.height_ratio)))
            if img.width > self.MAX_WIDTH:
                ratio = 1 / (img.width / self.MAX_WIDTH)
                print(f'Too big width. Resize with width {ratio} ratio')
                img = img.resize(size=(int(img.width*ratio),int(img.height*ratio)))
            pics.append(img)
        print(f'{len(pics)} pics loaded...')
        return pics

    def getBytes(self,img,qlty=75):
        imgByteArr = io.BytesIO()
        imgRGB = img.convert(mode='RGB')
        imgRGB.save(imgByteArr, format='JPEG',quality=qlty)
        imgRGB = imgByteArr.getvalue()
        return imgRGB

    async def getRandomImage(self):
        return random.choice(self.pics)

    async def getRandomImageWithText(self,text):
        text = text.decode('utf-8')
        imgRGB = await self.getRandomImage()
        draw = ImageDraw.Draw(imgRGB)
        draw.text((0,0),text,(255,255,255),font=self.font)
        return self.getBytes(imgRGB,qlty=60)