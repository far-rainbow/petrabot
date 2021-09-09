import io
import glob
import random
from PIL import Image,ImageDraw,ImageFont

class Img():
    
    MAX_HEIGHT = 1080
    MAX_WIDTH = 1920

    def __init__(self,path):
        self.pics = self.loadAllPics(path)
        self.font = ImageFont.truetype("BadScript-Regular.ttf", 40)
    
    def loadAllPics(self,path):
        pic_pathes = glob.glob(path+'*.jpg') + glob.glob(path+'*.png')
        pics = list()
        for _ in pic_pathes:
            ratio = None
            img = Image.open(_)
            print(f'{img.filename} {img.size} {img.format} loaded...')
            # explicit is better than implicit
            if img.height > self.MAX_HEIGHT or img.width > self.MAX_WIDTH:
                height_ratio = 1 / (img.height / self.MAX_HEIGHT)
                width_ratio = 1 / (img.width / self.MAX_WIDTH)
                ratio = min(height_ratio,width_ratio)
            elif img.height < self.MAX_HEIGHT or img.width < self.MAX_WIDTH:
                height_ratio = (self.MAX_HEIGHT / img.height)
                width_ratio = (self.MAX_WIDTH / img.width)
                ratio = min(height_ratio,width_ratio)
            if ratio:
                img = img.resize(size=(int(img.width*ratio),int(img.height*ratio)))
                print(f'Resized with {ratio} ratio. New size is {img.size}')
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