import io
import glob
import random
import textwrap
from PIL import Image,ImageDraw,ImageFont
from copy import deepcopy

class Img():
    
    MAX_HEIGHT = 1080
    MAX_WIDTH = 1920
    TEXT_FONT_SIZE = 80
    TEXT_START_V_POS = 32
    TEXT_MAX_CHARS_PER_LINE = 30
    TEXT_STROKE_COLOR = 'black'
    TEXT_STROKE_WIDTH = 2

    def __init__(self,path):
        self.pics = self.loadAllPics(path)
        self.font = ImageFont.truetype("Lobster-Regular.ttf", self.TEXT_FONT_SIZE)
    
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
        return deepcopy(random.choice(self.pics))

    async def getRandomImageWithText(self,text):
        imgRGB = await self.getRandomImage()
        draw = ImageDraw.Draw(imgRGB)
        text_lines = textwrap.wrap(text.decode('utf-8'),self.TEXT_MAX_CHARS_PER_LINE)
        v_pos = self.TEXT_START_V_POS
        for line in text_lines:
            font_width,font_height = self.font.getsize(line)
            draw.text((32,v_pos),line,(255,255,255),font=self.font,stroke_width=self.TEXT_STROKE_WIDTH, stroke_fill=self.TEXT_STROKE_COLOR)
            v_pos += font_height
        return self.getBytes(imgRGB,qlty=60)