''' PetraBot Telegram bot logic '''
import os
import sys
import subprocess
from datetime import datetime, timezone
import telebot
import httpx
import itertools
import proxyscrape

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

ROOTDIR = os.path.dirname(os.path.abspath(__file__))
API_TOKEN = '1067546684:AAEyYPuY1m9cIQ7OMVux71rBy6mS6pC9EAg'
BOT = telebot.TeleBot(API_TOKEN)
PROXYNUM = 32

if sys.platform == 'win32':
    WIN32 = True
else:
    WIN32 = False

START_MESSAGE = '''
Hi there, I am Kamenka SU Bot.
I am here to enjoy you with some stuff.
Tap /help to get more info.'''

HELP_MESSAGE = '''
Commands:
/face -- get fake face
/fortune -- get random cookie text
Chat with BOT to get some contex fortunes...
'''

BASE = declarative_base()


class MessageRecord(BASE):
    ''' ORM '''
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    query = Column(String)
    answer = Column(String)
    time = Column(DateTime)


ENGINE = create_engine(f'sqlite:///petrabot.db', echo=False)
BASE.metadata.create_all(ENGINE)
SESSION = sessionmaker(bind=ENGINE)()

collector = proxyscrape.create_collector(
    'default', 'https', refresh_interval=10)


def get_proxy_scrape(num):
    ''' proxy scraper '''
    proxy = collector.get_proxies({'anonymous': True})
    proxy_dict = []
    for _ in proxy[:num]:
        proxy_item = {'http': 'http://' + _[0] + ':' + _[1]}
        proxy_dict.append(proxy_item)
    return proxy_dict


proxy_loop_iterator = itertools.cycle(get_proxy_scrape(PROXYNUM))


def push_to_db(message, answer=None):
    ''' save username,query and BOT answer (optionaly) into db '''
    print(message.from_user.username, ' : ', message.text)
    if answer is not None:
        print('Answer: ', answer.decode('utf-8'))
    mrec = MessageRecord(name=message.from_user.username, query=message.text,
                         answer=answer, time=datetime.now(timezone.utc))
    SESSION.add(mrec)
    SESSION.commit()


def finder(uid, cmd=''):
    ''' find fortune via shell subprocess script '''
    if not WIN32:
        try:
            fortune = subprocess.check_output(
                ['%s/finder.sh' % ROOTDIR, '%s' % uid, '%s' % cmd.lower()])
        except subprocess.SubprocessError:
            fortune = subprocess.check_output(
                ['/usr/games/fortune', '-a', '/usr/share/games/fortunes/'])
    else:
        fortune = b'This is Windows OS. No fortune found...'
    return fortune


def get_face():
    ''' html response getter '''
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; YandexMetrika/2.0; \
                +http://yandex.com/bots yabs01)'}
    proxy = next(proxy_loop_iterator, None)
    print(f'{proxy=}')
    with httpx.Client(proxies=proxy, headers=headers, timeout=10.0) as sess:
        return sess.get(url='https://thispersondoesnotexist.com/image').content


@BOT.message_handler(commands=['help', 'start', 'stop', 'face', 'fortune'])
def send_welcome(message):
    ''' BOT commands logic '''
    answer = None
    if message.text == '/start':
        BOT.reply_to(message, START_MESSAGE)
    elif message.text == '/help':
        BOT.reply_to(message, HELP_MESSAGE)
    elif message.text == '/stop':
        BOT.reply_to(message, 'Z-z-z-z...')
    elif message.text == '/face':
        BOT.send_photo(message.chat.id, get_face())
    elif message.text == '/fortune':
        answer = finder(message.from_user.username)
        BOT.reply_to(message, answer)
    push_to_db(message, answer)


@BOT.message_handler(func=lambda message: True)
def echo_message(message):
    ''' user text logic '''
    answer = finder(message.from_user.username, message.text)
    BOT.reply_to(message, answer)
    push_to_db(message, answer)


BOT.polling()
