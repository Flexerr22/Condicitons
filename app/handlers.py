from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from typing import List

import app.keyboards as kb
from app.keyboards import create_date_keyboard, create_time_keyboard

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
    await state.update_data(size=message.text)
    await state.set_state(Register.photo)
    await message.answer('Скиньте фотографию комнаты изнутри')

@router.message(Register.photo, F.photo) 
async def reg_photo(message: Message, state: FSMContext): 
 
    user_data = await state.get_data() 
    photos: List = user_data.get("photo", [])    
 
    photos.append(message.photo[-1].file_id) 
    await state.update_data(photo=photos) 
     
    if len(photos) < 2: 
        await message.answer("Отправьте фотографию комнаты снаружи") 
          
    if len(photos) == 2: 
        print('цикл') 
        await state.set_state(Register.adress) 
        await message.answer('Введите ваш адресс')

@router.message(Register.adress)
async def reg_adress(message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await state.set_state(Register.day)
    await message.answer('Выбери день удобный вам для установки', reply_markup=await create_date_keyboard())

@router.callback_query(F.data.startswith('day_'))
async def process_date_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data[4:] 
    await state.update_data(day=selected_date)
    await callback_query.message.answer(f'Вы выбрали дату: {selected_date}. Теперь выберите удобное время для установки.', reply_markup=await create_time_keyboard())
    await state.set_state(Register.time)

@router.callback_query(F.data.startswith('time_'))
async def time_call(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data[5:]
    await state.update_data(time=selected_time)
    await callback_query.message.answer(f'Вы выбрали время: с {selected_time} часов. Пожалуйста, отправьте ваш контакт для завершения записи.', reply_markup=kb.get_number)
    
    await state.set_state(Register.phone)

@router.message(Register.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number, name=message.contact.first_name)
    data = await state.get_data()
    await message.answer_photo(photo=data['photo'][0],
        caption=(
            'Спасибо за обращение, запись успешно создана\n'
            f'Ваш размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов'
        ), reply_markup=kb.main)
    await state.clear()

@router.message(Servis.size)
async def reg_size_servis(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(Servis.photo)
    await message.answer('Скиньте пожалуйста фотографию, где установлен внутренний и наружный блок кондиционера.')

@router.message(Servis.photo)
async def reg_photo_servis(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фотографию.')
        return

    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.set_state(Servis.adress)
    await message.answer('Введите ваш адрес')

@router.message(Servis.adress)
async def reg_adress(message: Message, state: FSMContext):
    await state.update_data(adress=message.text)
    await state.set_state(Servis.day)
    await message.answer('Выбери день удобный вам для установки', reply_markup=await create_date_keyboard())

@router.callback_query(F.data.startswith('day_'))
async def process_date_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data[4:] 
    await state.update_data(day=selected_date)
    await callback_query.message.answer(f'Вы выбрали дату: {selected_date}. Теперь выберите удобное время для установки.', reply_markup=await create_time_keyboard())
    await state.set_state(Servis.time)

@router.callback_query(F.data.startswith('time_'))
async def time_call(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data[5:]
    await state.update_data(time=selected_time)
    await callback_query.message.answer(f'Вы выбрали время: с {selected_time} часов. Пожалуйста, отправьте ваш контакт для завершения записи.', reply_markup=kb.get_number)
    
    await state.set_state(Servis.phone)

@router.message(Servis.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number, name=message.contact.first_name)
    data = await state.get_data()
    await message.answer_photo(photo=data['photo'],
        caption=(
            'Спасибо за обращение, запись успешно создана\n'
            f'Ваш размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов'
        ), reply_markup=kb.main)
    await state.clear()
