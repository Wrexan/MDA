import requests
from bs4 import BeautifulSoup


class DK9Parser:
    S_NO_CONN, S_NO_LOGIN, S_OK, S_REDIRECT, S_CLI_ERR, S_SERV_ERR = 0, 1, 2, 3, 4, 5

    def __init__(self, login_url: str, search_url: str, headers: dict, data: dict):
        self.WIN = None
        self.LOGIN_URL = login_url
        self.SEARCH_URL = search_url
        self.HEADERS = headers
        self.DATA = data
        self.SESSION = requests.Session()
        self.validation_data: dict = {}
        self.TIMEOUT = 5

        # self.WEB_STATUSES = {0: 'Нет соединения', 1: 'Не залогинен', 2: 'Подключен',
        #                      3: 'Перенаправление', 4: 'Запрос отклонен', 5: 'Ошибка сервера'}

    def get_validation_data(self, soup: type(BeautifulSoup)):
        return {
            '__VIEWSTATE': soup.find('input', attrs={'id': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', attrs={'id': '__EVENTVALIDATION'})['value']}

    def login(self, progress, status, error):
        progress.emit(10)
        try:

            # print(f'CREATING SESSION')
            # self.SESSION = requests.Session()

            print('GETTING RESPONSE')
            status.emit(self.S_NO_LOGIN)
            r = self.get_response(self.LOGIN_URL, status)
            if r:
                progress.emit(20)
                soup = BeautifulSoup(r.content, 'html.parser')
                progress.emit(40)
                # print(f'{"*"*80}\nSOUP_LOGIN={soup}')
                # ===============================================================================================
                print(f'{self.validation_data=} {self.LOGIN_URL=} ')
                # try:
                self.SESSION.post(
                    self.LOGIN_URL,
                    data={**self.DATA, **self.get_validation_data(soup)},
                    headers=self.HEADERS,
                    timeout=self.TIMEOUT)
                progress.emit(60)
                # ===============================================================================================
                r = self.get_response(self.SEARCH_URL, status)
                if r:
                    progress.emit(90)
                    a = [len(d) for d in self.DATA.values()]
                    # print(f'{a=}')
                    if sum([len(d) for d in self.DATA.values()]) > 15:
                        print('LOGIN OK')
                        self.validation_data = \
                            self.get_validation_data(BeautifulSoup(r.content, 'html.parser'))
                        status.emit(self.S_OK)
                    else:
                        print('LOGIN FAIL')
                        self.validation_data = {'__VIEWSTATE': 'C78cd8ds6csC^dc7s',
                                                '__VIEWSTATEGENERATOR': '567Ddc67DS57s&&dtc',
                                                '__EVENTVALIDATION': 'cdc9796cjlmckdmjNCydc565nysdi'}
                        status.emit(self.S_NO_LOGIN)
                    progress.emit(100)
        # except [BaseException] as err:
        #     status.emit(self.S_NO_CONN)
        #     print(f'Error: Error while trying to connect',
        #           f'Message:\n{str(err)}')
        #     return
        except requests.exceptions.Timeout as err:
            status.emit(self.S_NO_CONN)
            print(f'Error: (Timeout) on CONNECT Message:\n{str(err)}')
            return
        except Exception as err:
            if '[Errno 11001]' in err.__str__():
                status.emit(self.S_NO_CONN)
                print(f'Error: (No connection) Message :\n{str(err)}')
                return
            print(f'Error: on LOGIN' 'Message:\n{str(err)}')
            # if hasattr(err.__dir__(), "code"):
            error.emit((f'Error {type(err)=} while trying to login:', err))

    def search(self, model: str, progress, status, error) -> tuple:
        print(f'Searching: {model}')
        progress.emit(10)
        try:
            # print(f'{"*"*80}\nSOUP_2_DEF={soup.find("div", attrs={"id": "ctl00_ContentPlaceHolder1_UpdatePanel2"})}')
            # ===============================================================================================
            data_to_send = {
                'ctl00$ContentPlaceHolder1$TextBoxAdvanced_new': str(model),
                'ctl00$ContentPlaceHolder1$ButtonSearch': 'Submit',
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
            progress.emit(50)
            # print(f'{"*" * 80}\nSOUP_3_DEF={soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})}')
            part_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})
            progress.emit(60)
            # self.fill_table_from_soup(part_table_soup, self.ui.table_parts, DK9_BG_P_COLOR1, DK9_BG_P_COLOR2)
            accessory_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView2"})
            # self.fill_table_from_soup(accessory_table_soup, self.ui.table_accesory, DK9_BG_A_COLOR1, DK9_BG_A_COLOR2)

            return part_table_soup, accessory_table_soup
            # ctl00$ContentPlaceHolder1$TextBoxAdvanced_new   строка поиска text
            # ctl00$ContentPlaceHolder1$ButtonSearch   кнопка поиска submit
            # ctl00_ContentPlaceHolder1_UpdatePanel2   div, внутри таблица,
            # ctl00_ContentPlaceHolder1_GridView1 - запчасти
            # ctl00_ContentPlaceHolder1_GridView2 - аксессуары
        except requests.exceptions.Timeout as err:
            status.emit(self.S_NO_CONN)
            print(f'Error: on CONNECT (Timeout) Message:\n{str(err)}')
            return ()
        except Exception as err:
            if '[Errno 11001]' in err.__str__():
                status.emit(self.S_NO_CONN)
                print(f'Error: (No connection) on CONNECT Message:\n{str(err)}')
                return ()
            print(f'Error: on SEARCH Message:\n{str(err)}\n{err.__str__()=}')
            error.emit((f'Error while trying to search:\n{model}', err))

    def change_data(self, data):
        print(f'{self.DATA=}')
        self.DATA = data

    def get_response(self, url, status):
        response = self.SESSION.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        print(f'{response=}')
        if 100 <= response.status_code < 200:
            status.emit(self.S_NO_CONN)
            return response
        elif 200 <= response.status_code < 300:
            status.emit(self.S_NO_LOGIN)
            return response
        elif 300 <= response.status_code < 400:
            status.emit(self.S_REDIRECT)
        elif 400 <= response.status_code < 500:
            status.emit(self.S_CLI_ERR)
        elif 500 <= response.status_code < 600:
            status.emit(self.S_SERV_ERR)
