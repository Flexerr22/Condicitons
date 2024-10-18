from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

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