import vk
from vk.exceptions import VkAPIError
import json
import os
import re

import logging
from time import sleep
from config import (
    VK_TOKEN, VK_API_VERSION, VK_CLUBS
)
from parser.client import Client


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

client_db = Client()


def get_api():
    session = vk.Session(access_token=VK_TOKEN)
    vk_api_v = VK_API_VERSION or 5.21
    return vk.API(session, v=vk_api_v)


def load_all_vk_data(init_load=True, max_count=100, default_offset=0):
    vk_api = get_api()
    res = []

    for club in VK_CLUBS:
        offset = default_offset
        logger.info(f'get data from {club}')
        try_count = 0

        data_all = []
        while True:
            try:
                if init_load:
                    data = vk_api.wall.get(
                        domain=club,
                        count=100,
                        offset=offset,
                    )
                    offset += 100
                    data_all.extend(data['items'])
                    print(f'data_all count: {len(data_all)}')
                    if len(data_all) > max_count:
                        break

            except VkAPIError as e:
                logger.debug(e)
                try_count += 1
                logger.debug(f'sleep {try_count} sek')
                sleep(try_count)
                if try_count > 3:
                    raise

        res.append(
            {
                'source': club,
                'data': data_all,
            }
        )

    return res


def load_to_file():
    data = load_all_vk_data(max_count=30000)
    filename = os.path.join(os.path.dirname(__file__), 'vk_clubs_data', 'sharingfood.json')
    with open(filename, 'w') as f:
        logger.info(f'save data from {filename} ..')
        json.dump(data, f, ensure_ascii=False)


def init_db(from_vk=True):
    filename = os.path.join(os.path.dirname(__file__), 'vk_clubs_data', 'sharingfood.json')
    if from_vk:
        data = load_all_vk_data()
    else:
        with open(filename) as f:
            data = json.load(f)
            for i in data:
                logger.info(f'insert into db')
                client_db.write_to_hakaton_db(collection='posts', data=i['data'])


if __name__ == '__main__':
    load_to_file()
