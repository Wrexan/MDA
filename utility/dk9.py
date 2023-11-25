import json
from datetime import datetime

import requests
import traceback
from bs4 import BeautifulSoup

from utility.config import DK9_CACHE_FILE_PATH
from utility.utils import save_error_file, is_error_ignored, PartFields


class DK9Parser:
    def __init__(self, C):
        self.C = C
        self.STATUS = DK9Status
        self.CACHE = DK9Cache(C, self)
        self.LOGIN_URL = C.DK9_LOGIN_URL
        self.LOGGED_IN_URL = C.DK9_LOGGED_IN_URL
        self.SEARCH_URL = C.DK9_SEARCH_URL
        self.HEADERS = C.DK9_HEADERS
        self.CDATA = C.c_data()
        self.RDATA = C.r_data()
        self.SESSION = requests.Session()
        self.validation_data: dict = {}
        self.TIMEOUT = 30
        self.LOGIN_SUCCESS = False
        self.LAST_ERROR_PAGE_TEXT = ''

        # self.WEB_STATUSES = {0: 'Нет соединения', 1: 'Не залогинен', 2: 'Подключен',
        #                      3: 'Перенаправление', 4: 'Запрос отклонен', 5: 'Ошибка сервера'}

    @staticmethod
    def _get_validation_data(soup: type(BeautifulSoup)):
        return {
            '__VIEWSTATE': soup.find('input', attrs={'id': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', attrs={'id': '__EVENTVALIDATION'})['value']}

    def addiction(self):
        return sum([len(d) for d in self.CDATA.values()]) > 15

    def _send_dk9_post(self, url, data, validation_data):
        self.SESSION.post(
            url,
            data={**data, **validation_data},
            headers=self.HEADERS,
            timeout=self.TIMEOUT)

    def login(self, progress, status, error):
        progress.emit(10)
        try:
            print('GETTING LOGIN RESPONSE')
            status.emit(self.STATUS.CONNECTING)
            # =============================================== LOGIN PAGE ==============================================
            r = self._get_response(self.LOGIN_URL, status)
            if r and r.__dict__['url'] == self.LOGIN_URL:
                progress.emit(20)
                soup = BeautifulSoup(r.content, 'html.parser')
                progress.emit(40)
                # ============================================= LOGOUT ================================================
                if soup.find("a", attrs={"id": "LinkButton1"}):
                    data_to_logout = {'LinkButton1': 'Submit'}
                    self._send_dk9_post(self.LOGGED_IN_URL, data_to_logout, self._get_validation_data(soup))
                    r = self._get_response(self.LOGIN_URL, status)
                    soup = BeautifulSoup(r.content, 'html.parser')
                # ============================================= LOGIN ==================================================
                self._send_dk9_post(self.LOGIN_URL, self.RDATA, self._get_validation_data(soup))
                progress.emit(60)
                # ============================================== READY =================================================
                r = self._get_response(self.SEARCH_URL, status)
                if r and r.__dict__['url'] == self.SEARCH_URL:
                    progress.emit(80)
                    if self.addiction() and self.C.APPROVED:
                        print('LOGIN OK')
                        self.validation_data = self._get_validation_data(BeautifulSoup(r.content, 'html.parser'))
                        self.LOGIN_SUCCESS = True
                        status.emit(self.STATUS.OK)
                    else:
                        print('LOGIN FAIL')
                        self.validation_data = {'__VIEWSTATE': 'C78cd8ds6csC^dc7s',
                                                '__VIEWSTATEGENERATOR': '567Ddc67DS57s&&dtc',
                                                '__EVENTVALIDATION': 'cdc9796cjlmckdmjNCydc565nysdi'}
                        self.LOGIN_SUCCESS = False
                        status.emit(self.STATUS.LOGIN_FAIL)
                    progress.emit(100)
                    return
                else:
                    self.LAST_ERROR_PAGE_TEXT = self.get_text_from_html_body(soup)
                    save_error_file(f'LOGIN FAIL{self.LAST_ERROR_PAGE_TEXT}')
                    self._error_handler(progress, status, err=f'Cannot connect to: {str(self.SEARCH_URL)}')
                    return
            else:
                self._error_handler(progress, status, err=f'Cannot connect to: {str(self.LOGIN_URL)}')
                return
        except requests.exceptions.Timeout as err:
            self._error_handler(progress, status, err=f'Timeout on CONNECT Message:\n{str(err)}',
                                emit=self.STATUS.NO_CONN)
            return
        except Exception as err:
            print(err.__str__())
            # self.save_error_file(f'{err.__str__()}\n{traceback.format_exc()}')  # -------------
            if is_error_ignored(err.__str__()):
                self._error_handler(progress, status, err)
                return
            save_error_file(f'{err.__str__()}\n{traceback.format_exc()}')
            error.emit((f'Error while trying to login', f'{traceback.format_exc()}'))

    def adv_search(self, type_: str, firm_: str, model_: str, description_: str, progress, status, error) \
            -> tuple or None:
        if not self.LOGIN_SUCCESS:
            return
        status.emit(self.STATUS.UPDATING)
        progress.emit(10)
        print(f'Searching: {type_=}  {firm_=}  {model_=}  {description_=}')
        # print(f'+++++++++: {self.validation_data=}')
        try:
            # ===============================================================================================
            data_to_send = {
                'ctl00$ContentPlaceHolder1$CheckBox1': 'Submit',
                'ctl00$ContentPlaceHolder1$ButtonSearch': 'Submit',
                'ctl00$ContentPlaceHolder1$TextBoxType_new': type_,
                'ctl00$ContentPlaceHolder1$TextBoxManufacture_new': firm_,
                'ctl00$ContentPlaceHolder1$TextBoxModel_new': model_,
                'ctl00$ContentPlaceHolder1$TextBoxDescription_new': description_,
            }
            print(f'Sending: POST')
            r = self.SESSION.post(
                self.SEARCH_URL,
                data={**data_to_send, **self.validation_data},
                headers=self.HEADERS,
                timeout=self.TIMEOUT)
            progress.emit(20)
            # print(f'Answer: {r}')
            soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
            # print(f'Search Title: {soup.title}')
            progress.emit(50)
            part_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})
            progress.emit(60)
            accessory_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView2"})
            if part_table_soup is None or accessory_table_soup is None:
                title = soup.title.string
                if title and 'login' in title.lower():
                    self.LOGIN_SUCCESS = False
                else:
                    self.LAST_ERROR_PAGE_TEXT = self.get_text_from_html_body(soup)
                    save_error_file(f'LOGIN FAIL{self.LAST_ERROR_PAGE_TEXT}')
                    status.emit(self.STATUS.SERV_ERR)

            return part_table_soup, accessory_table_soup
            # ctl00$ContentPlaceHolder1$ButtonSearch   кнопка поиска submit
            # ----------type----------
            # <input name="ctl00$ContentPlaceHolder1$TextBoxType_new" type="text"
            # id="ctl00_ContentPlaceHolder1_TextBoxType_new" style="width:64%;">
            # ----------firm----------
            # <input name="ctl00$ContentPlaceHolder1$TextBoxManufacture_new" type="text" value="xiaomi"
            # id="ctl00_ContentPlaceHolder1_TextBoxManufacture_new" style="width:64%;">
            # ----------model----------
            # <input name="ctl00$ContentPlaceHolder1$TextBoxModel_new" type="text" value="mi8"
            # id="ctl00_ContentPlaceHolder1_TextBoxModel_new" style="width:64%;">
            # ----------description----------
            # <input name="ctl00$ContentPlaceHolder1$TextBoxDescription_new" type="text"
            # id="ctl00_ContentPlaceHolder1_TextBoxDescription_new" style="width:64%;">
        except requests.exceptions.Timeout as err:
            self._error_handler(progress, status, err=f'Timeout on CONNECT Message:\n{str(err)}',
                                emit=self.STATUS.NO_CONN)
            return
        except Exception as err:
            print(err.__str__())
            # self.save_error_file(f'{err.__str__()}\n{traceback.format_exc()}')  # -------------
            if is_error_ignored(err.__str__()):
                self._error_handler(progress, status, err)
                return
            save_error_file(f'Error while trying to search: {model_}\n{err.__str__()}\n{traceback.format_exc()}')
            error.emit((f'Error while trying to search:\n'
                        f'{model_}',
                        f'{traceback.format_exc()}'))

    @staticmethod
    def get_text_from_html_body(soup):
        body = soup.find('body')
        for junk in body.find_all('input'):
            junk.extract()
        if body:
            return " ".join(body.text.split())[:2000]
        return ''

    @staticmethod
    def check_soups_is_broken(soups):
        if isinstance(soups, tuple):
            for soup in soups:
                if not soup:
                    print(f'one of soups is empty:{soup}')
                    return True
        else:
            print(f'soups is empty:{soups}')
            return True

    def change_data(self, data):
        self.CDATA = data

    def _get_response(self, url, status):
        response = self.SESSION.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        # print(f'{response.__dict__=}')
        if 100 <= response.status_code < 200:
            status.emit(self.STATUS.CONNECTING)
            return response
        elif 200 <= response.status_code < 300:
            status.emit(self.STATUS.CONNECTING)
            return response
        elif 300 <= response.status_code < 400:
            status.emit(self.STATUS.REDIRECT)
        elif 400 <= response.status_code < 500:
            status.emit(self.STATUS.CLI_ERR)
        elif 500 <= response.status_code < 600:
            status.emit(self.STATUS.SERV_ERR)

    def _error_handler(self, progress, status, err=None, emit=None):
        if err and '[Errno 11001]' in err.__str__():
            status.emit(self.STATUS.NO_CONN)
            print(f'Error: (No connection) Message :\n - {str(err)}')
        else:
            status.emit(emit or self.STATUS.CONN_ERROR)
            print(f'Error: (Connection error) Message :\n - {str(err)}')
        progress.emit(100)


class DK9Status:
    NO_CONN = 0
    CONNECTING = 1
    OK = 2
    REDIRECT = 3
    CLI_ERR = 4
    SERV_ERR = 5
    NO_LOGIN = 6
    CONN_ERROR = 7
    FILE_READ = 8
    FILE_WRITE = 9
    FILE_READ_ERR = 10
    FILE_WRITE_ERR = 11
    FILE_UPDATED = 12
    FILE_USED_OFFLINE = 13
    UPDATING = 14
    LOGIN_FAIL = 15


class DK9Cache:
    def __init__(self, Config, DK9):
        self.cache = {}
        self.cache_update_time = 0
        self.C = Config
        self.DK9 = DK9
        self.app = None

    def set_app(self, app):
        self.app = app

    def read_cache_file(self, progress, status, error):
        status.emit(self.DK9.STATUS.FILE_READ)
        progress.emit(10)
        try:
            with open(DK9_CACHE_FILE_PATH, 'r', encoding='utf-8') as cache_file:
                progress.emit(30)
                temp_cache = json.load(cache_file)
                progress.emit(50)
            if not self.cache_is_valid(temp_cache):
                raise Exception('Database cache file is not valid')
            self.cache.clear()
            progress.emit(70)
            self.cache = temp_cache
            progress.emit(100)
            status.emit(self.DK9.STATUS.FILE_USED_OFFLINE)
        except Exception as _err:
            status.emit(self.DK9.STATUS.FILE_READ_ERR)
            if self.app.ui:
                self.app.ui.web_status.setToolTip(f'Error while trying to load database cache: '
                                                  f'{DK9_CACHE_FILE_PATH} '
                                                  f'{traceback.format_exc()}')
            # error.emit((f'Error while trying to load database cache:\n'
            #             f'{C.DK9_CACHE_FILE}',
            #             f'{traceback.format_exc()}'))

    @staticmethod
    def cache_is_valid(cache):
        if not isinstance(cache, dict):
            return False
        for key, value_type in {'updated': str, 'parts': list, 'accessories': list}.items():
            if key not in cache:
                return False
            if not isinstance(cache[key], value_type):
                return False
        return True

    def write_cache_file(self, progress, status, error):
        status.emit(self.DK9.STATUS.FILE_WRITE)
        progress.emit(10)
        try:
            with open(DK9_CACHE_FILE_PATH, 'w', encoding='utf-8') as cache_file:
                progress.emit(50)
                json.dump(self.cache, cache_file, ensure_ascii=False)
            progress.emit(100)
            status.emit(self.DK9.STATUS.FILE_UPDATED)
        except Exception as _err:
            status.emit(self.DK9.STATUS.FILE_WRITE_ERR)
            error.emit((f'Error while trying to save database cache:\n'
                        f'{DK9_CACHE_FILE_PATH}',
                        f'{traceback.format_exc()}'))

    def search_rows_in_cache_dict(
            self,
            device_fields: PartFields,
            compatible_parts: [PartFields],
            advanced: bool = False,
    ):
        print(f'Searching in cache: {device_fields}')
        if any(device_fields.fields):
            if advanced:
                return (self.advanced_search_rows_in_cache_table(self.cache['parts'], device_fields),
                        self.advanced_search_rows_in_cache_table(self.cache['accessories'], device_fields))
            elif device_fields.model and device_fields.brand:
                return (self.search_rows_in_cache_table(self.cache['parts'], device_fields, compatible_parts),
                        self.search_rows_in_cache_table(self.cache['accessories'], device_fields, compatible_parts))
        return self.cache['parts'], self.cache['accessories']

    @staticmethod
    def search_rows_in_cache_table(
            table: list,
            search_fields: PartFields,
            compatible_parts: [PartFields],
    ) -> list:
        rows = []
        # print(f'+++{table[0]=}  {self.app.compatible_parts=}  ')
        for row in table:
            # print(f'{row=}')
            part = row[1].casefold()
            brand = row[2].casefold()
            model = row[3].casefold()
            note = row[4].casefold()
            if search_fields.brand == brand:
                if search_fields.model in model or search_fields.model in note:
                    rows.append(row)
                    continue

            for compatible_part in compatible_parts:
                # print(f'+++{compatible_part=}')
                if compatible_part.brand == brand and compatible_part.model == model:
                    if compatible_part.part in part:
                        # print(f'+++{row=}')
                        # and compatible_part.note == note
                        row.append(-666)
                        rows.append(row)

        return rows

    @staticmethod
    def advanced_search_rows_in_cache_table(
            table: list,
            search_fields: PartFields,
    ) -> list:
        rows = []
        # print(f'+++{table[0]=}  {self.app.compatible_parts=}  ')
        for row in table:
            # print(f'{row=}')
            part = row[1].casefold()
            brand = row[2].casefold()
            model = row[3].casefold()
            note = row[4].casefold()
            if not ((search_fields.part and search_fields.part not in part)
                    or (search_fields.brand and search_fields.brand not in brand)
                    or (search_fields.model and search_fields.model not in model)
                    or (search_fields.note and search_fields.note not in note)):
                rows.append(row)

        return rows

    # def get_cache_update_signals(self, result_to=None):
    #     signals = WorkerSignals()
    #     if result_to:
    #         signals.result.connect(result_to)
    #     signals.progress.connect(self.web_progress_bar)
    #     signals.finished.connect(self.dk9_finish_progress_bar)
    #     signals.error.connect(self.error)
    #     signals.status.connect(self.update_web_status)
    #     return signals
    #
    # def update_cache_start_worker(self):
    #     self.request_worker = Worker()
    #     signals = self.get_cache_update_signals(result_to=self.dk9_parse_and_start_saving)
    #     self.request_worker.add_task(DK9.adv_search, signals, 2, '', '', '', '')  # Empty request to get all
    #     print('Starting thread to search for dk9 cache')
    #     self.thread.start(self.request_worker, priority=QtCore.QThread.Priority.HighestPriority)
    #
    # def read_cache_start_worker(self):
    #     self.file_io_worker = Worker()
    #     signals = self.get_cache_update_signals()
    #     self.file_io_worker.add_task(DK9.CACHE.read_cache_file, signals, 1)
    #     print('Starting thread to read dk9 cache')
    #     self.thread.start(self.file_io_worker, priority=QtCore.QThread.Priority.HighestPriority)
    #
    # def write_cache_start_worker(self):
    #     self.file_io_worker = Worker()
    #     signals = self.get_cache_update_signals()
    #     self.file_io_worker.add_task(DK9.CACHE.write_cache_file, signals, 1)
    #     print('Starting thread to write dk9 cache')
    #     self.thread.start(self.file_io_worker, priority=QtCore.QThread.Priority.HighestPriority)

    def cache_search_parse_save_handler(self, progress, status, error):
        soups = self.DK9.adv_search('', '', '', '', progress, status, error)
        print(f'dk9_parse_and_start_saving')
        # return if any part of answear is empty
        if self.DK9.check_soups_is_broken(soups):
            return
        self.parse_soups_to_dict(soups, progress, status, error)
        self.write_cache_file(progress, status, error)

    def parse_soups_to_dict(self, soups, progress, status, error):
        print(f'parse_soups_to_dict')
        self.cache['updated'] = datetime.now().strftime("%H:%M %d.%m")
        for num, table_name in enumerate(('parts', 'accessories')):
            try:
                temp_cache = []
                # if not soups[num]:  # ERROR - Empty database
                #     print(f'ERROR: Empty database page for {table_name}')
                #     error.emit((f'Error parsing web database page to cache.:\n'
                #                 f'This page is empty: {table_name}',
                #                 f'{traceback.format_exc()}'))
                #     return
                print(f'Start parsing database page for {table_name}')
                for dk9_row in soups[num].tr.next_siblings:
                    if repr(dk9_row)[0] == "'":
                        # print(f'Excluded row: {dk9_row}')
                        # if C.DK9_COLORED and dk9_row.attrs:
                        continue
                    row_style = dk9_row.get('style')
                    row_palette = self.C.get_color_from_style(row_style) if row_style else 0
                    row = dk9_row.findAll('td')
                    row_data = [row_palette]
                    for dk9_td in row:
                        current_cell_text = str(dk9_td.string)
                        # current_cell_text = current_cell_text.encode().decode('utf-8')
                        if row_palette:
                            row_data.append(current_cell_text)
                        elif dk9_td.attrs and 'style' in dk9_td.attrs:
                            style = str(dk9_td['style'])
                            cell_palette = self.C.get_color_from_style(style)
                            row_data.append((current_cell_text, cell_palette))
                        else:
                            row_data.append(current_cell_text)
                    temp_cache.append(row_data)
                    # temp_cache.append((*row_data,))
                self.cache[table_name] = temp_cache
            except Exception as _err:
                error.emit((f'Error parsing web database page to cache.:\n'
                            f'Page: {table_name}',
                            f'{traceback.format_exc()}'))

        print(f'Done parsing database to cache')

    # def dk9_upd_caching_schedule(self, period=C.DK9_CACHING_PERIOD * 60_000):
    #     print(f'dk9_upd_caching_schedule')
    #     self.dk9_cache_timer.stop()
    #     self.dk9_update_cache_start_worker()
    #     self.dk9_cache_timer.start(C.DK9_CACHING_PERIOD * 1_000)  # * 60_000
