import configparser
import datetime
import os

import psycopg2
from pony.orm import Database, PrimaryKey, Required, Optional

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings/config.cfg'))
con = psycopg2.connect(**config['database'])

db = Database()
db.bind(**config['database'], provider='postgres')


class AllUsers(db.Entity):
    _table_ = 'users'
    id = PrimaryKey(int, auto=True)
    tg_id = Required(int, nullable=False, index=True, size=64)
    username = Required(str, nullable=True)
    date_of_cancel = Optional(datetime.date, nullable=True)


class Tariffs(db.Entity):
    _table_ = 'tariffs'
    id = PrimaryKey(int, auto=True)
    name = Required(str, nullable=False, unique=True)
    price = Required(int, nullable=False)
    months = Required(int, nullable=False)
    description = Required(str, nullable=False)
    payment = Required('PaymentOption')


class PaymentOption(db.Entity):
    _table_ = 'payment_option'
    id = PrimaryKey(int, auto=True)
    tariff_id = Optional(Tariffs)
    name = Required(str, nullable=False, unique=True)
    description = Required(str, nullable=False)
    price = Required(int, nullable=False)
    link_to_pay = Required(str, nullable=True)
