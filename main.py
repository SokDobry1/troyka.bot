from importer import *

from threading import Thread

from vk_api.longpoll import VkLongPoll, VkEventType
import message_handler
from vkapi import longpoll

if __name__ == '__main__':
    while True:
        try:
            for event in longpoll.listen():
                #Если пришло новое сообщение
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = {"body": event.text,
                                "user_id": event.user_id}
                        try:
                            request.update({"payload": event.payload})
                        except:
                            pass
                        
                        message_handler.create_answer(request)
        except: from vkapi import longpoll