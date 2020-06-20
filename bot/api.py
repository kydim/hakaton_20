from enum import Enum
import logging
import requests
import json
import os
from parser import extractor
from random import shuffle

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)10s- %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

URL = 'http://localhost:5555/'


def get_model_result():
    filename = os.path.join('model_result', 'prediction.json')
    with open(filename) as f:
        data = json.load(f)

    for i in data:
        i['text'] = ''

    res = [i for i in data if i['label'] is not None]

    return res


MODEL_RESULT = get_model_result()


class Status(Enum):
    init = 'init'
    wait_metro = 'wait_metro'
    wait_category = 'wait_category'
    looking = 'looking'


class BotText(Enum):
    init_query = "Какую категорию продуктов Вы ищите?"
    wait_metro_query = "Введите Вашу станцию метро?"

    @staticmethod
    def get_goal(text):
        return f"Хорошо, ищем '{text}' ..."


class Client:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.status = Status.init.value
        self.bot_text = BotText.init_query.value
        self.user_query = None
        self.search_good = None
        self.search_station = None
        self.result = None

    @property
    def text_search(self):
        return f"Хорошо, ищем '{self.search_good}' у станции метро '{self.search_station}' ..."

    @property
    def data(self):
        return dict(self.__dict__.items())

    def get_result(self):
        res_all = [i['url'] for i in MODEL_RESULT if i['label'] == self.search_good.lower()]
        logger.info(f'len(res)= {len(res_all)}')
        res = res_all[:5]
        shuffle(res)
        if res:
            res_str = ', '.join(res)
            return f'Нашлось! Приятного аппетитиа! {res_str}'
        else:
            return 'Увы, ничего поблизости нет'


test_client = Client(None)


def get_state(chat_id):
    # state = requests.get(f'{URL}/get_state/{chat_id}')
    test_client.chat_id = chat_id
    logger.info(test_client.data)
    return test_client


def reset():
    global test_client
    test_client = Client(None)


def update_state(chat_id, status, bot_text=None, user_query=None):
    if test_client.status == Status.init.value:
        logger.info('0')
        test_client.status = Status.wait_metro.value
        test_client.bot_text = BotText.wait_metro_query.value
    elif test_client.status == Status.wait_metro.value:
        logger.info('1')
        test_client.search_station = user_query
        test_client.status = Status.wait_category.value
        test_client.bot_text = BotText.init_query.value
    elif status == Status.wait_category.value:
        logger.info('2')
        test_client.search_good = user_query
        test_client.status = Status.looking.value
        test_client.bot_text = test_client.text_search
        # test_client.bot_text = BotText.get_goal(user_query)
    else:
        test_client.status = Status.init.value
        test_client.bot_text = BotText.init_query.value

    return test_client


def get_result():
    return test_client.get_result()


def get_nearest_station():
    nearest = extractor.get_nearest_stations_from_text(
        test_client.search_station, "Москва", threshold=0.06
    )
    if nearest:
        result = [i['name'] for i in nearest][:5]
    else:
        result = ''
    res_str = ', '.join(result)
    return f'Ближайшие станции метро: {res_str}'

    # n_stations = extractor.get_nearest_stations(test_client.search_station)
    # s_stations = ', '.join(n_stations)
    # result = f'Ближайшие станции {s_stations}'
    # return result
