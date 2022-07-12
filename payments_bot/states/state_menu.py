from aiogram.dispatcher.filters.state import StatesGroup, State


class Menu(StatesGroup):
    invitation_to_pay = State()
    tariff_selection = State()
    payment_option = State()
    payment = State()


class AdminMenu(StatesGroup):
    main_menu = State()
    list_subscription = State()
    info_subscription = State()
    create_subscription = State()
    list_payments = State()
    info_payments = State()
    create_payments = State()


class StepsAddSubscription(StatesGroup):
    add_name = State()
    add_price = State()
    add_months = State()
    add_description = State()
    add_payment = State()
    final = State()


class StepsAddPayments(StatesGroup):
    add_name = State()
    add_link = State()
    add_price = State()
    add_description = State()
    final = State()
