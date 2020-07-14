from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from chatbot.settings import DB_CONNECTION_STRING

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone_number = Column(String)
    platform = Column(String)
    user_id = Column(Integer, nullable=False, unique=True)
    email = Column(String)
    timestamp_of_record = Column(DateTime, nullable=False)
    card_number = Column(BigInteger, ForeignKey('giftcard.card_number'))


class GiftCard(Base):
    __tablename__ = 'giftcard'
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(BigInteger, unique=True)
    mechanics_id = Column(Integer, ForeignKey('giftmechanics.id'))


class GiftMechanics(Base):
    __tablename__ = 'giftmechanics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mechanics_name = Column(String)
    mechanics_type = Column(String)


def main():
    engine = create_engine(URL(**DB_CONNECTION_STRING), echo=True)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
