'''Задача "Меньше текста, больше кликов":
Необходимо дополнить код предыдущей задачи, чтобы вопросы о параметрах тела для расчёта
 калорий выдавались по нажатию кнопки.
Измените massage_handler для функции set_age. Теперь этот хэндлер будет реагировать на
текст 'Рассчитать', а не на 'Calories'.
Создайте клавиатуру ReplyKeyboardMarkup и 2 кнопки KeyboardButton на ней со следующим текстом:
'Рассчитать' и 'Информация'. Сделайте так, чтобы клавиатура подстраивалась под
размеры интерфейса устройства при помощи параметра resize_keyboard.
Используйте ранее созданную клавиатуру в ответе функции start, используя параметр reply_markup.
В итоге при команде /start у вас должна присылаться клавиатура с двумя кнопками.
При нажатии на кнопку с надписью 'Рассчитать' срабатывает функция set_age
с которой начинается работа машины состояний для age, growth и weight.'''


from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging

logging.basicConfig(level=logging.INFO)
api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание клавиатуры
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton('Рассчитать')
button2 = KeyboardButton('Информация')
kb.add(button)
kb.add(button2)

# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Хэндлер команды /start
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)

# Хэндлер для кнопки "Рассчитать"
@dp.message_handler(text='Рассчитать')
async def set_age(message: types.Message):
    await message.answer('Введите свой возраст: (лет)')
    await UserState.age.set()

# Хэндлер для кнопки "Информация"
@dp.message_handler(text='Информация')
async def info_message(message: types.Message):
    await message.answer('Я бот, который помогает рассчитывать калории и следить '
                         'за твоим здоровьем.')

# Хэндлер для состояния age
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост: (в см)')
    await UserState.growth.set()

# Хэндлер для состояния growth
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес: (кг)')
    await UserState.weight.set()

# Хэндлер для состояния weight и расчет калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result = int(10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    await message.answer(f'Ваша норма калорий: {result} в день.')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
