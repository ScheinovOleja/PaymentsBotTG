from aiogram import types
from aiogram.dispatcher import FSMContext
from pony.orm import db_session, commit

from payments_bot.models import PaymentOption
from payments_bot.states.state_menu import StepsAddPayments, AdminMenu


async def add_payments_name(query: types.CallbackQuery, state: FSMContext):
    text = "Следующим сообщением пришлите название Варианта оплаты!\n\nНазвание не должно превышать 16 символов!!!"
    await StepsAddPayments.add_name.set()
    await query.message.answer(text)


async def add_payments_link(message: types.Message, state: FSMContext):
    if len(message.text) > 16:
        text = 'Вы превысили допустимое количество символов! Повторите попытку!'
        await message.answer(text)
        return
    await state.set_data({"name": message.text})
    text = "Следующим сообщением пришлите ссылку на оплату!\nЕсли ссылки нет(криптовалюта), то укажите адрес " \
           "кошелька/id binance pay."
    await StepsAddPayments.add_link.set()
    await message.answer(text)


async def add_payments_price(message: types.Message, state: FSMContext):
    await state.update_data({"link": message.text})
    text = "Следующим сообщением пришлите цену, указанную в ссылке!\n\nЦену указывайте целым числом!"
    await StepsAddPayments.add_price.set()
    await message.answer(text)


async def add_payments_description(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except Exception as err:
        text = 'Вы ввели некорректную цену! Повторите попытку!'
        await message.answer(text)
        return
    await state.update_data({"price": price})
    text = "Следующим сообщением пришлите описание подписки!\n\nОписание не должно превышать 450 символов!"
    await StepsAddPayments.add_description.set()
    await message.answer(text)


async def add_payments_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    markup = types.InlineKeyboardMarkup()
    if len(message.text) > 450:
        text = 'Вы превысили допустимое количество символов! Повторите попытку!'
        await message.answer(text)
        return
    await state.update_data({"description": message.text})
    text = f"Оплата - {data['name']}. Цена в ссылке - {data['price']}\n\n" \
           f"Ссылка - {data['link']}.\n\n" \
           f"Описание:\n\n{message.text}\n\n" \
           f"Проверьте правильность введенных данных!"
    await StepsAddPayments.final.set()
    markup.add(
        types.InlineKeyboardButton(
            text='Все верно!',
            callback_data='confirmPayment'
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text='Я ошибся',
            callback_data='refusePayment'
        )
    )
    await message.answer(text, reply_markup=markup)


async def create_payment(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with db_session:
        PaymentOption(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            link_to_pay=data['link']
        )
        commit()
    await query.message.answer('Вариант оплаты успешно создан!')
    # ______________________________________________________________________
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
    await query.message.answer('Меню', reply_markup=markup)
