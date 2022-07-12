# Процесс создания подписки
from aiogram import types
from aiogram.dispatcher import FSMContext
from pony.orm import db_session, commit

from payments_bot.models import Tariffs, PaymentOption
from payments_bot.states.state_menu import StepsAddSubscription, AdminMenu


async def add_subscription_name(query: types.CallbackQuery, state: FSMContext):
    text = "Следующим сообщением пришлите название подписки!\n\nНазвание не должно превышать 16 символов!!!"
    await StepsAddSubscription.add_name.set()
    await query.message.answer(text)


async def add_subscription_price(message: types.Message, state: FSMContext):
    if len(message.text) > 16:
        text = 'Вы превысили допустимое количество символов! Повторите попытку!'
        await message.answer(text)
        return
    await state.set_data({"name": message.text})
    text = "Следующим сообщением пришлите числом цену за подписку!(450)\n\nЦена должна быть указана в USD целым числом!"
    await StepsAddSubscription.add_price.set()
    await message.answer(text)


async def add_subscription_months(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except Exception as err:
        text = 'Вы ввели некорректное число! Повторите попытку!'
        await message.answer(text)
        return
    await state.update_data({"price": price})
    text = "Следующим сообщением пришлите количество месяцев действия подписки целым числом!(2)\n\nЕсли подписка " \
           "дается навсегда, то укажите число -1"
    await StepsAddSubscription.add_months.set()
    await message.answer(text)


async def add_subscription_description(message: types.Message, state: FSMContext):
    try:
        months = int(message.text)
    except Exception as err:
        text = 'Вы ввели некорректное число! Повторите попытку!'
        await message.answer(text)
        return
    await state.update_data({"months": months})
    text = "Следующим сообщением пришлите описание подписки!\n\nОписание не должно превышать 450 символов"
    await StepsAddSubscription.add_description.set()
    await message.answer(text)


async def add_subscription_payment(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    if len(message.text) > 450:
        text = 'Вы превысили допустимое количество символов! Повторите попытку!'
        await message.answer(text)
        return
    await state.update_data({"description": message.text})
    with db_session:
        all_options = PaymentOption.select()[:]
    for option in all_options:
        markup.add(
            types.InlineKeyboardButton(
                text=f"{option.name} - {option.price}",
                callback_data=f"{option.id}_paymentsOption"
            )
        )
    await StepsAddSubscription.add_payment.set()
    text = "Выберите вариант оплаты, который будет привязан к текущей подписке."
    await message.answer(text, reply_markup=markup)


async def add_subscription_final(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data({"payment_id": query.data.split("_paymentsOption")[0]})
    markup = types.InlineKeyboardMarkup()
    text = f"Подписка - {data['name']}\n\n" \
           f"Цена - {data['price']}. Длительность подписки - {data['months']}.\n\n" \
           f"Описание:\n\n{data['description']}\n\n" \
           f"Проверьте правильность введенных данных!"
    await StepsAddSubscription.final.set()
    markup.add(
        types.InlineKeyboardButton(
            text='Все верно!',
            callback_data='confirm_subscription'
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text='Я ошибся',
            callback_data='refuse_subscription'
        )
    )
    await query.message.answer(text, reply_markup=markup)


async def create_subscription(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with db_session:
        Tariffs(
            name=data['name'],
            price=data['price'],
            months=data['months'],
            description=data['description'],
            payment=data['payment_id']
        )
        commit()
    await query.message.answer('Подписка была успешно создана!')
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


async def delete_subscription(query: types.CallbackQuery, state: FSMContext):
    tariff_id = query.data.split('delete_tariff_')[1]
    with db_session:
        tariff = Tariffs.select(lambda tariffs: tariffs.id == tariff_id)[:][0]
        tariff.delete()
        commit()
    await query.message.answer('Подписка была успешно удалена!')
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
