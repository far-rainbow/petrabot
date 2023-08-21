''' PetraBot Telegram bot logic | v.2.1 [11.12.2021] '''
import os
import sys
import time
import subprocess
import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
import httpx

from dotenv import load_dotenv
from img import Img
import db

# debug info
print(f'Bot start: v.{time.time()}\n')

# get env vars
load_dotenv()

VERSION = '1.1'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = ROOT_DIR + '/img/'
IMG_PATH_SPEC = ROOT_DIR + '/tih/'
AUDIO_PATH = ROOT_DIR + '/audio/'
VIDEO_PATH = ROOT_DIR + '/frames/'
API_TOKEN = os.environ['API_TOKEN']
#GRP_TOKEN = os.environ['GRP_TOKEN']
PROXYNUM = 32
THREADNUM = 4
WIN32 = bool(sys.platform == 'win32')

START_MESSAGE = '''
Hi there, I am Kamenka SU Bot.
I am here to enjoy you with some stuff.
Tap /help to get more info.'''

HELP_MESSAGE = '''
Commands:
/face -- get fake face
/talk -- get random cookie text
Or just chat with BOT to get some fun...
'''

BOT = AsyncTeleBot(API_TOKEN)
SESSION = db.get_session('sqlite:///db/petrabot.db')
images = Img(VIDEO_PATH,AUDIO_PATH,IMG_PATH,IMG_PATH_SPEC)


def finder(uid, cmd=''):
    ''' find fortune via shell subprocess script '''
    if not WIN32:
        try:
            fortune = subprocess.check_output(
                ['%s/finder.sh' % ROOT_DIR, '%s' % uid, '%s' % cmd.lower()])
        except subprocess.SubprocessError:
            fortune = subprocess.check_output(
                ['/usr/games/fortune', 'ru', '/usr/share/games/fortunes/'])
    else:
        fortune = f'This is Windows OS.\nNo fortune found...\n{START_MESSAGE}'
    return fortune


async def get_face():
    ''' html response getter '''
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; YandexMetrika/2.0; \
                +http://yandex.com/bots yabs01)'}
    async with httpx.AsyncClient(http2=True, headers=headers, timeout=10.0) as sess:
        result = await sess.get(url='https://thispersondoesnotexist.com/image')
        return result.content


async def get_stats():
    ''' unused statistic method '''
    stats = '%s %s\n' % (sys.executable or sys.platform, sys.version)
    stats += f'unique users: {db.get_users_count(SESSION)}\n'
    #TODO: refact into sub stats cmd
    for name in db.get_user_names(SESSION):
        stats += f'{name[0]}\n'
    stats += f'VERSION: {VERSION}'
    return stats

@BOT.message_handler(commands=['help', 'start', 'stop', 'face', 'talk', 'stats', 'insta', 'instavideo'])
async def send_welcome(message):
    ''' BOT commands logic '''
    if message.chat.id > 0:
        custom_text = None
        answer = None
        cmd = message.text.split(' ')[0]
        try:
            arg = message.text.split(' ')[1]
            if arg == 'ct':
                custom_text = True
                words_list = message.text.split(' ')[2:]
                arg = ' '.join(_ for _ in words_list)
                print(f'CT: {arg}')
        except:
            arg = None
        if cmd == '/start':
            await BOT.reply_to(message, START_MESSAGE)
        elif cmd == '/help':
            await BOT.reply_to(message, HELP_MESSAGE)
        elif cmd == '/stop':
            await BOT.reply_to(message, 'Z-z-z-z...')
        elif cmd == '/face':
            await BOT.send_photo(message.chat.id, await get_face())
        elif cmd == '/talk':
            answer = finder(message.from_user.username)
            await BOT.reply_to(message, answer.decode('utf-8', 'ignore'))
        elif cmd == "/stats":
            answer = await get_stats()
            await BOT.reply_to(message, answer)
        elif cmd == "/insta":
            if arg is None:
                answer = finder(message.from_user.username)
            else:
                if custom_text is None:
                    answer = finder(message.from_user.username, arg)
                else:
                    answer = arg
            photo = await images.get_random_image_with_text(answer)
            await BOT.send_photo(message.chat.id, photo)
        elif cmd == "/instavideo":
            if arg is None:
                answer = finder(message.from_user.username)
            else:
                if custom_text is None:
                    answer = finder(message.from_user.username, arg)
                else:
                    answer = arg
            # bytes file
            video = await images.get_random_video_with_text(answer,
                                                      frames_num=30,
                                                      framerate=25,
                                                      repeats=30,
                                                      blur_max=30,
                                                      rainbow=False,
                                                      flashing=True,
                                                      audiofile='Dual_Crew_Shining_and_Desire.flac',
                                                      bounce=True,
                                                      bounce_k=1.025,
                                                      THREADNUM=THREADNUM)
            await BOT.send_video(message.chat.id, video)
            video.close()
        db.push_to_db(SESSION, message, answer)
        sys.stdout.flush()

@BOT.message_handler(func=lambda message: True)
async def echo_message(message):
    ''' user text logic '''
    if message.chat.id > 0:
        answer = finder(message.from_user.username, message.text)
        await BOT.reply_to(message, answer.decode('utf-8','ignore'))
        db.push_to_db(SESSION, message)

async def listener(messages):
    ''' service method for telebot class '''
    for msg in messages:
        print(str(msg))
BOT.set_update_listener(listener)
asyncio.run(BOT.polling())
