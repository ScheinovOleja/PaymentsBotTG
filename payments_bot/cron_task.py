import datetime

from pony.orm import db_session

from payments_bot import loop, bot, config
from payments_bot.models import AllUsers


def periodic_check_user():
    with db_session:
        all_users = AllUsers.select()[:]
        date = datetime.date.today()
        for user in all_users:
            difference = user.date_of_cancel - date
            if 7 >= difference.days > 0:
                loop.run_until_complete(
                    bot.send_message(user.tg_id, 'Ваша подписка подходит к концу! Не забудьте продлить ее!'))
            elif difference.days <= 0:
                loop.run_until_complete(bot.ban_chat_member(config['channel']['id'], user.tg_id, revoke_messages=True))
                loop.run_until_complete(bot.unban_chat_member(config['channel']['id'], user.tg_id))
    print('Разбанен')


if __name__ == '__main__':
    periodic_check_user()
