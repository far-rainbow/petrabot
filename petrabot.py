import os
import subprocess
from datetime import datetime, timezone
from hashlib import sha3_256 as hash
import requests
import telebot
import httpx

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

ROOTDIR = os.path.dirname(os.path.abspath(__file__))
API_TOKEN = '1067546684:AAEyYPuY1m9cIQ7OMVux71rBy6mS6pC9EAg'
bot = telebot.TeleBot(API_TOKEN)

BASE = declarative_base()
class MessageRecord(BASE):
    ''' ORM '''
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    query = Column(String)
    answer = Column(String)
    time = Column(DateTime)

engine = create_engine(f'sqlite:///petrabot.db', echo=False)
BASE.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

def push_to_db(message,answer=None):
    print(message.from_user.username,' : ',message.text)
    if answer is not None:
        print('Answer: ',answer.decode('utf-8'))
    mrec = MessageRecord(name=message.from_user.username,query=message.text,answer=answer,time=datetime.now(timezone.utc))
    session.add(mrec)
    session.commit()

# find citates with user words
def finder(uid, cmd=''):
    try:
        fortune = subprocess.check_output(['%s/finder.sh' % ROOTDIR, '%s' % uid, '%s' % cmd.lower()])
    except:
        fortune = subprocess.check_output(['/usr/games/fortune', '-a', '/usr/share/games/fortunes/'])
    return fortune

def get_face():
    ''' html response getter '''
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; YandexMetrika/2.0; \
                +http://yandex.com/bots yabs01)'}
    with httpx.Client(headers=headers, timeout=10.0) as sess:
        return sess.get(url='https://thispersondoesnotexist.com/image').content

@bot.message_handler(commands=['help', 'start','stop','face','fortune'])
def send_welcome(message):

    answer = None
    if message.text == '/start':
        bot.reply_to(message, f"Hi there, I am Kamenka SU Bot. I am here to enjoy you with some stuff. Tap /help to get more info.")
    elif message.text == '/help':
        bot.reply_to(message,f'Commands:\n/face -- get fake face\n/fortune -- get random cookie text\nChat with bot to get some contex fortunes...')
    elif message.text == '/stop':
        bot.reply_to(message, 'Z-z-z-z...')
    elif message.text == '/face':
        bot.send_photo(message.chat.id, get_face())
    elif message.text == '/fortune':
        answer = finder(message.from_user.username)
        bot.reply_to(message, answer)
    push_to_db(message,answer)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):

    answer = finder(message.from_user.username,message.text)
    bot.reply_to(message,answer)
    push_to_db(message,answer)

bot.polling()
