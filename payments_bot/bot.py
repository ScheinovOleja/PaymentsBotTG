from aiogram import Dispatcher
from aiogram.utils import executor

from payments_bot import dp, loop


async def register_handler_scenarios(dispatcher: Dispatcher):
    pass


async def register_handler_handlers(dispatcher: Dispatcher):
    pass


async def register_handler_back_handler(dispatcher: Dispatcher):
    pass


async def startup(dispatcher: Dispatcher):
    pass


async def shutdown(dispatcher: Dispatcher):
    pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=loop, on_shutdown=shutdown, on_startup=startup)