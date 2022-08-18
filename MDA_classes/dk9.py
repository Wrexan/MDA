import requests
import traceback
from bs4 import BeautifulSoup


class DK9Parser:
    S_NO_CONN, S_PROCESS, S_OK, S_REDIRECT, S_CLI_ERR, S_SERV_ERR, S_NO_LOGIN, S_CONN_ERROR = 0, 1, 2, 3, 4, 5, 6, 7

    def __init__(self, C):
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
            print('GETTING RESPONSE')
            status.emit(self.S_PROCESS)
            # =============================================== LOGIN PAGE ==============================================
            r = self._get_response(self.LOGIN_URL, status)
            if r:
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
                if r:
                    progress.emit(80)
                    if self.addiction():
                        print('LOGIN OK')
                        self.validation_data = self._get_validation_data(BeautifulSoup(r.content, 'html.parser'))
                        self.LOGIN_SUCCESS = True
                        status.emit(self.S_OK)
                    else:
                        print('LOGIN FAIL')
                        self.validation_data = {'__VIEWSTATE': 'C78cd8ds6csC^dc7s',
                                                '__VIEWSTATEGENERATOR': '567Ddc67DS57s&&dtc',
                                                '__EVENTVALIDATION': 'cdc9796cjlmckdmjNCydc565nysdi'}
                        self.LOGIN_SUCCESS = False
                        status.emit(self.S_NO_LOGIN)
                    progress.emit(100)
        except requests.exceptions.Timeout as err:
            status.emit(self.S_NO_CONN)
            progress.emit(100)
            print(f'Error: (Timeout) on CONNECT Message:\n{str(err)}')
            return
        except Exception as err:
            if '[Errno 110' in err.__str__():
                self._110xx_error_handler(err, progress, status)
                return
            error.emit((f'Error while trying to login',
                        f'{traceback.format_exc()}'))

    def adv_search(self, type_: str, firm_: str, model_: str, description_: str, progress, status, error) -> tuple:
        if not self.LOGIN_SUCCESS:
            return ()
        print(f'Searching: {type_=}  {firm_=}  {model_=}  {description_=}\n')
        # print(f'+++++++++: {self.validation_data=}')
        progress.emit(10)
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
            status.emit(self.S_NO_CONN)
            progress.emit(100)
            print(f'Error: on CONNECT (Timeout) Message:\n{str(err)}')
            return ()
        except Exception as err:
            if '[Errno 110' in err.__str__():
                self._110xx_error_handler(err, progress, status)
                return ()
            error.emit((f'Error while trying to search:\n'
                        f'{model_}',
                        f'{traceback.format_exc()}'))

    def change_data(self, data):
        self.CDATA = data

    def _get_response(self, url, status):
        response = self.SESSION.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        print(f'{response=}')
        if 100 <= response.status_code < 200:
            status.emit(self.S_PROCESS)
            return response
        elif 200 <= response.status_code < 300:
            status.emit(self.S_PROCESS)
            return response
        elif 300 <= response.status_code < 400:
            status.emit(self.S_REDIRECT)
        elif 400 <= response.status_code < 500:
            status.emit(self.S_CLI_ERR)
        elif 500 <= response.status_code < 600:
            status.emit(self.S_SERV_ERR)

    def _110xx_error_handler(self, err, progress, status):
        if '[Errno 11001]' in err.__str__():
            status.emit(self.S_NO_CONN)
            print(f'Error: (No connection) Message :\n{str(err)}')
        else:
            status.emit(self.S_CONN_ERROR)
            print(f'Error: (Connection error) Message :\n{str(err)}')
        progress.emit(100)
