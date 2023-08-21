import logging
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.sql.expression import distinct

base = declarative_base()

class UserRecord(base):
    ''' user table '''
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    chatid = Column(Integer)
    reg_time = Column(DateTime)
    cash = Column(Float)
    demoexp = Column(Integer)
    demomode = Column(Integer)
    democash = Column(Float)

class MessageRecord(base):
    ''' bot messages log '''
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    query = Column(String)
    answer = Column(String)
    time = Column(DateTime)

class SettingsRecord(base):
    ''' user settings '''
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    bg_file = Column(String)
    font_file = Column(String)
    text_shadow_on_off = Column(Integer)
    splash_on_off = Column(Integer)
    splash_shadow_on_off = Column(Integer)
    splash_size = Column(Integer)
    splash_text = Column(String)

def get_session(path_to_db):
    engine = create_engine(path_to_db, echo=False)
    base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

def get_users_count(session):
    return session.query(func.count(distinct(MessageRecord.name))).scalar()

def get_user_names(session):
    return session.query(distinct(MessageRecord.name)).all()

def push_to_db(session, message, answer=None):
    ''' save username,query and BOT answer (optionaly) into db '''
    logging.debug(f'{message.from_user.username} :  {message.text}')
    if answer is not None:
        print('Answer: ', answer.decode('utf-8'))
    mrec = MessageRecord(name=message.from_user.username, query=message.text,
                         answer=answer, time=datetime.now(timezone.utc))
    session.add(mrec)
    session.commit()
