from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import random
from config import TOKEN

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


class MyStatesGroup(StatesGroup):
    new_round = State()
    round = State()


BOT_DESCRIPTION = "Привет. Здесь ты можешь сыграть в игру 'Угадай число'. Бот загадывает число от 0 до 100, " \
                  "ты выбираешь количество попыток, за которое предположительно сможешь его угадать. После каждой " \
                  "неудачной попытки бот подскажет, в большую или меньшую сторону тебе двигаться. "


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(text="Добрый день! Начнём, пожалуй.", reply_markup=make_kb())
    await msg.delete()


def make_kb() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="Новая игра")
    b2 = KeyboardButton(text="Правила")
    kb.add(b1, b2)
    return kb


@dp.message_handler(Text(equals="Правила"))
async def desc(msg: types.Message):
    await msg.answer(text=BOT_DESCRIPTION)
    await msg.delete()


@dp.message_handler(Text(equals="Выйти из игры"), state="*")
async def game_cancel(msg: types.message, state: FSMContext):
    await msg.delete()
    await msg.answer(text="Вы вышли из игры", reply_markup=make_kb())
    await state.finish()


@dp.message_handler(Text(equals="Новая игра"), state="*")
async def new_game(msg: types.Message):
    await msg.answer(text="За сколько попыток ты угадаешь число?", reply_markup=game_kb())
    await msg.delete()
    await MyStatesGroup.new_round.set()


def game_kb() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="Новая игра")
    b2 = KeyboardButton(text="Выйти из игры")
    kb.add(b1, b2)
    return kb


@dp.message_handler(lambda message: not message.text.isdigit() or int(message.text) not in range(0, 101),
                    state=[MyStatesGroup.new_round, MyStatesGroup.round])
async def validator(msg: types.Message):
    """
    The function checks, that the value entered by the player must be
    A NUMBER, whose range is from 0 to 100 inclusive.
    """
    await msg.answer(text="Нужно число от 0 до 100", reply_markup=game_kb())


@dp.message_handler(state=MyStatesGroup.new_round)
async def new_round(msg: types.Message, state: FSMContext):
    """
    The function welcomes the user, notifies that the bot
    thought of a number and prompts the user to indicate the number himself
    attempts, for which he guesses this number in the upcoming round.
    """
    async with state.proxy() as data:
        data["max_attempts"] = int(msg.text)
        data["secret_number"] = random.randint(1, 100)
        await msg.answer(text=f"Ты должен угадать моё число с {msg.text} попыток, поехали!",
                         reply_markup=game_kb())
        await MyStatesGroup.round.set()


@dp.message_handler(state=MyStatesGroup.round)
async def game_round(msg: types.Message, state: MyStatesGroup.new_round):
    """
    The function compares the number, received from the user with the number,
    which the bot thought of and tells you which way to move,
    to find the secret number.
    Also, function counts the number of attempts, that the user has left to
    find the correct number.
    """
    guess = int(msg.text)
    async with state.proxy() as data:
        data["max_attempts"] -= 1
        if guess == data["secret_number"]:
            await state.finish()
            await msg.answer("Ты выиграл!", reply_markup=make_kb())
            await bot.send_sticker(chat_id=msg.chat.id,
                                   sticker="CAACAgQAAxkBAAIKiGPkwh-tkRM9buouxqbSK_p6ahGuAALxAwACoOo7Bc0aqxT0najqLgQ")
        elif guess < data["secret_number"] and data["max_attempts"]:
            await msg.answer(text=f"Не, моё число больше, чем {guess}, попробуй ещё раз",
                             reply_markup=game_kb())
        elif guess > data["secret_number"] and data["max_attempts"]:
            await msg.answer(text=f"Не, моё число меньше, чем {guess}, попробуй ещё раз",
                             reply_markup=game_kb())
        else:
            await state.finish()
            await msg.answer("Вы исчерпали количество попыток..")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
