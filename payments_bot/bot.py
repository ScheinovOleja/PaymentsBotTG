from aiogram import Dispatcher
from aiogram.utils import executor

from payments_bot import dp, loop, logger_info, logger_error
from payments_bot.back_handlers import register_back_handler
from payments_bot.handlers import register_handler, register_admin_handler_subscription, register_admin_handler_payment, \
    register_admin_btn
from payments_bot.models import db


async def register_handler_handlers(dispatcher: Dispatcher):
    register_handler(dispatcher)
    register_admin_handler_subscription(dispatcher)
    register_admin_handler_payment(dispatcher)
    register_admin_btn(dispatcher)


async def register_handler_back_handler(dispatcher: Dispatcher):
    register_back_handler(dispatcher)


async def startup(dispatcher: Dispatcher):
    try:
        db.generate_mapping(create_tables=True)
        await register_handler_handlers(dispatcher)
        await register_handler_back_handler(dispatcher)
    except Exception as err:
        logger_error.error(err)
    logger_info.info('Start bot')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    logger_info.info('Stop bot. Storage closed.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=loop, on_shutdown=shutdown, on_startup=startup)
