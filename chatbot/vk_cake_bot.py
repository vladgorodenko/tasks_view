# Нет же особой разницы что продавать? Пусть будут торты
from re import search
from random import randint
import requests
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, Event
import logging
from chatbot import settings
from chatbot.dialog_agent import DialogFlowAssistent
from sqlalchemy import create_engine
from chatbot.cake_bot_service import DatabaseUpdater
from sqlalchemy.engine.url import URL

try:
    import settings
except ImportError:
    exit('copy settings.py.default into settings.py, set token and database connection string')

log = logging.getLogger("cake_bot")


def configure_logging():
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler("cake_bot.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('|%(name)s|: %(asctime)s %(levelname)s %(message)s',
                                                "%Y-%m-%d %H:%M"))
    log.addHandler(file_handler)


class Bot:
    """
    Use python3.8
    echo-bot for vk.com

    :param group_id:
    :param token:
    """

    def __init__(self, group_id, token, db_engine):
        self.group_id = group_id
        self.token = token

        self.vk = VkApi(token=token)
        self.long_poller = VkLongPoll(self.vk)
        self.api = self.vk.get_api()
        self.engine = db_engine

    def run(self):
        """

        running cake_bot
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)

            except Exception:
                log.exception("Ошибка в обработке события")

    def send_image(self, path_image_to_send, user_id):
        with open(path_image_to_send, 'rb') as image:
            upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
            upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
            image_data = self.api.photos.saveMessagesPhoto(**upload_data)
            attachment = f'photo{image_data[0]["owner_id"]}_{image_data[0]["id"]}'
        self.api.messages.send(attachment=attachment,
                               random_id=randint(0, 2 ** 30),
                               peer_id=user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(message=text_to_send,
                               random_id=randint(0, 2 ** 30),
                               peer_id=user_id)

    def on_event(self, event):
        """
        return message, if text

        :param Event object:
        :return None:
        """
        if not event.to_me:
            log.debug(f'Неизвестное событие {event.type}')
            return

        inputed_text = event.raw[5].lower()
        user_id = event.peer_id
        image = './external_data/images/giftcards/salescard_52681212715.png'

        user_data = self.api.users.get(user_ids=(user_id))

        assistent = DialogFlowAssistent(user_id)
        answer_text, params = assistent.get_answer(inputed_text=inputed_text)
        self.send_text(answer_text, user_id)

        if not DatabaseUpdater(self.engine).check_user_id(user_id):
            DatabaseUpdater(self.engine).append_customer(user_data)
            card_num = DatabaseUpdater(self.engine).get_giftcard_number(user_id)

            if card_num is not None:
                image = f'./external_data/images/giftcards/salescard_{card_num}.png'
            self.send_text('Благодарим вас за проявленный к нам интерес. Вот ваша индивидуальная скидка:', user_id)
            self.send_image(image, user_id)


if __name__ == '__main__':
    configure_logging()
    engine = create_engine(URL(**settings.DB_CONNECTION_STRING), echo=False)
    bot = Bot(group_id=settings.GROUP_ID, token=settings.TOKEN, db_engine=engine)
    bot.run()
#зачёт!