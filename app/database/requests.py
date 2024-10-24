from app.database.models import async_session
from app.database.models import User, Product, Installation_note, Service_note, Cart
from sqlalchemy import select
import json

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def set_installation(user_id, user_name, adress, size, photo, telephone_number, date, time):
    async with async_session() as session:
        installation = await session.scalar(select(Installation_note).where(Installation_note.user_id == user_id))

        if not installation:
            photo_json = json.dumps(photo)

            session.add(Installation_note(user_id=user_id, user_name=user_name,
                                          adress=adress, size=size, photo=photo_json, 
                                          telephone_number=telephone_number, date=date, time=time))
            await session.commit()

async def set_service(user_id, user_name, adress, photo, telephone_number, date, time):
    async with async_session() as session:
        service = await session.scalar(select(Service_note).where(Service_note.user_id == user_id))

        if not service:
            photo_json = json.dumps(photo)

            session.add(Service_note(user_id=user_id, user_name=user_name,
                                     adress=adress, photo=photo_json, 
                                     telephone_number=telephone_number, date=date, time=time))
            await session.commit()

async def get_items():
    async with async_session() as session:
        return await session.scalars(select(Product))
