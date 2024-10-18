from aiogram import F, Router,Bot
from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)

import app.keyboards as kb

router = Router()

class Register(StatesGroup):
    size = State()
    photo = State()
    adress = State()
    phone = State()
    day = State()
    time = State()

class Servis(StatesGroup):
    size = State()
    photo = State()
    adress = State()
    phone = State()
    day = State()
    time = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать", reply_markup=kb.main)

@router.message(Command("clear"))
async def clear_bot(message: Message, bot: Bot)-> None:
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
    await message.answer('Введите размер своей комнаты куда будет установлен кондиционер')

@router.message(Register.size)
async def reg_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(Register.photo)
    await message.answer('Скиньте фотографии комнату изнутри и снаружи')

@router.message(Register.photo)
async def reg_photo(message: Message, state: FSMContext):
    # Проверяем, есть ли фото в сообщении
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фотографию.')
        return

    # Если фото есть, получаем его
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.set_state(Register.adress)
    await message.answer('Введите ваш адрес')

@router.message(Register.adress)
async def reg_adress (message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await state.set_state(Register.day)
    await message.answer('Выбери день удобный вам для установки')

@router.message(Register.day)
async def reg_day (message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    await state.set_state(Register.time)
    await message.answer('Выберите время удобное для установки')

@router.message(Register.time)
async def reg_time (message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(Register.phone)
    await message.answer('Введите имя и номер телефона', reply_markup=kb.get_number)

@router.message(Register.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(phone = message.contact.phone_number, name=message.contact.first_name)
    data = await state.get_data()
    await message.answer_photo(photo=data['photo'],
        caption=(
            'Спасибо за обращение, запись успешно создана\n'
            f'Размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'Дата установки: {data["day"]} {data["time"]}\n'
        ), reply_markup=kb.main)
    await state.clear()

@router.message(F.text == 'Запись на обслуживание')
async def zap_yst(message: Message, state: FSMContext):
    await state.set_state(Servis.size)
    await message.answer('Введите размер своей комнаты куда будет установлен кондиционер')

@router.message(Servis.size)
async def reg_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(Servis.photo)
    await message.answer('Скиньте пожалуйста фотографию , где установлен внутренний и наружный блок кондиционера.')

@router.message(Servis.photo)
async def reg_photo(message: Message, state: FSMContext):
    # Проверяем, есть ли фото в сообщении
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фотографию.')
        return

    # Если фото есть, получаем его
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.set_state(Servis.adress)
    await message.answer('Введите ваш адрес')


@router.message(Servis.adress)
async def reg_adress (message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await state.set_state(Servis.day)
    await message.answer('Выбери день удобный вам для установки')

@router.message(Servis.day)
async def reg_day (message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    await state.set_state(Servis.time)
    await message.answer('Выберите время удобное для установки')

@router.message(Servis.time)
async def reg_time (message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(Servis.phone)
    await message.answer('Введите имя и номер телефона', reply_markup=kb.get_number)

@router.message(Servis.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(phone = message.contact.phone_number, name=message.contact.first_name)
    data = await state.get_data()
    await message.answer_photo(photo=data['photo'],
        caption=(
            'Спасибо за обращение, запись успешно создана\n'
            f'Размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'Дата установки: {data["day"]} {data["time"]}\n'
        ), reply_markup=kb.main)
    await state.clear()