import json
import hmac
import hashlib
import os

import requests
from datetime import datetime, timezone, timedelta


# (2023, '1#31#1#Samsung#A500', 1)
# (2023, '1#Samsung',{A500:[1,0,2],A505:[2,1,3]})

class MDAS:
    def __init__(self, config):
        self.C = config
        self.current_date = self.get_current_date()

        self.cache_to_send = []

    @staticmethod
    def unpack_statistic_data(raw_list: list):
        # ('1#31#1#Samsung#A500', 1)
        data = {'period': raw_list[1], 'period_length': 31, 'points': {}}
        for raw_item in raw_list[2]:
            item = raw_item[0].split('#')
            day = int(item[1])
            branch = int(item[2])
            brand = item[3]
            model = item[4]
            if data['points'].get(day) is None:
                data['points'][day] = {}
            if data['points'][day].get(brand) is None:
                data['points'][day][brand] = {}
            if data['points'][day][brand].get(model) is None:
                data['points'][day][brand][model] = [0, 0, 0]
            data['points'][day][brand][model][branch - 1] += raw_item[1]
        return data

    @staticmethod
    def unpack_archive_data(raw_list: list):
        # raw_list=[2023, {'2': {'Huawei': {'p smart': [0, 1, 0], ...}, ...}, ...]
        data = {'period': raw_list[0], 'period_length': 12, 'points': raw_list[1]}
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
        """Returns: unpacked_data =
        {'year': 2023, 'month': 2, 'days': {
        1: {'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]}, ...},"""
        request = requests.get(url=f'{self.C.MDAS_URL}year-month/{year}-{month}',
                               headers={self.C.MDAS_HEADER: self.get_mdas_token()})
        print(request.status_code)
        if request.status_code == 200:
            raw_data: dict = json.loads(request.content)
            if raw_data.get('statusCode') == 200 and raw_data.get('body'):
                unpacked_data = self.unpack_statistic_data(raw_data['body'])
                # print(unpacked_data)
                return unpacked_data
        print(f'{request.content=}')

    # =======================================================================
    # ===========================  GET by YEAR  ============================
    # =======================================================================
    def request_statistic_for_year(self, year: int):
        """Returns: unpacked_data =
        {'year': 2023, 'months': {
        1: {'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]}, ...},"""
        request = requests.get(url=f'{self.C.MDAS_URL}year/{year}',
                               headers={self.C.MDAS_HEADER: self.get_mdas_token()})
        print(f'{request.status_code=}')
        if request.status_code == 200:
            raw_data: dict = json.loads(request.content)
            if raw_data.get('statusCode') == 200 and raw_data.get('body'):
                unpacked_data = self.unpack_archive_data(raw_data['body'])
                # print(unpacked_data)
                return unpacked_data
        print(f'{request.content=}')

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

    def load_month_statistic(self, year: int, month: int):
        stat_data = {}
        self.current_date = self.get_current_date()
        if year > self.current_date.year or (year == self.current_date.year and month > self.current_date.month):
            return stat_data
        self.check_and_create_folder(self.C.MDAS_PATH)

        # f'm-{year}-{month}.cache' f'y-{year}.cache'
        if 0 < month < 13:
            stat_data = self.load_stat_file(self.C.MDAS_PATH, year)
            if stat_data:
                return stat_data

            # requesting and saving file
            print(f'requesting stats for: {year}-{month}')
            stat_data = self.request_statistic_for_month(year=year, month=month)
            if not stat_data:
                return {}

            self.save_stat_file(self.C.MDAS_PATH, stat_data, year, month)
        # print(f'returning: {stat_data=}')
        return stat_data

    def load_year_statistic(self, year: int, _=None):
        stat_data = {}
        self.current_date = self.get_current_date()
        if year > self.current_date.year:
            return stat_data

        # f'y-{year}.cache'
        stat_data = self.load_stat_file(self.C.MDAS_PATH, year)
        if stat_data:
            return stat_data

        # requesting and saving file
        print(f'requesting stats for: {year}')
        stat_data = self.request_statistic_for_year(year=year)
        if not stat_data:
            return {}

        self.save_stat_file(self.C.MDAS_PATH, stat_data, year)
        # print(f'returning: {stat_data=}')
        return stat_data

    @staticmethod
    def check_and_create_folder(folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    @staticmethod
    def generate_file_names(year: int, month: int = 0) -> tuple:
        fn_part = f'm-{year}-{month}' if month else f'y-{year}'
        return f'{fn_part}.cache', f'{fn_part}.tmp'

    def load_stat_file(self, folder_path, year: int, month: int = 0):
        self.check_and_create_folder(folder_path)
        file_name, file_name_tmp = self.generate_file_names(year, month)
        # if full cache found - reading
        if os.path.exists(f'{folder_path}{file_name}'):
            print(f'reading stats from: {file_name}')
            with open(f'{folder_path}{file_name}', 'r') as cache_file:
                stat_data = json.load(cache_file)
            return stat_data
        # if temp found
        elif os.path.exists(f'{folder_path}{file_name_tmp}'):
            # ================================================== FOR TEST ONLY  #
            # with open(f'{folder_path}{file_name_tmp}', 'r') as cache_file:  #
            #     stat_data = json.load(cache_file)  #
            # return stat_data  #
            # ================================================== FOR TEST ONLY  #

            # if outdated - deleting
            if year < self.current_date.year \
                    or (year == self.current_date.year and 0 < month < self.current_date.month):
                os.remove(f'{folder_path}{file_name_tmp}')

    def save_stat_file(self, folder_path, stat_data, year: int, month: int = 0):
        self.check_and_create_folder(folder_path)
        file_name, file_name_tmp = self.generate_file_names(year, month)

        if year == self.current_date.year and (month == self.current_date.month or month == 0):
            print(f'saving stats in: {file_name_tmp}')
            with open(f'{folder_path}{file_name_tmp}', 'w') as cache_file:
                json.dump(stat_data, cache_file)
        else:
            print(f'saving stats in: {file_name}')
            with open(f'{folder_path}{file_name}', 'w') as cache_file:
                json.dump(stat_data, cache_file)
