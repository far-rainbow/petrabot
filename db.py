import logging
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.sql.expression import distinct

base = declarative_base()


class MessageRecord(base):
    ''' ORM '''
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    query = Column(String)
    answer = Column(String)
    time = Column(DateTime)

def get_session(path_to_db):
    engine = create_engine(path_to_db, echo=False)
    base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

def get_users_count(session):
    mcnt = session.query(func.count(distinct(MessageRecord.name))).scalar()
    return mcnt

def get_users_name(session):
    mnames = session.query(distinct(MessageRecord.name)).all()
    return mnames

def push_to_db(session, message, answer=None):
    ''' save username,query and BOT answer (optionaly) into db '''
    logging.debug(f'{message.from_user.username} :  {message.text}')
    if answer is not None:
        print('Answer: ', answer.decode('utf-8'))
    mrec = MessageRecord(name=message.from_user.username, query=message.text,
                         answer=answer, time=datetime.now(timezone.utc))
    session.add(mrec)
    session.commit()
