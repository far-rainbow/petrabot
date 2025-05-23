''' img lib class '''
import io
import sys
import time
import asyncio
import hashlib
import glob
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
import numpy
import cv2
import audio
import concurrent.futures

class Img():
    '''
    This class is an images lib + some public stuff...
    '''
    MAX_HEIGHT = 1080
    MAX_WIDTH = 1920
    SQUARE_MAX_HEIGHT = 1080
    SQUARE_MAX_WIDTH = 1080
    FRAME_DIR = "frames/"
    TEXT_MAIN_FONT = "fonts/BalsamiqSans-Bold.ttf"
    TEXT_SPLASH_FONT = "fonts/Lobster-Regular.ttf"
    TEXT_FONT_SIZE = 80
    TEXT_FONT_SIZE_FALLBACK_1 = 70
    TEXT_FONT_SIZE_FALLBACK_2 = 60
    TEXT_FONT_SIZE_FALLBACK_3 = 50
    TEXT_FONT_SIZE_SPLASH = 40
    TEXT_BANKNAME = {'main':'@gratiavulgaris', 'test':'@gratiavulgaris'}
    TEXT_SHADOW_BLUR = 20
    W_OFFSET = 32
    W_OFFSET_SHADOW = 40
    H_OFFSET_SHADOW = 16
    W_SPLASH_OFFSET_SHADOW = 4
    H_SPLASH_OFFSET_SHADOW = 4
    TEXT_START_V_POS = 32
    TEXT_MAX_CHARS_PER_LINE = 30
    TEXT_COLOR = 'white'
    TEXT_SHADOW_COLOR = 'black'
    TEXT_STROKE_COLOR = 'chocolate'
    TEXT_COLOR_FULL_TRANSPARENT = (0, 0, 0, 0)
    TEXT_STROKE_WIDTH = 2
    MAIN_BLUR = 16
    INSTA_BLUR = 1

    def __init__(self, VIDEO_PATH, AUDIO_PATH, *args):
        self.VIDEO_PATH = VIDEO_PATH
        self.AUDIO_PATH = AUDIO_PATH
        self.last_three_pics_name = [1, 2, 3]
        self.pics = {}
        self.pics['main'] = self._load_all_pics(args[0],
                                                self.MAX_WIDTH, self.MAX_HEIGHT)
        self.pics['test'] = self._load_all_pics(args[1],
                                                self.SQUARE_MAX_WIDTH,
                                                self.SQUARE_MAX_HEIGHT)
        self.font = ImageFont.truetype(self.TEXT_MAIN_FONT, self.TEXT_FONT_SIZE)
        self.font_fallback_1 = ImageFont.truetype(self.TEXT_MAIN_FONT,
                                                  self.TEXT_FONT_SIZE_FALLBACK_1)
        self.font_fallback_2 = ImageFont.truetype(self.TEXT_MAIN_FONT,
                                                  self.TEXT_FONT_SIZE_FALLBACK_2)
        self.font_fallback_3 = ImageFont.truetype(self.TEXT_MAIN_FONT,
                                                  self.TEXT_FONT_SIZE_FALLBACK_3)
        self.font_splash = ImageFont.truetype(self.TEXT_SPLASH_FONT, self.TEXT_FONT_SIZE_SPLASH)
    @staticmethod
    def chunklist(long_list, size_of_chunk):
        ''' ГЕНЕРАТОР -- разбить список на список списков длинной size_of_chunk '''
        for i in range(0, len(long_list), size_of_chunk):
            yield long_list[i:i + size_of_chunk]
    @staticmethod
    def _load_all_pics(path, max_width, max_height):
        '''
        preload all images with on-fly resizing to global width/height attrs
        :param path: dir path to fetch pics from
        :returns: a list with Image object loaded from path dir
        '''
        pic_pathes = glob.glob(path + '*.jpg')+glob.glob(path + '*.png')+glob.glob(path + '*.webp')
        pics = []
        for _ in pic_pathes:
            ratio = 1
            img = Image.open(_)
            filename = img.filename
            print(f'{img.filename} {img.size} {img.format} loaded...')
            # explicit is better than implicit
            if img.height > max_height or img.width > max_width:
                height_ratio = 1 / (img.height / max_height)
                width_ratio = 1 / (img.width / max_width)
                ratio = min(height_ratio, width_ratio)
            elif img.height < max_height or img.width < max_width:
                height_ratio = max_height / img.height
                width_ratio = max_width / img.width
                ratio = max(height_ratio, width_ratio)
            if ratio != 1:
                img = img.resize(size=(int(img.width * ratio), int(img.height * ratio)))
                print(f'Resized with {ratio} ratio. New size is {img.size}')
            img.filename = filename
            pics.append(img)
        print(f'{len(pics)} pics loaded...')
        return pics

    @staticmethod
    def get_bytes_jpeg(img, qlty=75):
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
        choose random Image object from all the banks
        :returns: Image object
        '''
        pic_name = None
        while 1:
            img = {}
            for img_k, img_v in self.pics.items():
                img[img_k] = random.choice(img_v)
            img_k = random.choice(list(img.keys()))
            img = img[img_k]
            img.bankname = img_k
            pic_name = img.filename
            if pic_name not in self.last_three_pics_name:
                self.last_three_pics_name.append(pic_name)
                del self.last_three_pics_name[0]
                break
        return img
    
    def get_image_with_text(self,
                                  text,
                                  img_rgb,
                                  splash=True,
                                  bg_blur=None,
                                  shadow_blur=TEXT_SHADOW_BLUR,
                                  stroke_color=TEXT_STROKE_COLOR,
                                  bounce=False,
                                  bounce_k=1.0):
        '''
        render one frame with predef background
        :param text: str to render
        :param img_rgb Image background
        :param splash: True=on,False=off
        :param shadow_blur: shadow blur strength
        :param stroke_color: stroke color (R, G, B) or ImageColor.colormap key
        :returns: Image object
        '''
        print(f'{bounce_k=}')
        if img_rgb.bankname == 'main':
            imgbankname = 'main'
            if bg_blur is None:
                bg_blur = self.MAIN_BLUR
            img_rgb = img_rgb.filter(ImageFilter.GaussianBlur(bg_blur))
        else:
            imgbankname = 'test'
            if bg_blur is None:
                bg_blur = self.INSTA_BLUR
            img_rgb = img_rgb.filter(ImageFilter.GaussianBlur(bg_blur))
            
        text_rgb = Image.new(mode='RGBA', size=(self.SQUARE_MAX_WIDTH, self.SQUARE_MAX_HEIGHT),
                             color=self.TEXT_COLOR_FULL_TRANSPARENT)
        text_shadow = Image.new(mode='RGBA', size=(self.SQUARE_MAX_WIDTH, self.SQUARE_MAX_HEIGHT),
                                color=self.TEXT_COLOR_FULL_TRANSPARENT)
        draw_rgb = ImageDraw.Draw(text_rgb)
        draw_shadow = ImageDraw.Draw(text_shadow)
        if splash:
            text_splash_shadow = Image.new(mode='RGBA',
                                           size=(self.SQUARE_MAX_WIDTH,
                                                 self.SQUARE_MAX_HEIGHT),
                                           color=self.TEXT_COLOR_FULL_TRANSPARENT)
            draw_splash_shadow = ImageDraw.Draw(text_splash_shadow)
            line = self.TEXT_BANKNAME[imgbankname]
            font_width, font_height = self.font_splash.getsize(line)
            draw_splash_shadow.text(
                (self.SQUARE_MAX_WIDTH - font_width - self.W_OFFSET + self.W_SPLASH_OFFSET_SHADOW,
                 self.SQUARE_MAX_HEIGHT - font_height - self.W_OFFSET + self.H_SPLASH_OFFSET_SHADOW),
                line, fill=self.TEXT_SHADOW_COLOR,
                font=self.font_splash)
            draw_rgb.text(
                (self.SQUARE_MAX_WIDTH - font_width - self.W_OFFSET,
                 self.SQUARE_MAX_HEIGHT - font_height - self.W_OFFSET),
                line, fill=self.TEXT_COLOR,
                font=self.font_splash)
            # shadow_blur shadow layer
            text_splash_shadow = text_splash_shadow.filter(ImageFilter.GaussianBlur(self.TEXT_SHADOW_BLUR))
            # paste shadow layer
            img_rgb.paste(text_splash_shadow, (0, 0), text_splash_shadow)
            # paste rgb layer
            img_rgb.paste(text_rgb, (0, 0), text_rgb)      
        # split text
        text_utf8 = text.decode('utf-8').split('--', maxsplit=1)
        if len(text_utf8) > 1:
            text = text_utf8[0]+('\n--'+text_utf8[1])
        else:
            text = text_utf8[0]
        text_lines = textwrap.wrap(text, width=self.TEXT_MAX_CHARS_PER_LINE)
        # render lines
        v_position = self.TEXT_START_V_POS
        for line in text_lines:
            font_line = self.font
            font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - self.W_OFFSET_SHADOW:
                font_line = self.font_fallback_1
                font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - self.W_OFFSET_SHADOW:
                font_line = self.font_fallback_2
                font_width, font_height = font_line.getsize(line)
            # draw text line shadow
            draw_shadow.text((self.W_OFFSET_SHADOW, v_position+self.H_OFFSET_SHADOW),
                             line, fill=self.TEXT_SHADOW_COLOR,
                             font=font_line, stroke_width=self.TEXT_STROKE_WIDTH,
                             stroke_fill=self.TEXT_SHADOW_COLOR)
            # draw text line
            draw_rgb.text((self.W_OFFSET, v_position),
                          line, fill=self.TEXT_COLOR,
                          font=font_line, stroke_width=self.TEXT_STROKE_WIDTH,
                          stroke_fill=stroke_color)
            # carriage return
            v_position += font_height
        # shadow_blur shadow layer
        text_shadow = text_shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        # centring the layers via text height
        h_center = (self.SQUARE_MAX_HEIGHT - self.TEXT_START_V_POS - v_position)//2
        # paste shadow layer
        img_rgb.paste(text_shadow, (0, h_center),
                      text_shadow)
        # paste rgb layer
        pre_width, pre_height = (0, 0)
        post_width, post_height = (0, 0)
        if bounce:
                pre_width, pre_height = text_rgb.size
                print(f'Pre-zoom {pre_width} / {pre_height}')
                text_rgb = text_rgb.resize((int(pre_width*bounce_k),
                                int(pre_height*bounce_k)),
                                Image.LANCZOS)
                post_width, post_height = text_rgb.size
                print(f'Post-zoom {post_width} / {post_height}')
        img_rgb.paste(text_rgb, (-(post_width-pre_width)//2,
                                 h_center - (post_height-pre_height)//2),
                                 text_rgb)
        # crop
        img_rgb = img_rgb.crop((0, 0, self.SQUARE_MAX_WIDTH,
                                self.SQUARE_MAX_HEIGHT))
        return img_rgb

    async def get_random_image_with_text(self, text, splash=True, shadow_offset=None):
        '''
        Get random image from pics list, draw a text on it, convert it to JPEG
            and return a byte array of it to caller (send to Telegram API srv)
        :param text: string to draw on image
        :returns: byte array of random image from pics list with text added
        '''
        if shadow_offset is not None:
            W_OFFSET_SHADOW = shadow_offset
            H_OFFSET_SHADOW = shadow_offset
        else:
            W_OFFSET_SHADOW = self.W_OFFSET_SHADOW
            H_OFFSET_SHADOW = self.H_OFFSET_SHADOW
        img_rgb = await self._get_random_image()
        if img_rgb.bankname == 'main':
            imgbankname = 'main'
            img_rgb = img_rgb.filter(ImageFilter.GaussianBlur(self.MAIN_BLUR))
        else:
            imgbankname = 'test'
            img_rgb = img_rgb.filter(ImageFilter.GaussianBlur(self.INSTA_BLUR))
        text_rgb = Image.new(mode='RGBA', size=(self.SQUARE_MAX_WIDTH, self.SQUARE_MAX_HEIGHT),
                             color=self.TEXT_COLOR_FULL_TRANSPARENT)
        text_shadow = Image.new(mode='RGBA', size=(self.SQUARE_MAX_WIDTH, self.SQUARE_MAX_HEIGHT),
                                color=self.TEXT_COLOR_FULL_TRANSPARENT)
        draw_rgb = ImageDraw.Draw(text_rgb)
        draw_shadow = ImageDraw.Draw(text_shadow)
        if splash:
            text_splash_shadow = Image.new(mode='RGBA',
                                           size=(self.SQUARE_MAX_WIDTH,
                                                 self.SQUARE_MAX_HEIGHT),
                                           color=self.TEXT_COLOR_FULL_TRANSPARENT)
            draw_splash_shadow = ImageDraw.Draw(text_splash_shadow)
            line = self.TEXT_BANKNAME[imgbankname]
            font_width, font_height = self.font_splash.getsize(line)
            draw_splash_shadow.text(
                (self.SQUARE_MAX_WIDTH - font_width - self.W_OFFSET + self.W_SPLASH_OFFSET_SHADOW,
                 self.SQUARE_MAX_HEIGHT - font_height - self.W_OFFSET + self.H_SPLASH_OFFSET_SHADOW),
                line, fill=self.TEXT_SHADOW_COLOR,
                font=self.font_splash)
            draw_rgb.text(
                (self.SQUARE_MAX_WIDTH - font_width - self.W_OFFSET,
                 self.SQUARE_MAX_HEIGHT - font_height - self.W_OFFSET),
                line, fill=self.TEXT_COLOR,
                font=self.font_splash)
            # blur shadow layer
            text_splash_shadow = text_splash_shadow.filter(ImageFilter.GaussianBlur(self.TEXT_SHADOW_BLUR))
            # paste shadow layer
            img_rgb.paste(text_splash_shadow, (0, 0), text_splash_shadow)
            # paste rgb layer
            img_rgb.paste(text_rgb, (0, 0), text_rgb)
        text_utf8 = text.decode('utf-8').split('--', maxsplit=1)
        if len(text_utf8) > 1:
            #text_body_wraped = ''
            #text_body = text_utf8[0].split('\n')
            #for line in text_body:
            #    if len(line)>self.TEXT_MAX_CHARS_PER_LINE:
            #        w = textwrap.TextWrapper(width=self.TEXT_MAX_CHARS_PER_LINE, break_long_words=True)
            #        line = '\n'.join(w.wrap(line))
            #    text_body_wraped += line + '\n'
            #text = text_body_wraped+('\n--'+text_utf8[1])
            text = text_utf8[0]+'\n--'+text_utf8[1]
        else:
            #text_body_wraped = ''
            #text = text_utf8[0]
            #text_body = text_utf8[0].split('\n')
            #for line in text_body:
            #    if len(line)>self.TEXT_MAX_CHARS_PER_LINE:
            #        w = textwrap.TextWrapper(width=self.TEXT_MAX_CHARS_PER_LINE, break_long_words=True)
            #        line = '\n'.join(w.wrap(line))
            #    text_body_wraped += line + '\n'
            #text = text_body_wraped
            text = text_utf8[0]
        text_lines = textwrap.wrap(text, width=self.TEXT_MAX_CHARS_PER_LINE, replace_whitespace=False)
        #text_lines = text.split('\n')
        print(f'TL: {text_lines}')
        v_position = self.TEXT_START_V_POS
        for line in text_lines:
            font_line = self.font
            if '\n' in line:
                font_width, font_height = font_line.getsize(line)
                font_height = font_height*2
            else:
                font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - W_OFFSET_SHADOW:
                font_line = self.font_fallback_1
                if '\n' in line:
                    font_width, font_height = font_line.getsize(line)
                    font_height = font_height*2
                else:
                    font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - W_OFFSET_SHADOW:
                font_line = self.font_fallback_2
                if '\n' in line:
                    font_width, font_height = font_line.getsize(line)
                    font_height = font_height*2
                else:
                    font_width, font_height = font_line.getsize(line)
            if font_width > self.SQUARE_MAX_WIDTH - W_OFFSET_SHADOW:
                font_line = self.font_fallback_3
                if '\n' in line:
                    font_width, font_height = font_line.getsize(line)
                    font_height = font_height*3
                else:
                    font_width, font_height = font_line.getsize(line)
            # draw text line shadow
            draw_shadow.text((W_OFFSET_SHADOW, v_position+H_OFFSET_SHADOW),
                             line, fill=self.TEXT_SHADOW_COLOR,
                             font=font_line, stroke_width=self.TEXT_STROKE_WIDTH,
                             stroke_fill=self.TEXT_SHADOW_COLOR)
            # draw text line
            draw_rgb.text((self.W_OFFSET, v_position),
                          line, fill=self.TEXT_COLOR,
                          font=font_line, stroke_width=self.TEXT_STROKE_WIDTH,
                          stroke_fill=self.TEXT_STROKE_COLOR)
            # carriage return
            v_position += font_height
        # blur shadow layer
        text_shadow = text_shadow.filter(ImageFilter.GaussianBlur(self.TEXT_SHADOW_BLUR))
        # centring the layers via text height
        center = (self.SQUARE_MAX_HEIGHT - self.TEXT_START_V_POS - v_position)//2
        # paste shadow layer
        img_rgb.paste(text_shadow, (0, center),
                      text_shadow)
        # paste rgb layer
        img_rgb.paste(text_rgb, (0, center),
                      text_rgb)
        # crop
        img_rgb = img_rgb.crop((0, 0, self.SQUARE_MAX_WIDTH,
                                self.SQUARE_MAX_HEIGHT))
        return self.get_bytes_jpeg(img_rgb)

    async def get_random_video_with_text(self, text, splash=True, frames_num=25,
                                         framerate=25, repeats=1, blur_max = 30,
                                         rainbow=False, flashing=False, audiofile='',
                                         bounce=False,
                                         bounce_k=1.0,THREADNUM=2):
        '''
        :returns: video file -- random background with text and audio
        '''
        # one frame delta for each frame to reach full blur at the end of the range
        # TODO: zero blur 
        blur_coef = frames_num/blur_max
        # get random background
        img_rgb = await self._get_random_image()
        # tmp file name
        videofile_random_name = hashlib.md5(str(random.randrange(100000000,999999999)).encode('utf-8'))
        videofile_random_name = videofile_random_name.hexdigest()+f"{time.time()}.mp4"
        # full tmp file path
        tmp_video_name = self.VIDEO_PATH+videofile_random_name
        images = [None] * frames_num
        frame_chunks = self.chunklist([*range(frames_num)],THREADNUM)
        for frameblock in frame_chunks:
            # info log
            # TODO: print thread/user info
            print(f'Frames {frameblock} queued for render')
            # change color every N-th frame if rainbow stroke is ON
            # TODO: N-th frame delay, now it us every frame color change (too fast)
            if rainbow:
                stroke_color = random.choice(list(ImageColor.colormap.values()))
            else:
                stroke_color = self.TEXT_STROKE_COLOR
            # render frames
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADNUM) as pool:
                # why numpy but custom simple equation? coz there is a much numpy tasks in future versions...
                frame_k = numpy.linspace(1,bounce_k,frames_num)
                future_to_image = {pool.submit(self.get_image_with_text,
                                               text,
                                               img_rgb,
                                               splash=splash,
                                               bg_blur=frame//(blur_coef*2),
                                               shadow_blur=frame//blur_coef,
                                               stroke_color=stroke_color,
                                               bounce=bounce,
                                               bounce_k = frame_k[frame]): frame for frame in frameblock}
                for future in concurrent.futures.as_completed(future_to_image):
                    images[future_to_image[future]] = (future.result())
                    sys.stdout.flush()
        print(f'{images=}')
        sys.stdout.flush()
        # render video
        # TODO: move out into static method, args, video mode switch
        video = cv2.VideoWriter(tmp_video_name, cv2.VideoWriter_fourcc(*'mp4v'), framerate,
                                (self.SQUARE_MAX_WIDTH, self.SQUARE_MAX_HEIGHT))
        for _ in range(repeats):
            for image in reversed(images):
                image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
                video.write(image)
            for image in images:
                image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
                video.write(image)
        # write video
        video.release()
        # add audio into video (ffmpeg coz cv2 has no audio concat)
        tmp_video_name = audio.add_mp3_to_video(videofile_random_name,
                                               audiofile,
                                               self.VIDEO_PATH,
                                               self.AUDIO_PATH)
        # info log
        # TODO: print thread/user info
        print(f'Video rendered: {tmp_video_name}')
        return open(tmp_video_name, 'rb')
