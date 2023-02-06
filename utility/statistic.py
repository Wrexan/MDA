import json
import hmac
import hashlib
import os

import requests
from datetime import datetime, timezone, timedelta


class MDAS:
    def __init__(self, config):
        self.C = config

        self.cache_to_send = []

    @staticmethod
    def unpack_statistic_data(raw_list: list):
        # ('1#31#1#Samsung#A500', 1)
        data = {'year': raw_list[0], 'month': raw_list[1], 'days': {}}
        for raw_item in raw_list[2]:
            item = raw_item[0].split('#')
            day = int(item[1])
            branch = int(item[2])
            brand = item[3]
            model = item[4]
            if data['days'].get(day) is None:
                data['days'][day] = {}
            if data['days'][day].get(brand) is None:
                data['days'][day][brand] = {}
            if data['days'][day][brand].get(model) is None:
                data['days'][day][brand][model] = [0, 0, 0]
            data['days'][day][brand][model][branch - 1] += raw_item[1]
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
    def request_statistic_for_month(self, year: int, month: int):
        request = requests.get(url=f'{self.C.MDAS_URL}year-month/{year}-{month}',
                               headers={self.C.MDAS_HEADER: self.get_mdas_token()})
        print(request.status_code)
        if request.status_code == 200:
            raw_data: dict = json.loads(request.content)
            if raw_data.get('statusCode') == 200 and raw_data.get('body'):
                unpacked_data = self.unpack_statistic_data(raw_data['body'])
                # print(unpacked_data)
                return unpacked_data

    # unpacked_data = {'year': 2023, 'month': 2, 'days': {
    #             1: {
    #                 'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]},
    #                 'Samsung': {'A500': [1, 1, 0], 'M215': [1, 0, 3]},
    #                 'Huawei': {'Y5 2020': [1, 0, 0], 'Nova': [1, 2, 0]}
    #             },

    # =======================================================================
    # ===============================  PUT  =================================
    # =======================================================================

    def send_statistic_cache(self, progress, status, error):
        print(f'SENDING: {self.cache_to_send}')
        # data = {'data': ['1#Samsung#A500', '2#Xiaomi#mi8', '1#Xiaomi#mi11']}
        cache_to_send = self.cache_to_send[:]
        self.cache_to_send = []
        request = requests.post(url=self.C.MDAS_URL,
                                json={'data': cache_to_send},
                                headers={self.C.MDAS_HEADER: self.get_mdas_token()})
        raw_data: dict = json.loads(request.content)
        print(f'stat answer: {raw_data=}')
        if request.status_code != 200 or raw_data.get('statusCode') != 200:
            self.cache_to_send.extend(cache_to_send)

    def load_statistic(self, year: int, month: int = 0):
        stat_data = {}
        current_date = self.get_current_date()
        if year > current_date.year or (year == current_date.year and month > current_date.month):
            return stat_data

        if not os.path.exists(self.C.MDAS_PATH):
            os.makedirs(self.C.MDAS_PATH)
        print(f'+++++++++++++++')

        # f'm-{year}-{month}.cache' f'y-{year}.cache'
        if 0 < month < 13:
            file_name = f'm-{year}-{month}.cache'
            file_name_tmp = f'm-{year}-{month}.tmp'

            # if full cache found - reading
            if os.path.exists(f'{self.C.MDAS_PATH}{file_name}'):
                print(f'reading stats from: {file_name}')
                with open(f'{self.C.MDAS_PATH}{file_name}', 'r') as cache_file:
                    stat_data = json.load(cache_file)
                return stat_data
            # if temp found
            elif os.path.exists(f'{self.C.MDAS_PATH}{file_name_tmp}'):
                # if outdated - deleting
                if year < current_date.year or (year == current_date.year and month < current_date.month):
                    os.remove(f'{self.C.MDAS_PATH}{file_name_tmp}')

            # requesting and saving file
            print(f'requesting stats for: {year}-{month}')
            stat_data = self.request_statistic_for_month(year=year, month=month)
            if not stat_data:
                return {}

            if year == current_date.year and month == current_date.month:
                print(f'saving stats in: {file_name_tmp}')
                with open(f'{self.C.MDAS_PATH}{file_name_tmp}', 'w') as cache_file:
                    json.dump(stat_data, cache_file)
            else:
                print(f'saving stats in: {file_name}')
                with open(f'{self.C.MDAS_PATH}{file_name}', 'w') as cache_file:
                    json.dump(stat_data, cache_file)
        print(f'returning: {stat_data=}')
        return stat_data

