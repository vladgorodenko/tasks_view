from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session
from chatbot import settings
from chatbot.vk_cake_bot import Bot, Event
from chatbot.cake_bot_service import GiftCardMaker

engine = create_engine(URL(**settings.DB_CONNECTION_STRING), echo=False)


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        session = Session(engine)
        test_func(*args, **kwargs)
        session.rollback()
        session.close()

    return wrapper


class Test1(TestCase):
    RAW_EVENT = [4, 656, 17, 526812127, 1582111822, 'Oops', {'title': ' ... '}, {}, 0]

    INPUTS = [
        'Цена',
        'Да',
        '89143334411'
    ]

    EXPECTED_OUTPUTS = [
        'Вот примерные цены на основной ассортимент:\n• Бисквитный- 1400 р/ кг \n• С чизкейком внутри-1600р/кг \n'
        '• Капкейки от 200р/шт (минимальный заказ 6 шт) \n• Мини-тортики от 250р/шт(минимальный заказ 6 шт) \n'
        '• Трайфлы 200р/шт (минимальный заказ 6 шт)\n• Кейк-попсы 150-200р(минимальный заказ 12шт)\n\n'
        'Цены могут меняться как в большую так и в меньшую сторону в зависимости от дополнительных пожеланий\n\n'
        'Если, хотите, мы можем позвонить вам и рассказать подробнее?',
        'Напишите, пожалуйста ваш номер телефона',
        'Как мы можем к вам обращаться?',
    ]

    def test_ok(self):
        count = 5
        events = [{}] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('chatbot.vk_cake_bot.VkApi'):
            with patch('chatbot.vk_cake_bot.VkLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '', '')
                bot.on_event = Mock()
                bot.run()
                bot.on_event.assert_called()
                bot.on_event.call_count == count

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            raw = deepcopy(self.RAW_EVENT)
            raw[5] = input_text
            events.append(Event(raw))

        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('chatbot.vk_cake_bot.VkLongPoll', return_value=long_poller_listen_mock):
            bot = Bot('', '', engine)
            bot.api = api_mock
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])

        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        gift_card = GiftCardMaker().create_salescard(0)

        with open('./external_data/images/giftcards/salescard_0.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
            assert gift_card.read() == expected_bytes
