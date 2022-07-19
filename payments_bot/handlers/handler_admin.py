import calendar
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from pony.orm import db_session, commit

from payments_bot import bot, config
from payments_bot.models import Tariffs, PaymentOption, AllUsers
from payments_bot.states.state_menu import AdminMenu

main_menu_btn = types.InlineKeyboardButton(
    text='В главное меню',
    callback_data='main_menu'
)
back_btn = types.InlineKeyboardButton(
    text='Назад',
    callback_data='back'
)


async def send_menu_msg(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text=f'Список подписок',
            callback_data="list_subscription"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text=f'Список возможностей оплаты',
            callback_data="list_payments"
        )
    )
    await AdminMenu.first()
    await message.answer('Меню', reply_markup=markup)


async def send_menu_btn(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text=f'Список подписок',
            callback_data="list_subscription"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text=f'Список возможностей оплаты',
            callback_data="list_payments"
        )
    )
    await AdminMenu.first()
    await query.message.edit_text('Меню', reply_markup=markup)


async def list_subscription(query: types.CallbackQuery, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    with db_session:
        all_tariffs = Tariffs.select()[:]
    if len(all_tariffs) > 0:
        for tariff in all_tariffs:
            markup.add(
                types.InlineKeyboardButton(
                    text=f"{tariff.name} - {tariff.price} USD",
                    callback_data=f'{tariff.id}' + '_tariffEdit_' + f'{tariff.price}'
                )
            )
    markup.add(
        types.InlineKeyboardButton(
            text='Добавить подписку',
            callback_data='add_tariff'
        )
    )
    markup.add(
        main_menu_btn
    )
    await AdminMenu.list_subscription.set()
    await query.message.edit_text('Список подписок', reply_markup=markup)


async def list_payments(query: types.CallbackQuery, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    with db_session:
        all_option = PaymentOption.select()[:]
    if len(all_option) > 0:
        for option in all_option:
            markup.add(
                types.InlineKeyboardButton(
                    text=f"{option.name} - {option.price}",
                    callback_data=f'{option.id}' + '_paymentEdit_'
                )
            )
    markup.add(
        types.InlineKeyboardButton(
            text='Добавить вариант оплаты',
            callback_data='add_payment'
        )
    )
    markup.add(
        main_menu_btn
    )
    await AdminMenu.list_payments.set()
    await query.message.edit_text('Список вариантов оплаты', reply_markup=markup)


async def info_subscription(query: types.CallbackQuery, state: FSMContext):
    tariff_id = query.data.split("_tariffEdit_")[0]
    markup = types.InlineKeyboardMarkup()
    with db_session:
        tariff = Tariffs.select(lambda tariffs: tariffs.id == tariff_id)[:][0]
    text = f"Подписка на {tariff.months} месяцев!\n\n" \
           f"Цена: {tariff.price} USD!\n\n" \
           f"Описание:\n" \
           f"{tariff.description}"
    markup.add(
        types.InlineKeyboardButton(
            text='Удалить подписку',
            callback_data=f'delete_tariff_{tariff_id}'
        )
    )
    markup.add(
        main_menu_btn, back_btn
    )
    await AdminMenu.info_subscription.set()
    await query.message.edit_text(text, reply_markup=markup)


async def info_payment(query: types.CallbackQuery, state: FSMContext):
    option_id = query.data.split("_paymentEdit_")[0]
    markup = types.InlineKeyboardMarkup()
    with db_session:
        option = PaymentOption.select(lambda options: options.id == option_id)[:][0]
    text = f"Оплата {option.name}. Цена, указанная в ссылке - {option.price}\n\n" \
           f"Ссылка для оплаты: {option.link_to_pay}\n\n" \
           f"Описание:\n" \
           f"{option.description}"
    markup.add(
        types.InlineKeyboardButton(
            text='Удалить вариант оплаты',
            callback_data='delete_option'
        )
    )
    markup.add(
        main_menu_btn, back_btn
    )
    await AdminMenu.info_payments.set()
    await query.message.edit_text(text, reply_markup=markup)


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


async def confirm_paid(query: types.CallbackQuery, state: FSMContext):
    channel_obj = await bot.create_chat_invite_link(config['channel']['id'],
                                                    expire_date=datetime.datetime.now() + datetime.timedelta(days=1),
                                                    member_limit=1)
    with db_session:
        user = AllUsers.get(tg_id=query.data.split('_')[1])
        data = await state.get_data(user.tg_id)
        date = datetime.date.today()
        test_date = add_months(date, data['months'])
        user.date_of_cancel = test_date
        commit()
    await bot.send_message(query.data.split('_')[1], f'Ваша ссылка для вступления в канал: {channel_obj.invite_link}')
    await query.message.edit_reply_markup(None)


async def refuse_paid(query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(query.data.split('_')[1], f'К сожалению, мы не смогли проверить вашу оплату.')
    await query.message.edit_reply_markup(None)
