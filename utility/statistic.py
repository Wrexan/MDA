import json
import hmac
import hashlib
import os

import requests
from datetime import date, datetime, timezone, timedelta


class MDAS:
    def __init__(self, config):
        self.C = config

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
            key=self.C.MDAS_KEY.encode(encoding="utf-8"),
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
        cash_len = len(self.cache_to_send)
        if cash_len < 100:
            self.cache_to_send.append(f'{branch}#{brand}#{model}')
            # Not full
            if cash_len < self.C.STAT_CACHE_SIZE:
                return 0
            # Full+
            if cash_len < (self.C.STAT_CACHE_SIZE + 3):
                return 1
            # Overflowing
            return 2
        # STOPPED Overflow
        return 3

    # =======================================================================
    # ===========================  GET by MONTH  ============================
    # =======================================================================
    def get_statistic_for_month(self, year: int, month: int):
        request = requests.get(url=f'{self.C.MDAS_URL}year-month/{year}-{month}',
                               headers={self.C.MDAS_HEADER: self.get_mdas_token()})
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
    @staticmethod
    def send_test():
        print(f'SENDING: TEST OK!!')

    def send_statistic_cache(self):
        print(f'SENDING: {self.cache_to_send}')
        # data = {'data': ['1#Samsung#A500', '2#Xiaomi#mi8', '1#Xiaomi#mi11']}
        cache_to_send = self.cache_to_send[:]
        self.cache_to_send = []
        # print(f'{cache_to_send=}')
        request = requests.post(url=self.C.MDAS_URL,
                                json={'data': cache_to_send},
                                headers={self.C.MDAS_HEADER: self.get_mdas_token()})
        print(f'{json.loads(request.content)=}')
        if request.status_code != 200 or json.loads(request.content).get('statusCode') != 200:
            self.cache_to_send.extend(cache_to_send)
