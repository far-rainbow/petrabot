''' PetraBot Telegram bot logic | v.2 [18.06.2021] '''
import os
import sys
import subprocess
import asyncio
from datetime import datetime, timezone
#import itertools
import telebot
import httpx
#import proxyscrape

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from dotenv import load_dotenv
load_dotenv()

ROOTDIR = os.path.dirname(os.path.abspath(__file__))
API_TOKEN = os.environ['API_TOKEN']
#GRP_TOKEN = os.environ['GRP_TOKEN']
BOT = telebot.AsyncTeleBot(API_TOKEN)
PROXYNUM = 32
WIN32 = bool(sys.platform == 'win32')

START_MESSAGE = '''
Привет! Я робот Птица Говорун.
Напиши мне любое слово на любом языке,
и я поддержу беседу. Также ты можешь загадать
что-нибудь и написать мне какое-то слово, связанное
с тем что загадано. И я найду что-нибудь интересное
связанное с твоей загадкой или даже мечтой. Пиши!'''


BASE = declarative_base()


class MessageRecord(BASE):
    ''' ORM '''
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    query = Column(String)
    answer = Column(String)
    time = Column(DateTime)


ENGINE = create_engine(f'sqlite:///db/petrabot.db', echo=False)
BASE.metadata.create_all(ENGINE)
SESSION = sessionmaker(bind=ENGINE)()
#COLLECTOR = proxyscrape.create_collector(
#    'default', 'http')


#def get_proxy_scrape(num):
#    ''' proxy scraper '''
#    proxy = COLLECTOR.get_proxies()
#    print(proxy)
#    proxy_dict = []
#    for _ in proxy[:num]:
#        proxy_item = {'http://': 'http://' + _[0] + ':' + _[1]}
#        proxy_dict.append(proxy_item)
#    return proxy_dict


#PROXYLOOPITERATOR = itertools.cycle(get_proxy_scrape(PROXYNUM))


def push_to_db(message, answer=None):
    ''' save username,query and BOT answer (optionaly) into db '''
    print(message.from_user.username, ' : ', message.text)
    if answer is not None:
        print('Answer: ', answer.decode('utf-8'))
    mrec = MessageRecord(name=message.from_user.username, query=message.text,
                         answer=answer, time=datetime.now(timezone.utc))
    SESSION.add(mrec)
    SESSION.commit()
    sys.stdout.flush()


def finder(uid, cmd=''):
    ''' find fortune via shell subprocess script '''
    if not WIN32:
        try:
            fortune = subprocess.check_output(
                ['%s/finder.sh' % ROOTDIR, '%s' % uid, '%s' % cmd.lower()])
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
#    proxy = next(PROXYLOOPITERATOR, None)
#    print(f'DBG> get face with {proxy}')
#    async with httpx.AsyncClient(proxies=proxy, http2=True, headers=headers, timeout=10.0) as sess:
    async with httpx.AsyncClient(http2=True, headers=headers, timeout=10.0) as sess:
        result = await sess.get(url='https://thispersondoesnotexist.com/image')
        return result.content


def get_stats():
    return bytes('%s %s' % (sys.executable or sys.platform, sys.version),'utf-8')

@BOT.message_handler(commands=['start', 'talk', 'stats'])
def send_welcome(message):
    ''' BOT commands logic '''
    if message.chat.id > 0:
        answer = None
        if message.text == '/start':
            BOT.reply_to(message, START_MESSAGE)
        elif message.text == '/talk':
            answer = finder(message.from_user.username)
            BOT.reply_to(message, answer)
        elif message.text == "/stats":
            answer = get_stats()
            BOT.reply_to(message, answer)
        push_to_db(message, answer)


@BOT.message_handler(func=lambda message: True)
def echo_message(message):
    ''' user text logic '''
    if message.chat.id > 0:
        answer = finder(message.from_user.username, message.text)
        BOT.reply_to(message, answer)
        push_to_db(message, answer)

def listener(messages):
    for m in messages:
        print(str(m))

BOT.set_update_listener(listener)
BOT.polling()
