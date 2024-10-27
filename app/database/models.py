from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from sqlalchemy import Column, Integer, BigInteger, String, Time, Date
from sqlalchemy import ForeignKey

engine = create_async_engine(url="postgresql+asyncpg://postgres:postgres@localhost:5432/telegram_bot")

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False, unique=True)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    photo = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer)

class Installation_note(Base):
    __tablename__ = 'installations'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))
    user_name = Column(String, nullable=False)
    adress = Column(String, nullable=False)
    size = Column(String, nullable=False)
    photo = Column(String, nullable=False)
    telephone_number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)

class Service_note(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))
    user_name = Column(String, nullable=False)
    adress = Column(String, nullable=False)
    photo = Column(String, nullable=False)
    telephone_number = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)

class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    user = relationship("User", backref="carts")
    product = relationship("Product", backref="carts")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)