from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from typing import List

import app.keyboards as kb
from app.keyboards import create_date_keyboard, create_time_keyboard, change_data_keyboard, confirm_changes_keyboard

router = Router()

class Register(StatesGroup):
    size = State()
    photo = State()
    adress = State()
    phone = State()
    day = State()
    time = State()
    confirm_data = State()
    change_data = State()

class Changes(StatesGroup):
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
    confirm_data = State()
    change_data = State()

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
        await state.set_state(Register.adress) 
        await message.answer('Введите ваш адресс')

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
    
    await state.set_state(Register.phone)

@router.message(Register.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number, name=message.contact.first_name)
    data = await state.get_data()
    await message.answer(
        f'Ваш размер комнаты: {data["size"]}\n'
        f'Имя: {data["name"]}\n'
        f'Адрес: {data["adress"]}\n'
        f'Номер телефона: {data["phone"]}\n'
        f'День установки: {data["day"]}\n'
        f'Время для установки: с {data["time"]} часов\n'
        'Проверьте данные и выберите действие'
        ,reply_markup=kb.confirm_or_change
    )
    await state.set_state(Register.confirm_data)

@router.callback_query(F.data == 'save_data')
async def save_data_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer_photo(
        photo=data['photo'][0],  # Отправляем первую фотографию
        caption=(
            'Спасибо за обращение, запись успешно создана\n'
            f'Ваш размер комнаты: {data["size"]}\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов'
        ), 
        reply_markup=kb.main
    )
    await state.clear()

@router.callback_query(F.data == 'main_change_data')
async def change_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите данные для изменения', reply_markup=await change_data_keyboard())



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
    await state.update_data(size=message.text)
    await message.answer('Размер комнаты изменен. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Register.confirm_data)

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
    print('2  ', photos)

    await state.update_data(photo=photos) 
    print('3  ', photos)
     
    if len(photos) < 2: 
        await message.answer("Отправьте вторую фотографию") 
          
    if len(photos) == 2:
        await state.update_data(photo=photos)
        await message.answer('Фотографии изменены. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
        await state.set_state(Register.confirm_data)

@router.message(F.text == 'Запись на обслуживание')
async def reg_size_servis(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(Servis.photo)
    await message.answer('Скиньте пожалуйста фотографию, где установлен внутренний блок кондиционера.')

@router.message(Servis.photo)
async def reg_photo_servis(message: Message, state: FSMContext):
    user_data = await state.get_data() 
    photos: List = user_data.get("photo", [])    
 
    photos.append(message.photo[-1].file_id) 
    await state.update_data(photo=photos) 
     
    if len(photos) < 2: 
        await message.answer("Скиньте пожалуйста фотографию, где установлен наружний блок кондиционера.") 
          
    if len(photos) == 2: 
        print('цикл') 
        await state.set_state(Servis.adress) 
        await message.answer('Введите ваш адресс')

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
    
    await state.set_state(Servis.phone)

@router.message(Servis.phone, F.contact)
async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number, name=message.contact.first_name)
    data = await state.get_data()
    await message.answer(
        f'Имя: {data["name"]}\n'
        f'Адрес: {data["adress"]}\n'
        f'Номер телефона: {data["phone"]}\n'
        f'День установки: {data["day"]}\n'
        f'Время для установки: с {data["time"]} часов\n'
        'Проверьте данные и выберите действие'
        ,reply_markup=kb.confirm_or_change
    )
    await state.set_state(Servis.confirm_data)

@router.callback_query(F.data == 'save_data')
async def save_data_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer_photo(
        photo=data['photo'][0],
        caption=(
            'Спасибо за обращение, запись успешно создана\n'
            f'Имя: {data["name"]}\n'
            f'Адрес: {data["adress"]}\n'
            f'Номер телефона: {data["phone"]}\n'
            f'День установки: {data["day"]}\n'
            f'Время для установки: с {data["time"]} часов'
        ), 
        reply_markup=kb.main
    )
    await state.clear()

@router.callback_query(F.data == 'main_change_data')
async def change_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите данные для изменения', reply_markup=await change_data_keyboard())



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
    await state.set_state(Servis.confirm_data)

@router.message(Changes.size)
async def handle_new_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer('Размер комнаты изменен. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Servis.confirm_data)

@router.callback_query(Changes.day, F.data.startswith('day_'))
async def process_date_selection(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data[4:] 
    await state.update_data(day=selected_date)
    await callback_query.message.answer('Дата изменена. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Servis.confirm_data)

@router.callback_query(Changes.time, F.data.startswith('time_'))
async def time_call(callback_query: CallbackQuery, state: FSMContext):
    selected_time = callback_query.data[5:]
    await state.update_data(time=selected_time)
    await callback_query.message.answer('Время изменено. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
    await state.set_state(Servis.confirm_data)

@router.message(Changes.photo)
async def handle_new_photo(message: Message, state: FSMContext):
    photos = []
   
    photos.append(message.photo[-1].file_id)
    print('2  ', photos)

    await state.update_data(photo=photos) 
    print('3  ', photos)
     
    if len(photos) < 2: 
        await message.answer("Отправьте вторую фотографию") 
          
    if len(photos) == 2:
        await state.update_data(photo=photos)
        await message.answer('Фотографии изменены. Желаете изменить что-то еще?', reply_markup=await confirm_changes_keyboard())
        await state.set_state(Servis.confirm_data)