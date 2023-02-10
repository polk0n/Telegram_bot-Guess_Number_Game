from aiogram import executor
from create_bot import dp
import handlers

handlers.register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
