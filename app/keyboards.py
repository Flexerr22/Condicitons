import locale

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)
from datetime import datetime, timedelta

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import get_items

locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Каталог товаров'),KeyboardButton(text='Корзина')],
    [KeyboardButton(text='Запись на установку'),KeyboardButton(text='Запись на обслуживание')],
    [KeyboardButton(text='Контакты')],
], resize_keyboard=True, input_field_placeholder='Выберите пункт из меню')

get_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить имя и номер', request_contact=True), KeyboardButton(text='Ввести данные вручную')]
], resize_keyboard=True)

contacts = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Связаться с нами', url='https://wa.me/79047138977')]
])

async def create_time_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=2)
    
    time_slots = [
        '8 до 11', '12 до 15', '16 до 19', '20 до 23'
    ]
    
    for time_slot in time_slots:
        button = InlineKeyboardButton(text=f'с {time_slot.replace("-", " до ")}', callback_data=f'time_{time_slot}')
        keyboard.inline_keyboard.append([button])  
    
    return keyboard

async def create_date_keyboard():
    current_date = datetime.now()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for i in range(14):
        day = current_date + timedelta(days=i+1)
        button = InlineKeyboardButton(text=day.strftime("%d %B %Y"), callback_data=f"day_{day.strftime('%d %B %Y')}")
        keyboard.inline_keyboard.append([button])  
    
    return keyboard

change_data_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Размер комнаты', callback_data='change_size'),InlineKeyboardButton(text='Фото', callback_data='change_photo'), InlineKeyboardButton(text='Имя', callback_data='change_name')],
    [InlineKeyboardButton(text='Номер телефона', callback_data='change_phone'),InlineKeyboardButton(text='Адрес', callback_data='change_address')],
    [InlineKeyboardButton(text='Дата', callback_data='change_date'),InlineKeyboardButton(text='Время', callback_data='change_time')],
])

async def confirm_changes_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Изменить другие данные', callback_data='main_change_data'))
    keyboard.add(InlineKeyboardButton(text='Сохранить данные', callback_data='save_data'))
    return keyboard.as_markup()

confirm_or_change = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Сохранить данные', callback_data='save_data'), InlineKeyboardButton(text='Изменить данные', callback_data='main_change_data')]
    ]
)

confirm_or_change = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Сохранить данные', callback_data='save_data'), InlineKeyboardButton(text='Изменить данные', callback_data='main_change_data')]
    ]
)

async def show_items(message):
    all_items = await get_items()
    
    for item in all_items:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='В корзину', callback_data=f"cart_item_{item.id}")]
            ]
        )

        await message.answer_photo(photo=item.photo, caption=(
            f"Название: {item.name}\n"
            f"Описание: {item.description}\n"
            f"Цена: {item.price} ₽"
        ), reply_markup=keyboard)

    return