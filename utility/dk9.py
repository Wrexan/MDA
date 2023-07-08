import json

import requests
import traceback
from bs4 import BeautifulSoup


class DK9Parser:
    def __init__(self, C):
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
        self.TIMEOUT = 5
        self.LOGIN_SUCCESS = False

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
                    if self.addiction():
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
                        status.emit(self.STATUS.NO_LOGIN)
                    progress.emit(100)
                    return
                else:
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
            if '[Errno 110' in err.__str__():
                self._error_handler(progress, status, err)
                return
            error.emit((f'Error while trying to login',
                        f'{traceback.format_exc()}'))

    def adv_search(self, type_: str, firm_: str, model_: str, description_: str, progress, status, error) -> tuple:
        if not self.LOGIN_SUCCESS:
            return ()
        status.emit(self.STATUS.UPDATING)
        progress.emit(10)
        print(f'Searching: {type_=}  {firm_=}  {model_=}  {description_=}\n')
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
            return ()
        except Exception as err:
            if '[Errno 110' in err.__str__():
                self._error_handler(progress, status, err)
                return ()
            error.emit((f'Error while trying to search:\n'
                        f'{model_}',
                        f'{traceback.format_exc()}'))

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
            with open(f'{self.C.DK9_CACHE_FILE}', 'r', encoding='utf-8') as cache_file:
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
                                                  f'{self.C.DK9_CACHE_FILE} '
                                                  f'{traceback.format_exc()}')
            # error.emit((f'Error while trying to load database cache:\n'
            #             f'{C.DK9_CACHE_FILE}',
            #             f'{traceback.format_exc()}'))

    @staticmethod
    def cache_is_valid(cache):
        if not isinstance(cache, dict):
            return False
        for key, value_type in {'updated': str, 'parts': list, 'accessories': list}:
            if key not in cache:
                return False
            if not isinstance(cache[key], value_type):
                return False
        return True

    def write_cache_file(self, progress, status, error):
        status.emit(self.DK9.STATUS.FILE_WRITE)
        progress.emit(10)
        try:
            with open(f'{self.C.DK9_CACHE_FILE}', 'w', encoding='utf-8') as cache_file:
                progress.emit(50)
                json.dump(self.cache, cache_file, ensure_ascii=False)
            progress.emit(100)
            status.emit(self.DK9.STATUS.FILE_UPDATED)
        except Exception as _err:
            status.emit(self.DK9.STATUS.FILE_WRITE_ERR)
            error.emit((f'Error while trying to save database cache:\n'
                        f'{self.C.DK9_CACHE_FILE}',
                        f'{traceback.format_exc()}'))

    def search_rows_in_cache_dict(self):
        print(f'Searching in cache: {self.app.curr_manufacturer} {self.app.curr_model}')
        if self.app.curr_model and self.app.curr_manufacturer:
            return \
                self.search_rows_in_cache_table(self.cache['parts']), \
                self.search_rows_in_cache_table(self.cache['accessories'])
        else:
            return \
                self.cache['parts'], \
                self.cache['accessories']

    def search_rows_in_cache_table(self, table: list):
        rows = []
        for row in table:
            if self.app.curr_manufacturer.lower() == row[2].lower() \
                    and self.app.curr_model.lower() in row[3].lower():
                rows.append(row)
        return rows
