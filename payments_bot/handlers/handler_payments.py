from aiogram import types
from aiogram.dispatcher import FSMContext
from pony.orm import db_session, commit

from payments_bot import logger_error, bot, config
from payments_bot.models import AllUsers, Tariffs, PaymentOption
from payments_bot.states.state_menu import Menu


async def send_invitation_to_pay(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    with db_session:
        try:
            if not AllUsers.get(tg_id=message.from_user.id) and not message.from_user.is_bot:
                AllUsers(tg_id=message.from_user.id,
                         username=message.from_user.username if message.from_user.username else '-')
                commit()
        except Exception as err:
            logger_error.error(err)
            return
        for tariff in Tariffs.select().order_by(Tariffs.id)[:]:
            markup.add(
                types.InlineKeyboardButton(
                    text=f"{tariff.name} - {tariff.price} USD",
                    callback_data=f'{tariff.id}' + '_tariff_' + f'{tariff.price}')
            )
    await Menu.first()
    await message.answer('Подпишитесь на канал "Заметки трейдера™️🔖" и чат "Трейдерский деск™", нажав кнопку ниже ⤵️',
                         reply_markup=markup)


async def choice_tariff(query: types.CallbackQuery, state: FSMContext):
    await state.set_data({'tariff': query.data.split('_tariff_')[0], "price": query.data.split('_tariff_')[1]})
    data = await state.get_data()
    markup = types.InlineKeyboardMarkup()
    with db_session:
        for payment_option in PaymentOption.select().order_by(PaymentOption.id)[:]:
            markup.add(
                types.InlineKeyboardButton(
                    text=f'{payment_option.name}',
                    callback_data=f"{payment_option.id}" + '_option'
                )
            )
        tariff = Tariffs.select(lambda tariffs: tariffs.id == data['tariff'])[:][0]
    await Menu.next()
    text = f"Подписка - {tariff.name} на {tariff.months} месяца.\n" \
           f"Стоимость - {tariff.price} USD.\n\n" \
           f"{tariff.description}"
    await query.message.edit_text(text, reply_markup=markup)


async def payment_option(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    markup = types.InlineKeyboardMarkup()
    with db_session:
        tariff = Tariffs.select(lambda tariffs: tariffs.id == data['tariff'])[:][0]
        option = PaymentOption.select(lambda options: options.tariff_id == tariff)[:][0]
        markup.add(
            types.InlineKeyboardButton(
                text=f'Я оплатил',
                callback_data=f"{query.from_user.id}" + "_paid"
            )
        )
    await Menu.next()
    text = f"Оплата - {option.link_to_pay}\n\n" \
           f"{option.description}"
    await query.message.edit_text(text, reply_markup=markup)


async def waiting_payment_confirm(query: types.CallbackQuery, state: FSMContext):
    await Menu.last()
    await query.message.edit_text('Пришлите скриншот чека, подтверждающего вашу оплату.')


async def check_and_wait(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text=f'Подтвердить',
            callback_data=f"confirm_{message.from_user.id}"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text=f'Отказать',
            callback_data=f"refuse_{message.from_user.id}"
        )
    )
    await bot.send_photo(config["admin"]["id"], message.photo[-1].file_id,
                         caption=f'Пользователь: '
                                 f'{"@" + message.from_user.username if message.from_user.username else message.from_user.url}',
                         reply_markup=markup)
    await message.answer('Спасибо за предоставленный чек. Как только мы проверим вашу оплату, мы выдадим вам '
                         'доступ в канал')
