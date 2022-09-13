from importer import *

import json
from settings import token
from vk_api.longpoll import VkLongPoll, VkEventType

vk_session = vk_api.VkApi(token = token)
longpoll = VkLongPoll(vk_session)

vk = vk_session.get_api()

def send_message(user_id, message, attachment, keyboard):
    try:
        if keyboard == '':
            vk.messages.send(
    			user_id = user_id,
    			random_id = vk_api.utils.get_random_id(),
    			message = message)
        else:
            vk.messages.send(
    			user_id = user_id,
    			message = message,
    			random_id = vk_api.utils.get_random_id(),
    			keyboard = keyboard)
    except:
        pass

def debug_message(message, keyboard=''):
    send_message(228179762, message, '', keyboard)

def get_full_user_info(user_id):
    return api.users.get(access_token=token, user_ids=str(user_id), name_case='Nom')[0]

def set_online_group(group_id=194144255):
    return api.groups.enableOnline(access_token=token, group_id=group_id)


if __name__ == "__main__":
    from commands.listCreator import *
    from commands import UseDataBase as db
    buttons = [
        [ ['Отмена', 'negative'] ],
    ]

    debug_message('В этот день нет предмета "Геометрия"\nВведи дату, когда дз будет актуально, в формате [День].[Месяц].[Год]\n(На следующий день в 3:00 по МСК дз будет удалено)', createButtons(buttons))































