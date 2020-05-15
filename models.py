from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    channel_name = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime)
