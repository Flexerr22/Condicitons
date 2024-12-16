import json
import re
from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from typing import List
from datetime import datetime, time
import app.keyboards as kb
from app.keyboards import create_date_keyboard, create_time_keyboard, change_data_keyboard, confirm_changes_keyboard
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests as rq

router = Router()

class Register(StatesGroup):
    size = State()
    photo = State()
    adress = State()
    name = State()
    phone = State()
    day = State()
    time = State()
    confirm_data = State()
    change_data = State()

class Changes(StatesGroup):
    name = State()
    size = State()
    photo = State()
    adress = State()
    phone = State()
    day = State()
    time = State()

class Servis(StatesGroup):
    name = State()
    size = State()
    photo = State()
    adress = State()
    phone = State()
    day = State()
    time = State()
    confirm_data = State()
    change_data = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer("Добро пожаловать", reply_markup=kb.main)

@router.message(Command("clear"))
async def clear_bot(message: Message, bot: Bot) -> None:
    try:
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")

@router.message(F.text == 'Контакты')
async def contants(message: Message):
    await message.answer('Наши контакты', reply_markup=kb.contacts)

@router.message(F.text == 'Запись на установку')
async def zap_yst(message: Message, state: FSMContext):
    await state.set_state(Register.size)
    await message.answer('Введите квадратуру комнаты в которой будет установлен кондиционер')

@router.message(Register.size)
async def reg_size(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(size=message.text)
        await state.set_state(Register.photo)
        await message.answer('Отправьте фотографию комнаты изнутри и снаружи (2 фото)')
    else:
        await message.answer('Неверный формат квадратуры. Введите число.')

@router.message(Register.photo, F.media_group_id)
async def handle_media_group(message: Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    media_group = data.get('media_group', [])

    # Добавляем фото из медиагруппы только один раз
    if message.media_group_id not in data:
        media_group.extend([message.photo[-1].file_id])  # Добавляем только одно фото на медиагруппу
        await state.update_data(media_group_id=message.media_group_id, media_group=media_group)

    # Проверяем количество фото в медиагруппе
    if len(media_group) == 2:
        await message.answer("Получены две фотографии. Теперь введите ваш адрес.")
        await state.update_data(photo=media_group)
        print(media_group)
        await state.set_state(Register.adress)
    elif len(media_group) > 2:
        await message.answer("Вы отправили больше двух фотографий. Пожалуйста, отправьте ровно две фотографии.")
        await state.update_data(media_group=[])  # Сброс состояния медиагруппы

# Обработчик для одиночных фото
@router.message(Register.photo, F.photo & F.media_group_id.is_(None))  # Проверяем, что фото не в составе альбома
async def handle_single_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    # Добавляем фото в список
    photos.append(message.photo[-1].file_id)

    # Обновляем данные в состоянии
    await state.update_data(photos=photos)

    # Проверяем, если получили две фотографии
    if len(photos) == 2:
        await message.answer("Получены две фотографии. Теперь введите ваш адрес.")
        await state.set_state(Register.adress)
    elif len(photos) > 2:
        await message.answer("Вы отправили больше двух фотографий. Пожалуйста, отправьте ровно две фотографии.")
        await state.update_data(photos=[])  # Сброс состояния одиночных фото
# @router.message(Register.photo, F.photo)
# async def reg_photo(message: Message, state: FSMContext): 
 
#     user_data = await state.get_data() 
#     photos: List = user_data.get("photo", [])    
 
#     photos.append(message.photo[-1].file_id) 
#     await state.update_data(photo=photos) 
     
#     if len(photos) < 2: 
#         await message.answer("Отправьте фотографию комнаты снаружи") 
          
#     if len(photos) == 2: 
#         await state.set_state(Register.adress) 
#         await message.answer('Введите ваш адресс')

@router.message(Register.adress)
async def reg_adress(message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await state.set_state(Register.day)
    await message.answer('Выбери день удобный вам для установки', reply_markup=await create_date_keyboard())

@router.callback_query(Register.day, F.data.startswith('day_'))
async def process_date_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data[4:] 
    await state.update_data(day=selected_date)
    await callback_query.message.answer(f'Вы выбрали дату: {selected_date}. Теперь выберите удобное время для установки.', reply_markup=await create_time_keyboard())
    await state.set_state(Register.time)

@router.callback_query(Register.time, F.data.startswith('time_'))
async def time_call(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data[5:]
    await state.update_data(time=selected_time)
    await callback_query.message.answer(f'Вы выбрали время: с {selected_time} часов. Пожалуйста, отправьте ваш контакт для завершения записи.', reply_markup=kb.get_number)


@router.message(F.text == 'Ввести данные вручную')
async def reg_pn(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('Введите ваше имя')

# Хендлер для ввода имени вручную
@router.message(Register.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите ваш номер телефона')
    await state.set_state(Register.phone)


@router.message(Register.phone)
async def reg_phone_hand(message: Message, state: FSMContext):
    phone = message.text

    if len(phone) == 11 and (phone.isdigit()):
        await state.update_data(phone=phone)

        data = await state.get_data()
        await message.answer(
            f'Ваш размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов\n'
            'Проверьте данные и выберите действие',
            reply_markup=kb.confirm_or_change
        )
        await state.set_state(Servis.confirm_data)
    else:
        await message.answer('Неверный формат телефона, попробуйте заново.\nПравильный формат: +7xxxxxxxxxx или 8xxxxxxxxxx')


@router.message(F.contact)
async def reg_phone(message: Message, state: FSMContext):
    if message.contact:
        await state.update_data(phone=message.contact.phone_number, name=message.contact.first_name)
    else:
        await state.update_data(phone=message.text)
    
    data = await state.get_data()
    photos = data.get("media_group", [])
    if len(photos) >= 2:
        await message.answer_media_group(media=[
            types.InputMediaPhoto(media=photos[0]),
            types.InputMediaPhoto(media=photos[1]),
        ])
    
    # Вывод итоговых данных
    data = await state.get_data()
    await message.answer(
        f'Ваш размер комнаты: {data["size"]}\n'
        f'Имя: {data["name"]}\n'
        f'Адрес: {data["adress"]}\n'
        f'Номер телефона: {data["phone"]}\n'
        f'День установки: {data["day"]}\n'
        f'Время для установки: с {data["time"]} часов\n'
        'Проверьте данные и выберите действие',
        reply_markup=kb.confirm_or_change
    )
    await state.set_state(Register.confirm_data)


@router.callback_query(F.data == 'save_data')
async def save_data_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    # Преобразование даты в объект date 
    try:
        day_obj = datetime.strptime(data['day'], '%d %B %Y').date()
    except ValueError:
        await callback.message.answer('Произошла ошибка при обработке даты. Пожалуйста, попробуйте снова.')
        await state.clear()
        return 

    # Преобразование времени в объект time
    try:
        start_hour = int(data['time'].split(' до ')[0]) 
        time_obj = time(hour=start_hour, minute=0, second=0)  
    except (ValueError, IndexError) as e:
        await callback.message.answer('Произошла ошибка при обработке времени. Пожалуйста, попробуйте снова.')
        await state.clear()
        return
    media_group_json = json.dumps(data['media_group'])
    # Проверка наличия ключа 'size' и формирование сообщения
    if ('size' in data and data['size']!=0) and 'media_group' in data and len(data['media_group']) > 0:
        
        caption = (
            'Спасибо за обращение, запись успешно создана\n'
            f'Ваш размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов'
        )

        await rq.set_installation(
            user_id=callback.from_user.id, 
            user_name=data['name'], 
            adress=data['adress'], 
            size=str(data['size']),
            photo=media_group_json,  
            telephone_number=data['phone'], 
            date=day_obj,       
            time=time_obj  
        )
    else:
        caption = (
            'Спасибо за обращение, запись успешно создана\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов'
        )
        
        await rq.set_service(
            user_id=callback.from_user.id, 
            user_name=data['name'], 
            adress=data['adress'], 
            telephone_number=data['phone'], 
            date=day_obj,     
            photo=media_group_json,     
            time=time_obj  
        )

    # Отправка сообщения после всех операций
    await callback.message.answer_photo(
        photo=data['photo'][0],
        caption=caption,
        reply_markup=kb.main
    )

    await state.clear()

    # try:
    #     day_obj = datetime.strptime(data['day'], '%d %B %Y').date()  # Преобразуем в объект date
    #     formatted_date = day_obj.strftime('%Y-%m-%d') 
    # except ValueError:
    #     formatted_date = None  # Обработка ошибки, если дата невалидна

    # # Преобразование времени
    # start_time = data['time'].split(' до ')[0]  # Получаем время начала
    # formatted_time = f"{start_time}:00:00"  # Форматируем время в HH:MM:SS

    # # Обновляем словарь
    # data['day'] = formatted_date
    # data['time'] = formatted_time
    
    # await rq.set_installation(user_id=callback.from_user.id, user_name=data['name'] , adress=data['adress'], size=data['size'],
    #                           photo='photo_path', telephone_number=data['phone'], date=data['day'], time=data['time'])
    await state.clear()

@router.callback_query(F.data == 'main_change_data')
async def change_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите данные для изменения', reply_markup=change_data_keyboard)



@router.callback_query(F.data.startswith('change_'))
async def change_data_callback(callback: CallbackQuery, state: FSMContext):
    field_to_change = callback.data.split('_')[1]

    if field_to_change == 'size':
        await state.set_state(Changes.size)
        await callback.message.answer('Введите новый размер комнаты:')
    elif field_to_change == 'photo':
        await state.set_state(Changes.photo)
        await callback.message.answer('Отправьте новые фотографии (две штуки):')
    elif field_to_change == 'address':
        await state.set_state(Changes.adress)
        await callback.message.answer('Введите новый адрес:')
    elif field_to_change == 'name':
        await state.set_state(Changes.name)
        await callback.message.answer('Введите новое имя:')
    elif field_to_change == 'phone':
        await state.set_state(Changes.phone)
        await callback.message.answer('Введите новый номер телефона:')
    elif field_to_change == 'date':
        await state.set_state(Changes.day)
        await callback.message.answer('Выберите новую дату:', reply_markup=await create_date_keyboard())
    elif field_to_change == 'time':
        await state.set_state(Changes.time)
        await callback.message.answer('Выберите новое время:', reply_markup=await create_time_keyboard())

    await callback.answer()


@router.message(Changes.adress)
async def handle_new_adress(message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await message.answer('Адрес изменен. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Register.confirm_data)

@router.message(Changes.size)
async def handle_new_size(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(size=message.text)
        await message.answer('Размер комнаты изменен. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
        await state.set_state(Register.confirm_data)
    else:
        await message.answer('Неверный формат квадратуры. Введите число.')

@router.message(Changes.name)
async def handle_new_adress(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Имя изменено. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Register.confirm_data)

@router.message(Changes.phone)
async def handle_new_size(message: Message, state: FSMContext):
    phone = message.text

    phone = message.text
    phone.replace('+', '')

    if len(phone) == 11 and (phone.isdigit()):
        await state.update_data(phone=phone)
        await message.answer('Номер телефона изменен. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
        await state.set_state(Register.confirm_data)
    else:
        await message.answer('Неверный формат телефона, попробуйте заново.\nПравильный формат: +7xxxxxxxxxx или 8xxxxxxxxxx')

@router.callback_query(Changes.day, F.data.startswith('day_'))
async def process_date_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data[4:] 
    await state.update_data(day=selected_date)
    await callback_query.message.answer('Дата изменена. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Register.confirm_data)

@router.callback_query(Changes.time, F.data.startswith('time_'))
async def time_call(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data[5:]
    await state.update_data(time=selected_time)
    await callback_query.message.answer('Время изменено. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Register.confirm_data)

@router.message(Changes.photo)
async def handle_new_photo(message: Message, state: FSMContext):
    photos = []
   
    photos.append(message.photo[-1].file_id)
    await state.update_data(photo=photos) 
     
    if len(photos) < 2: 
        await message.answer("Отправьте вторую фотографию") 
          
    if len(photos) == 2:
        await state.update_data(photo=photos)
        await message.answer('Фотографии изменены. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
        await state.set_state(Register.confirm_data)

@router.message(F.text == 'Запись на обслуживание')
async def reg_size_servis(message: Message, state: FSMContext):
    await state.update_data(size=0)
    await state.set_state(Servis.photo)
    await message.answer('Отправьте фотографию комнаты изнутри и снаружи (2 фото)')

# @router.message(Servis.photo)
# async def reg_photo_servis(message: Message, state: FSMContext):
#     user_data = await state.get_data() 
#     photos: List = user_data.get("photo", [])    
 
#     photos.append(message.photo[-1].file_id) 
#     await state.update_data(photo=photos) 
     
#     if len(photos) < 2: 
#         await message.answer("Скиньте пожалуйста фотографию, где установлен наружний блок кондиционера.") 
          
#     if len(photos) == 2: 
#         print('цикл') 
#         await state.set_state(Servis.adress) 
#         await message.answer('Введите ваш адресс')



@router.message(Servis.photo, F.media_group_id)
async def handle_media_group(message: Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    media_group = data.get('media_group', [])

    # Добавляем фото из медиагруппы только один раз
    if message.media_group_id not in data:
        media_group.extend([message.photo[-1].file_id])  # Добавляем только одно фото на медиагруппу
        await state.update_data(media_group_id=message.media_group_id, media_group=media_group)

    # Проверяем количество фото в медиагруппе
    if len(media_group) == 2:
        await message.answer("Получены две фотографии. Теперь введите ваш адрес.")
        await state.update_data(photo=media_group)
        await state.set_state(Servis.adress)
    elif len(media_group) > 2:
        await message.answer("Вы отправили больше двух фотографий. Пожалуйста, отправьте ровно две фотографии.")
        await state.update_data(media_group=[])  # Сброс состояния медиагруппы

# Обработчик для одиночных фото
@router.message(Servis.photo, F.photo & F.media_group_id.is_(None))  # Проверяем, что фото не в составе альбома
async def handle_single_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    # Добавляем фото в список
    photos.append(message.photo[-1].file_id)

    # Обновляем данные в состоянии
    await state.update_data(photo=photos)

    # Проверяем, если получили две фотографии
    if len(photos) == 2:
        await message.answer("Получены две фотографии. Теперь введите ваш адрес.")
        await state.set_state(Servis.adress)
    elif len(photos) > 2:
        await message.answer("Вы отправили больше двух фотографий. Пожалуйста, отправьте ровно две фотографии.")
        await state.update_data(photos=[])  # Сброс состояния одиночных фото


@router.message(Servis.adress)
async def reg_adress(message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await state.set_state(Servis.day)
    await message.answer('Выбери день удобный вам для приезда на обслуживание', reply_markup=await create_date_keyboard())

@router.callback_query(F.data.startswith('day_'))
async def process_date_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data[4:] 
    await state.update_data(day=selected_date)
    await callback_query.message.answer(f'Вы выбрали дату: {selected_date}. Теперь выберите удобное время для приезда на обслуживание.', reply_markup=await create_time_keyboard())
    await state.set_state(Servis.time)

@router.callback_query(F.data.startswith('time_'))
async def time_call(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data[5:]
    await state.update_data(time=selected_time)
    await callback_query.message.answer(f'Вы выбрали время: с {selected_time} часов. Пожалуйста, отправьте ваш контакт для завершения записи.', reply_markup=kb.get_number)

@router.message(F.text == 'Ввести данные вручную')
async def reg_pn(message: Message, state: FSMContext):
    await state.set_state(Servis.name)
    await message.answer('Введите ваше имя')

@router.message(Servis.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите ваш номер телефона')
    await state.set_state(Servis.phone)


@router.message(Servis.phone)
async def reg_phone_hand(message: Message, state: FSMContext):
    phone = message.text
    phone.replace('+', '')

    if len(phone) == 11 and (phone.isdigit()):
        await state.update_data(phone=phone)

        data = await state.get_data()
        await message.answer(
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов\n'
            'Проверьте данные и выберите действие',
            reply_markup=kb.confirm_or_change
        )
        await state.set_state(Servis.confirm_data)
    else:
        await message.answer('Неверный формат телефона, попробуйте заново.\nПравильный формат: +7xxxxxxxxxx или 8xxxxxxxxxx')


@router.message(F.contact)
async def reg_phone(message: Message, state: FSMContext):
    if message.contact:
        await state.update_data(phone=message.contact.phone_number, name=message.contact.first_name)
    else:
        await state.update_data(phone=message.text)
    
    data = await state.get_data()

    await message.answer(
        f'Имя: {data["name"]}\n'
        f'Адрес: {data["adress"]}\n'
        f'Номер телефона: {data["phone"]}\n'
        f'День установки: {data["day"]}\n'
        f'Время для установки: с {data["time"]} часов\n'
        'Проверьте данные и выберите действие',
        reply_markup=kb.confirm_or_change
    )
    await state.set_state(Servis.confirm_data)


@router.message(F.text == 'Каталог товаров')
async def catalog(message: Message):
    items_text = await kb.show_items(message)
    await message.answer(items_text)

@router.callback_query(F.data.startswith('item_'))
async def item_details(callback: CallbackQuery):
    item_data = await rq.get_items(callback.data)
    await callback.message.answer_photo(photo=item_data.photo, caption=f'{item_data.name}\n{item_data.description}\n{item_data.price} ₽')


@router.message(F.text == 'Корзина')
async def cart(message: Message):
    user_id = message.from_user.id
    user = await rq.get_user(user_id)

    if user:
        cart_products = await rq.get_cart(user_id=user_id)

        if cart_products:
            total_products = len(cart_products)
            total_price = sum(product['total_price'] for product in cart_products)

            drop_all = InlineKeyboardButton(
                text="Очистить корзину",
                callback_data=f"drop_all:{user_id}"
            )
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[drop_all]])
            cart_text = (
                f"🛒 **Ваша корзина:**\n\n"
                f"**Количество товаров:** {total_products}\n"
                f"**Общая стоимость:** {total_price} ₽\n\n"
            )

            await message.answer(cart_text, reply_markup=keyboard1)

            for product in cart_products:
                delete_button = InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"delete_from_cart:{product['product_id']}" 
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[delete_button]])

                product_text = (
                    f"**{product['product_name']}**\n\n"
                    f"Цена: {product['price']} ₽\n"
                    f"Количество: {product['quantity']}\n"
                )

                await message.answer_photo(
                    photo=product['photo'],
                    caption=product_text,
                    reply_markup=keyboard
                ) 
        else:
            await message.answer('🛒 **Ваша корзина пуста!**', show_alert=True)
        
    else:
        await message.answer('Мы не смогли найти данные о вас.\nПожалуйста, начните работу с ботом с команды /start', show_alert=True)

@router.callback_query(F.data.startswith('cart_item_'))
async def add_item_to_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    product_id = int(callback.data[10:])
    success = await rq.add_to_cart(user_id=user_id, product_id=product_id)
    if  not success:
        await callback.answer("Товар успешно добавлен в корзину", show_alert=True)
    else:
        await callback.answer("Не получилось добавить товар в корзину", show_alert=True)

@router.callback_query(F.data.startswith('delete_from_cart:'))
async def delete_item_from_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    product_id = int(callback.data.split(":")[1])  # Получаем product_id из callback data

    # Находим товар в корзине по user_id и product_id
    success = await rq.delete_from_cart(user_id=user_id, product_id=product_id)

    if success:
        await callback.answer("Товар успешно удалён из корзины.", show_alert=True)
    else:
        await callback.answer("Не удалось удалить товар из корзины.", show_alert=True)


@router.callback_query(F.data.startswith('drop_all:'))
async def drop_all_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    success = await rq.delete_all(user_id=user_id)

    if success:
        message = callback.message
        await callback.answer('Не удалось очистить корзину', show_alert=True)
        empty_cart_text = '🛒 **Ваша корзина пуста!**'
        await message.edit_text(empty_cart_text)
        await message.edit_reply_markup()
    else:
        await callback.answer("Корзина успешно очищена", show_alert=True)



