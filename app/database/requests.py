from app.database.models import async_session
from app.database.models import User, Product, Installation_note, Service_note, Cart
from sqlalchemy import select,delete

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))

        if user:
            return user

async def set_installation(user_id, user_name, adress, size, photo, telephone_number, date, time):
    async with async_session() as session:
        
        intsallation = await session.scalar(select(Installation_note).where(Installation_note.user_id==user_id))

        if not intsallation:
            session.add(Installation_note(user_id=user_id, user_name=user_name,
                                           adress=adress, size=size, photo=photo, telephone_number=telephone_number,
                                             date=date, time=time))
            await session.commit()



async def set_service(user_id, user_name, adress, photo, telephone_number, date, time):
    async with async_session() as session:
        
        service = await session.scalar(select(Service_note).where(Service_note.user_id==user_id))

        if not service:
            session.add(Service_note(user_id=user_id, user_name=user_name,
                                           adress=adress, photo=photo, telephone_number=telephone_number,
                                             date=date, time=time))
            await session.commit()


async def get_items():
    async with async_session() as session:
        return await session.scalars(select(Product))
    

async def get_cart(user_id):
    async with async_session() as session:   
        
        cart_items = await session.scalars(select(Cart).filter_by(user_id=user_id))
        cart_info = []

        for item in cart_items:
            product = await session.scalar(select(Product).filter_by(id=item.product_id))
            cart_info.append({
                'product_id': product.id,
                'product_name': product.name,
                'photo': product.photo,
                'quantity': item.quantity,
                'price': product.price,
                'total_price': item.quantity * product.price,
            })
        
        return cart_info

async def add_to_cart(user_id, product_id):
    async with async_session() as session: 
        cart_item = Cart(user_id = user_id, product_id=product_id)
        session.add(cart_item)
        await session.commit()

async def delete_from_cart(user_id, product_id):
    async with async_session() as session:
        cart_item = await session.scalar(select(Cart).filter_by(user_id=user_id, product_id=product_id))
        if cart_item:
            await session.delete(cart_item)
            await session.commit()
            return True
        return False
    
async def get_product_by_name(product_name):
    async with async_session() as session:
        return await session.scalar(select(Product).filter_by(name=product_name))

async def delete_all(user_id):  
    async with async_session() as session:
        await session.execute(delete(Cart).where(Cart.user_id==user_id))
        await session.commit()

    