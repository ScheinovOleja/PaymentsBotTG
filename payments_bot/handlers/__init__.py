from aiogram import Dispatcher, types

from payments_bot import config
from payments_bot.handlers.handler_add_payments import add_payments_name, add_payments_link, add_payments_description, \
    add_payments_final, create_payment, add_payments_price
from payments_bot.handlers.handler_add_subscription import add_subscription_name, add_subscription_price, \
    add_subscription_months, add_subscription_description, add_subscription_final, create_subscription, \
    add_subscription_payment, delete_subscription
from payments_bot.handlers.handler_admin import confirm_paid, refuse_paid, send_menu_msg, send_menu_btn, \
    list_subscription, info_subscription, list_payments, info_payment
from payments_bot.handlers.handler_payments import send_invitation_to_pay, choice_tariff, payment_option, \
    waiting_payment_confirm, check_and_wait
from payments_bot.states.state_menu import Menu, AdminMenu, StepsAddSubscription, StepsAddPayments


def register_admin_btn(dp: Dispatcher):
    dp.register_callback_query_handler(send_menu_btn,
                                       lambda query: query.from_user.id == int(config['admin']['id']) and
                                       "main_menu" == query.data,
                                       state="*")


def register_handler(dp: Dispatcher):
    dp.register_message_handler(send_invitation_to_pay,
                                lambda message: message.from_user.id != int(config['admin']['id']),
                                state="*", commands=['start'])
    dp.register_callback_query_handler(choice_tariff, lambda query: '_tariff_' in query.data and
                                                                    query.from_user.id != int(config["admin"]["id"]),
                                       state=Menu.invitation_to_pay)
    dp.register_callback_query_handler(payment_option, lambda query: '_option' in query.data and
                                                                     query.from_user.id != int(config["admin"]["id"]),
                                       state=Menu.tariff_selection)
    dp.register_callback_query_handler(waiting_payment_confirm, lambda query: "_paid" in query.data and
                                                                              query.from_user.id != int(
        config["admin"]["id"]),
                                       state=Menu.payment_option)
    dp.register_message_handler(check_and_wait, content_types=['photo'], state=Menu.payment)


def register_admin_handler_payment(dp: Dispatcher):
    dp.register_callback_query_handler(list_payments, lambda query: "list_payments" == query.data and
                                                                    query.from_user.id == int(config["admin"]["id"]),
                                       state=AdminMenu.main_menu)
    dp.register_callback_query_handler(info_payment, lambda query: "_paymentEdit_" in query.data and
                                                                   query.from_user.id == int(config["admin"]["id"]),
                                       state=AdminMenu.list_payments)
    dp.register_callback_query_handler(add_payments_name, lambda query: "add_payment" == query.data and
                                                                        query.from_user.id == int(
        config["admin"]["id"]),
                                       state=AdminMenu.list_payments)
    dp.register_message_handler(add_payments_link, lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddPayments.add_name)
    dp.register_message_handler(add_payments_price, lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddPayments.add_link)
    dp.register_message_handler(add_payments_description, lambda message: message.from_user.id == int(
        config["admin"]["id"]),
                                state=StepsAddPayments.add_price)
    dp.register_message_handler(add_payments_final, lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddPayments.add_description)
    dp.register_callback_query_handler(create_payment,
                                       lambda query: query.data == 'confirmPayment' and
                                                     query.from_user.id == int(config["admin"]["id"]),
                                       state=StepsAddPayments.final
                                       )


def register_admin_handler_subscription(dp: Dispatcher):
    dp.register_message_handler(send_menu_msg, lambda message: message.from_user.id == int(config['admin']['id']),
                                state='*', commands=['start'])
    dp.register_callback_query_handler(list_subscription, lambda query: "list_subscription" == query.data and
                                                                        query.from_user.id == int(
        config["admin"]["id"]),
                                       state=AdminMenu.main_menu)
    dp.register_callback_query_handler(info_subscription, lambda query: "_tariffEdit_" in query.data and
                                                                        query.from_user.id == int(
        config["admin"]["id"]),
                                       state=AdminMenu.list_subscription)
    dp.register_callback_query_handler(delete_subscription, lambda query: "delete_tariff_" in query.data and
                                                                          query.from_user.id == int(
        config["admin"]["id"]),
                                       state=AdminMenu.info_subscription)
    # Процесс создания подписки
    dp.register_callback_query_handler(add_subscription_name, lambda query: "add_tariff" == query.data and
                                                                            query.from_user.id == int(
        config["admin"]["id"]),
                                       state=AdminMenu.list_subscription)
    dp.register_message_handler(add_subscription_price,
                                lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddSubscription.add_name)
    dp.register_message_handler(add_subscription_months,
                                lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddSubscription.add_price)
    dp.register_message_handler(add_subscription_description,
                                lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddSubscription.add_months)
    dp.register_message_handler(add_subscription_payment,
                                lambda message: message.from_user.id == int(config["admin"]["id"]),
                                state=StepsAddSubscription.add_description
                                )
    dp.register_callback_query_handler(add_subscription_final,
                                       lambda query: query.from_user.id == int(config["admin"]["id"]) and
                                                     "_paymentsOption" in query.data,
                                       state=StepsAddSubscription.add_payment)
    dp.register_callback_query_handler(create_subscription,
                                       lambda query: query.data == 'confirm_subscription' and
                                                     query.from_user.id == int(config["admin"]["id"]),
                                       state=StepsAddSubscription.final
                                       )
    dp.register_callback_query_handler(add_subscription_name,
                                       lambda query: query.data == 'refuse_subscription' and
                                                     query.from_user.id == int(config["admin"]["id"]),
                                       state=StepsAddSubscription.final
                                       )
    # ------------------------------------------------------------------------------------------------------------------
    dp.register_callback_query_handler(confirm_paid, lambda query: "confirm_" in query.data and
                                                                   query.from_user.id == int(config["admin"]["id"]),
                                       state="*")
    dp.register_callback_query_handler(refuse_paid, lambda query: "refuse_" in query.data and
                                                                  query.from_user.id == int(config["admin"]["id"]),
                                       state="*")
