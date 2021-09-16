''' img lib class '''
import io
import glob
import random
import logging
import textwrap
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class Img():
    '''
    This class is an images lib + some public stuff...
    '''
    MAX_HEIGHT = 1080
    MAX_WIDTH = 1920
    SQUARE_MAX_HEIGHT = 1080
    SQUARE_MAX_WIDTH = 1080
    
    TEXT_FONT_SIZE = 80
    TEXT_FONT_SIZE_FALLBACK_1 = 70
    TEXT_FONT_SIZE_FALLBACK_2 = 60
    H_OFFSET = 32
    H_OFFSET_SHADOW = 40
    
    TEXT_START_V_POS = 32
    TEXT_MAX_CHARS_PER_LINE = 30
    TEXT_STROKE_COLOR = 'black'
    TEXT_STROKE_WIDTH = 2
    INSTA_BLUR = 50

    def __init__(self, path):
        self.last_three_pics_name = [1,2,3]
        self.pics = self._load_all_pics(path)
        self.font = ImageFont.truetype("Lobster-Regular.ttf", self.TEXT_FONT_SIZE)
        self.font_fallback_1 = ImageFont.truetype("Lobster-Regular.ttf", self.TEXT_FONT_SIZE_FALLBACK_1)
        self.font_fallback_2 = ImageFont.truetype("Lobster-Regular.ttf", self.TEXT_FONT_SIZE_FALLBACK_2)
    def _load_all_pics(self, path):
        '''
        preload all images with onfly resizing to global width/height attrs
        :param dir path to fetch pics from
        :returns: a list with Image object loaded from path dir
        '''
        pic_pathes = glob.glob(path + '*.jpg') + glob.glob(path + '*.png') + glob.glob(path + '*.webp')
        pics = []
        for _ in pic_pathes:
            ratio = 1
            img = Image.open(_)
            filename = img.filename
            print(f'{img.filename} {img.size} {img.format} loaded...')
            # explicit is better than implicit
            if img.height > self.MAX_HEIGHT or img.width > self.MAX_WIDTH:
                height_ratio = 1 / (img.height / self.MAX_HEIGHT)
                width_ratio = 1 / (img.width / self.MAX_WIDTH)
                ratio = min(height_ratio, width_ratio)
            elif img.height < self.MAX_HEIGHT or img.width < self.MAX_WIDTH:
                height_ratio = self.MAX_HEIGHT / img.height
                width_ratio = self.MAX_WIDTH / img.width
                ratio = max(height_ratio, width_ratio)
            if ratio != 1:
                img = img.resize(size=(int(img.width * ratio), int(img.height * ratio)))
                print(f'Resized with {ratio} ratio. New size is {img.size}')
            img.filename = filename
            pics.append(img)
        print(f'{len(pics)} pics loaded...')
        return pics

    @staticmethod
    def get_bytes(img, qlty=75):
        '''
        convert Image into JPEG byte array
        :param img: Image obj to convert
        :param qlty: JPEG quality (default is 75)
        :returns: byte array of Image (Telegram API acceptable)
        '''
        img_byte_array = io.BytesIO()
        img_rgb = img.convert(mode='RGB')
        img_rgb.save(img_byte_array, format='JPEG', quality=qlty)
        img_rgb = img_byte_array.getvalue()
        return img_rgb

    async def _get_random_image(self):
        '''
        :returns: deep copy of Image object to prevent original object modification
        '''
        pic_name = None
        while pic_name in self.last_three_pics_name:
            img = random.choice(self.pics)
            pic_name = img.filename
        self.last_three_pics_name.append(pic_name)
        del self.last_three_pics_name[0]
        return deepcopy(random.choice(self.pics))

    async def get_random_image_with_text(self, text):
        '''
        Get random image from pics list, draw a text on it, convert it to JPEG
            and return a byte array of it to caller (send to Telegram API srv)
        :param text: string to draw on image
        :returns: byte array of random image from pics list with text added
        '''
        img_rgb = await self._get_random_image()
        img_rgb = img_rgb.filter(ImageFilter.GaussianBlur(self.INSTA_BLUR))
        text_rgb = Image.new(mode='RGBA', size=(self.SQUARE_MAX_WIDTH,self.SQUARE_MAX_HEIGHT), color=(0,0,0,0))
        draw = ImageDraw.Draw(text_rgb)
        text_utf8 = text.decode('utf-8').split('--',maxsplit=1)
        print(f'>>> {text_utf8}')
        if len(text_utf8) > 1:
            text = text_utf8[0]+'\n--'+text_utf8[1]
        else:
            text = text_utf8[0]
        text_lines = textwrap.wrap(text, width=self.TEXT_MAX_CHARS_PER_LINE)
        v_pos = self.TEXT_START_V_POS
        for line in text_lines:
            font_line = self.font
            font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - self.H_OFFSET_SHADOW:
                font_line = self.font_fallback_1
                font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - self.H_OFFSET_SHADOW:
                font_line = self.font_fallback_2
                font_width, font_height = font_line.getsize(line)
            # draw text line shadow
            draw.text((self.H_OFFSET_SHADOW, v_pos+10), line, (0, 0, 0),
                      font=font_line,stroke_width=self.TEXT_STROKE_WIDTH,
                      stroke_fill=self.TEXT_STROKE_COLOR)
            # draw text line
            draw.text((self.H_OFFSET, v_pos), line, (255, 255, 255),
                      font=font_line,stroke_width=self.TEXT_STROKE_WIDTH,
                      stroke_fill=self.TEXT_STROKE_COLOR)
            # carriage return
            v_pos += font_height
        img_rgb.paste(text_rgb,(0,0),text_rgb)
        img_rgb = img_rgb.crop((0,0,self.SQUARE_MAX_WIDTH,self.SQUARE_MAX_HEIGHT))
        return self.get_bytes(img_rgb)
