from aiogram import Dispatcher

from payments_bot import config
from payments_bot.handlers import list_subscription, list_payments
from payments_bot.states.state_menu import AdminMenu


def register_back_handler(dp: Dispatcher):
    dp.register_callback_query_handler(list_subscription,
                                       lambda query: "back" == query.data and query.from_user.id == int(
                                           config["admin"]["id"]),
                                       state=AdminMenu.info_subscription)
    dp.register_callback_query_handler(list_payments,
                                       lambda query: "back" == query.data and query.from_user.id == int(
                                           config["admin"]["id"]),
                                       state=AdminMenu.info_payments)
