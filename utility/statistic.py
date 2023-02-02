import json
import hmac
import hashlib
import os

import requests
from datetime import date, datetime, timezone, timedelta


class MDAS:
    def __init__(self, c, send_event_timer):
        self.MDAS_URL = c.MDAS_URL
        self.MDAS_KEY = c.MDAS_KEY
        self.MDAS_HEADER = c.MDAS_HEADER
        self.send_event_timer = send_event_timer

        self.cache_to_send = []

    @staticmethod
    def unpack_statistic_data(raw_list: list):
        # ('1#31#1#Samsung#A500', 1)
        data = {'year': raw_list[0], 'month': raw_list[1]}
        for raw_item in raw_list[2]:
            item = raw_item[0].split('#')
            day = int(item[1])
            branch = int(item[2])
            brand = item[3]
            model = item[4]
            if data.get(day) is None:
                data[day] = {}
            if data[day].get(brand) is None:
                data[day][brand] = {}
            if data[day][brand].get(model) is None:
                data[day][brand][model] = [0, 0, 0]
            data[day][brand][model][branch - 1] += raw_item[1]
        return data

    def get_mdas_token(self):
        token = hmac.new(
            key=self.MDAS_KEY.encode(encoding="utf-8"),
            msg=self.get_current_date().isoformat().encode(encoding="utf-8"),
            digestmod=hashlib.md5
        ).hexdigest()
        return token

    @staticmethod
    def get_current_date():
        """current date utc+2"""
        return datetime.now(timezone(timedelta(hours=2))).date()

    def cache_item(self, branch: int, brand: str, model: str):
        # '1#Samsung#A500'
        self.cache_to_send.append(f'{branch}#{brand}#{model}')
        if len(self.cache_to_send) >= 6:
            return True

    # =======================================================================
    # ===========================  GET by MONTH  ============================
    # =======================================================================
    def get_statistic_for_month(self, year: int, month: int):
        request = requests.get(url=f'{self.MDAS_URL}year-month/{year}-{month}',
                               headers={self.MDAS_HEADER: self.get_mdas_token()})
        print(request.status_code)
        if request.status_code == 200:
            raw_data: dict = json.loads(request.content)
            if raw_data.get('body'):
                unpacked_data = self.unpack_statistic_data(raw_data['body'])
                print(unpacked_data)
    # unpacked_data = {'year': 2023, 'month': 1, 31: {
    #     'Xiaomi': {
    #         'mi8': [1, 2, 3],
    #         'mi11': [5, 0, 1]
    #     },
    #     'Samsung': {
    #         'A500': [1, 0, 0],
    #         'M215': [1, 0, 0]
    #     }}}

    # =======================================================================
    # ===============================  PUT  =================================
    # =======================================================================
    def send_statistic_cache(self):
        print(f'SENDING: {self.cache_to_send}')
        # data = {'data': ['1#Samsung#A500', '2#Xiaomi#mi8', '1#Xiaomi#mi11']}
        cache_to_send = self.cache_to_send[:]
        self.cache_to_send = []
        print(f'{cache_to_send=}')
        request = requests.post(url=self.MDAS_URL,
                                json={'data': cache_to_send},
                                headers={self.MDAS_HEADER: self.get_mdas_token()})
        print(f'{json.loads(request.content)=}')
        if request.status_code == 200 and json.loads(request.content).get('statusCode') == 200:
            self.send_event_timer.stop()
            return True
        else:
            self.cache_to_send.extend(cache_to_send)
            return False
