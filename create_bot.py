from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import TOKEN

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

BOT_DESCRIPTION = "Привет. Здесь ты можешь сыграть в игру 'Угадай число'. Бот загадывает число от 0 до 100, " \
                  "ты выбираешь количество попыток, за которое предположительно сможешь его угадать. После каждой " \
                  "неудачной попытки бот подскажет, в большую или меньшую сторону тебе двигаться. "


class MyStatesGroup(StatesGroup):
    new_round = State()
    round = State()
