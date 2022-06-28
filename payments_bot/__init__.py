import asyncio
import configparser
import logging
import os

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings/config.cfg'))

loop = asyncio.get_event_loop()
bot = Bot(token=config['bot']['API_TOKEN'], parse_mode=types.ParseMode.HTML)
storage = RedisStorage2('localhost', 6379, db=2)
dp = Dispatcher(bot, storage=storage, loop=loop)
dp.middleware.setup(LoggingMiddleware())

if not os.path.isdir(f'{os.getcwd()}/payments_bot/logs'):
    os.mkdir(f'{os.getcwd()}/payments_bot/logs')
# Логгер INFO
logger_info = logging.getLogger('log_info')
logger_info.setLevel(logging.INFO)
# Логгер ERROR
logger_error = logging.getLogger('log_error')
logger_error.setLevel(logging.ERROR)
# Файлы логгера
fh_info = logging.FileHandler(f'{os.getcwd()}/payments_bot/logs/log_info.log')
fh_info.setLevel(logging.INFO)
fh_error = logging.FileHandler(f'{os.getcwd()}/payments_bot/logs/log_error.log')
fh_error.setLevel(logging.ERROR)
# Формат логгера
fmtstr = "[%(asctime)s] %(levelname)s : %(name)s : %(message)s"
fmtdate = "%d-%m-%y %H:%M:%S"
formatter = logging.Formatter(fmtstr, fmtdate)
# Установка формата логгера
fh_info.setFormatter(formatter)
fh_error.setFormatter(formatter)
# Инициализация логгера
logger_info.addHandler(fh_info)
logger_error.addHandler(fh_error)
