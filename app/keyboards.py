import locale

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)
from datetime import datetime, timedelta

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Каталог товаров'),KeyboardButton(text='Корзина')],
    [KeyboardButton(text='Запись на установку'),KeyboardButton(text='Запись на обслуживание')],
    [KeyboardButton(text='Контакты')],
], resize_keyboard=True, input_field_placeholder='Выберите пункт из меню')

get_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить имя и номер', request_contact=True)]
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
        day = current_date + timedelta(days=i)
        button = InlineKeyboardButton(text=day.strftime("%d %B %Y"), callback_data=f"day_{day.strftime('%d %B %Y')}")
        keyboard.inline_keyboard.append([button])  
    
    return keyboard