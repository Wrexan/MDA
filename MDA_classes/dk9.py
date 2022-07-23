import requests
from bs4 import BeautifulSoup


class DK9Parser:
    S_NO_CONN, S_PROCESS, S_OK, S_REDIRECT, S_CLI_ERR, S_SERV_ERR, S_NO_LOGIN = 0, 1, 2, 3, 4, 5, 6

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

    def addiction(self):
        return sum([len(d) for d in self.DATA.values()]) > 15

    def login(self, progress, status, error):
        progress.emit(10)
        try:
            print('GETTING RESPONSE')
            status.emit(self.S_PROCESS)
            r = self.get_response(self.LOGIN_URL, status)
            if r:
                progress.emit(20)
                soup = BeautifulSoup(r.content, 'html.parser')
                progress.emit(40)
                # ===============================================================================================
                self.SESSION.post(
                    self.LOGIN_URL,
                    data={**self.DATA, **self.get_validation_data(soup)},
                    headers=self.HEADERS,
                    timeout=self.TIMEOUT)
                progress.emit(60)
                # ===============================================================================================
                r = self.get_response(self.SEARCH_URL, status)
                if r:
                    progress.emit(70)
                    if self.addiction():
                        print('LOGIN OK')
                        self.validation_data = self.get_validation_data(BeautifulSoup(r.content, 'html.parser'))
                        status.emit(self.S_OK)
                    else:
                        print('LOGIN FAIL')
                        self.validation_data = {'__VIEWSTATE': 'C78cd8ds6csC^dc7s',
                                                '__VIEWSTATEGENERATOR': '567Ddc67DS57s&&dtc',
                                                '__EVENTVALIDATION': 'cdc9796cjlmckdmjNCydc565nysdi'}
                        status.emit(self.S_NO_LOGIN)
                    progress.emit(100)
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
            error.emit((f'Error {type(err)=} while trying to login:', err))

    # def switch_to_adv_search(self, status, error) -> bool:
    #     print(f'Switching to advanced search')
    #     try:
    #         # ===============================================================================================
    #         data_to_send = {
    #             'ctl00$ContentPlaceHolder1$CheckBox1': 'Submit'
    #         }
    #         print(f'Sending: POST')
    #         r = self.SESSION.post(
    #             self.SEARCH_URL,
    #             data={**data_to_send, **self.validation_data},
    #             headers=self.HEADERS,
    #             timeout=self.TIMEOUT)
    #         # progress.emit(20)
    #         # print(f'Answer: {r}')
    #         soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
    #         panel_3 = soup.find("div", attrs={"id": "ctl00_ContentPlaceHolder1_Panel3"})
    #         # print(panel_3)
    #         # check if we got page with adv search fields
    #         if panel_3:
    #                 # and 'ctl00$ContentPlaceHolder1$TextBoxType_new' in panel_3.contents \
    #                 # and 'ctl00$ContentPlaceHolder1$TextBoxManufacture_new' in panel_3.contents \
    #                 # and 'ctl00$ContentPlaceHolder1$TextBoxModel_new' in panel_3.contents \
    #                 # and 'ctl00$ContentPlaceHolder1$TextBoxDescription_new' in panel_3.contents:
    #             # print('ADV OK')
    #             return True
    #         else:
    #             error.emit((f'Error while trying to turn on advanced search:', 'Page not found'))
    #             return False
    #         # ctl00$ContentPlaceHolder1$CheckBox1   advanced search checkbox
    #     except requests.exceptions.Timeout as err:
    #         status.emit(self.S_NO_CONN)
    #         print(f'Error: on CONNECT (Timeout) Message:\n{str(err)}')
    #         return False
    #     except Exception as err:
    #         if '[Errno 11001]' in err.__str__():
    #             status.emit(self.S_NO_CONN)
    #             print(f'Error: (No connection) on CONNECT Message:\n{str(err)}')
    #             return False
    #         print(f'Error while trying to switch to advanced search:\n{str(err)}\n{err.__str__()=}')
    #         error.emit((f'Error while trying to switch to advanced search:', err))

    def adv_search(self, type_: str, firm_: str, model_: str, description_: str, progress, status, error) -> tuple:
        print(f'Searching: {type_=}  {firm_=}  {model_=}  {description_=}')
        progress.emit(10)
        try:
            # print(f'{"*"*80}\nSOUP_2_DEF={soup.find("div", attrs={"id": "ctl00_ContentPlaceHolder1_UpdatePanel2"})}')
            # ===============================================================================================
            data_to_send = {
                'ctl00$ContentPlaceHolder1$CheckBox1': 'Submit',
                'ctl00$ContentPlaceHolder1$ButtonSearch': 'Submit',
                'ctl00$ContentPlaceHolder1$TextBoxType_new': type_,
                'ctl00$ContentPlaceHolder1$TextBoxManufacture_new': firm_,
                'ctl00$ContentPlaceHolder1$TextBoxModel_new': model_,
                'ctl00$ContentPlaceHolder1$TextBoxDescription_new': description_,
            }
            # if type_:
            #     data_to_send['ctl00$ContentPlaceHolder1$TextBoxType_new'] = type_
            # if firm_:
            #     data_to_send['ctl00$ContentPlaceHolder1$TextBoxManufacture_new'] = firm_
            # if model_:
            #     data_to_send['ctl00$ContentPlaceHolder1$TextBoxModel_new'] = model_
            # if description_:
            #     data_to_send['ctl00$ContentPlaceHolder1$TextBoxDescription_new'] = description_

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
            print(f'Error: on CONNECT (Timeout) Message:\n{str(err)}')
            return ()
        except Exception as err:
            if '[Errno 11001]' in err.__str__():
                status.emit(self.S_NO_CONN)
                print(f'Error: (No connection) on CONNECT Message:\n{str(err)}')
                return ()
            print(f'Error: on SEARCH Message:\n{str(err)}\n{err.__str__()=}')
            error.emit((f'Error while trying to search:\n{model_}', err))

    # def search(self, model_: str, progress, status, error) -> tuple:
    #     print(f'Searching: {model_}')
    #     progress.emit(10)
    #     try:
    #         # print(f'{"*"*80}\nSOUP_2_DEF={soup.find("div", attrs={"id": "ctl00_ContentPlaceHolder1_UpdatePanel2"})}')
    #         # ===============================================================================================
    #         data_to_send = {
    #             'ctl00$ContentPlaceHolder1$TextBoxAdvanced_new': str(model_),
    #             'ctl00$ContentPlaceHolder1$ButtonSearch': 'Submit',
    #         }
    #         print(f'Sending: POST')
    #         r = self.SESSION.post(
    #             self.SEARCH_URL,
    #             data={**data_to_send, **self.validation_data},
    #             headers=self.HEADERS,
    #             timeout=self.TIMEOUT)
    #         progress.emit(20)
    #         # print(f'Answer: {r}')
    #         soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
    #         progress.emit(50)
    #         # print(f'{"*" * 80}\nSOUP_3_DEF={soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})}')
    #         part_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})
    #         progress.emit(60)
    #         # self.fill_table_from_soup(part_table_soup, self.ui.table_parts, DK9_BG_P_COLOR1, DK9_BG_P_COLOR2)
    #         accessory_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView2"})
    #         # self.fill_table_from_soup(accessory_table_soup, self.ui.table_accesory, DK9_BG_A_COLOR1, DK9_BG_A_COLOR2)
    #
    #         return part_table_soup, accessory_table_soup
    #         # ctl00$ContentPlaceHolder1$TextBoxAdvanced_new   строка поиска text
    #         # ctl00$ContentPlaceHolder1$ButtonSearch   кнопка поиска submit
    #         # ctl00_ContentPlaceHolder1_UpdatePanel2   div, внутри таблица,
    #         # ctl00_ContentPlaceHolder1_GridView1 - запчасти
    #         # ctl00_ContentPlaceHolder1_GridView2 - аксессуары
    #     except requests.exceptions.Timeout as err:
    #         status.emit(self.S_NO_CONN)
    #         print(f'Error: on CONNECT (Timeout) Message:\n{str(err)}')
    #         return ()
    #     except Exception as err:
    #         if '[Errno 11001]' in err.__str__():
    #             status.emit(self.S_NO_CONN)
    #             print(f'Error: (No connection) on CONNECT Message:\n{str(err)}')
    #             return ()
    #         print(f'Error: on SEARCH Message:\n{str(err)}\n{err.__str__()=}')
    #         error.emit((f'Error while trying to search:\n{model_}', err))

    def change_data(self, data):
        self.DATA = data

    def get_response(self, url, status):
        response = self.SESSION.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        print(f'{response=}')
        if 100 <= response.status_code < 200:
            status.emit(self.S_PROCESS)
            return response
        elif 200 <= response.status_code < 300:
            status.emit(self.S_OK)
            return response
        elif 300 <= response.status_code < 400:
            status.emit(self.S_REDIRECT)
        elif 400 <= response.status_code < 500:
            status.emit(self.S_CLI_ERR)
        elif 500 <= response.status_code < 600:
            status.emit(self.S_SERV_ERR)
