''' PetraBot Telegram bot logic | v.2 [18.06.2021] '''
import os
import sys
import subprocess
import asyncio
import telebot
import httpx

from dotenv import load_dotenv
from img import Img
import db

# get env vars
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = ROOT_DIR + '/img/'
IMG_PATH_SPEC = ROOT_DIR + '/tih/'
AUDIO_PATH = ROOT_DIR + '/audio/'
API_TOKEN = os.environ['API_TOKEN']
#GRP_TOKEN = os.environ['GRP_TOKEN']
PROXYNUM = 32
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

BOT = telebot.AsyncTeleBot(API_TOKEN)
SESSION = db.get_session('sqlite:///db/petrabot.db')
images = Img(IMG_PATH,IMG_PATH_SPEC)


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
        fortune = b'This is Windows OS. No fortune found...'
    return fortune


async def get_face():
    ''' html response getter '''
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; YandexMetrika/2.0; \
                +http://yandex.com/bots yabs01)'}
    async with httpx.AsyncClient(http2=True, headers=headers, timeout=10.0) as sess:
        result = await sess.get(url='https://thispersondoesnotexist.com/image')
        return result.content


def get_stats():
    ''' unused statistic method '''
    stats = bytes('%s %s\n' % (sys.executable or sys.platform, sys.version),'utf-8')
    stats += bytes(f'> unique users: {db.get_users_count(SESSION)}\n', 'utf-8')
    #TODO: refact into sub stats cmd
    for name in db.get_users_name(SESSION):
        stats += bytes(f'>>     {name[0]}\n','utf-8')
    return stats

@BOT.message_handler(commands=['help', 'start', 'stop', 'face', 'talk', 'stats', 'insta', 'instavideo'])
def send_welcome(message):
    ''' BOT commands logic '''
    if message.chat.id > 0:
        answer = None
        cmd = message.text.split(' ')[0]
        try:
            arg = message.text.split(' ')[1]
        except:
            arg = None
        if cmd == '/start':
            BOT.reply_to(message, START_MESSAGE)
        elif cmd == '/help':
            BOT.reply_to(message, HELP_MESSAGE)
        elif cmd == '/stop':
            BOT.reply_to(message, 'Z-z-z-z...')
        elif cmd == '/face':
            BOT.send_photo(message.chat.id, asyncio.run(get_face()))
        elif cmd == '/talk':
            answer = finder(message.from_user.username)
            BOT.reply_to(message, answer)
        elif cmd == "/stats":
            answer = get_stats()
            BOT.reply_to(message, answer)
        elif cmd == "/insta":
            if arg is None:
                answer = finder(message.from_user.username)
            else:
                answer = finder(message.from_user.username, arg)
            photo = asyncio.run(images.get_random_image_with_text(answer))
            BOT.send_photo(message.chat.id, photo)
        elif cmd == "/instavideo":
            if arg is None:
                answer = finder(message.from_user.username)
            else:
                answer = finder(message.from_user.username, arg)
            # bytes file
            video = asyncio.run(images.get_random_video_with_text(answer,
                                                                  frames_num=30,
                                                                  framerate=30,
                                                                  repeats=15,
                                                                  blur_max=30,
                                                                  rainbow=False,
                                                                  flashing=True,
                                                                  audio=AUDIO_PATH+'100ways.mp3'))
            BOT.send_video(message.chat.id, video)
            video.close
        db.push_to_db(SESSION, message, answer)


@BOT.message_handler(func=lambda message: True)
def echo_message(message):
    ''' user text logic '''
    if message.chat.id > 0:
        answer = finder(message.from_user.username, message.text)
        BOT.reply_to(message, answer)
        db.push_to_db(SESSION, message, answer)

def listener(messages):
    ''' service method for telebot class '''
    for msg in messages:
        print(str(msg))
BOT.set_update_listener(listener)
BOT.polling()
