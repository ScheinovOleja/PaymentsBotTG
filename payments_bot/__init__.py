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

if not os.path.isdir(f'{os.getcwd()}/logs'):
    os.mkdir(f'{os.getcwd()}/logs')
logging.basicConfig(format="[%(asctime)s] %(levelname)s : %(name)s : %(message)s",
                    level=logging.ERROR, datefmt="%d-%m-%y %H:%M:%S", filename='logs/log_error.log')
logging.getLogger('aiogram').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
