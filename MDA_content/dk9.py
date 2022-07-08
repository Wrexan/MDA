import requests
from bs4 import BeautifulSoup
from MDA_content.windows import Messages as M


class DK9Parser:

    def __init__(self, login_url: str, search_url: str, headers: dict, login_data: dict):
        self.LOGIN_URL = login_url
        self.SEARCH_URL = search_url
        self.HEADERS = headers
        self.LOGIN_DATA = login_data
        self.SESSION: type(requests) = ()
        self.validation_data: dict = {}

    def get_validation_data(self, soup: type(BeautifulSoup)):
        return {
            '__VIEWSTATE': soup.find('input', attrs={'id': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', attrs={'id': '__EVENTVALIDATION'})['value']}

    def login(self, progress_callback):
        progress_callback.emit(10)
        try:
            self.SESSION = requests.Session()
            r = self.SESSION.get(self.LOGIN_URL, headers=self.HEADERS)
            progress_callback.emit(20)
            soup = BeautifulSoup(r.content, 'html.parser')
            progress_callback.emit(40)
            # print(f'{"*"*80}\nSOUP_LOGIN={soup}')
            # ===============================================================================================
            self.SESSION.post(
                self.LOGIN_URL,
                data={**self.LOGIN_DATA, **self.get_validation_data(soup)},
                headers=self.HEADERS)
            progress_callback.emit(60)
            # soup = BeautifulSoup(r.content, 'html.parser')
            # print(f'{"*" * 80}\nSOUP_1_ANS={soup}')
            # encodings.mac_iceland.decoding_table
            # ===============================================================================================
            r = self.SESSION.get(self.SEARCH_URL, headers=self.HEADERS)
            progress_callback.emit(90)
            self.validation_data = self.get_validation_data(BeautifulSoup(r.content, 'html.parser'))
            progress_callback.emit(100)
        except Exception as err:
            M.warning(f'Error while trying to login as:\n{self.LOGIN_DATA}',
                      f'Message:\n{err}')

    def search(self, model: str, progress_callback) -> tuple:
        print(f'Searching: {model}')
        progress_callback.emit(10)
        try:
            # print(f'{"*"*80}\nSOUP_2_DEF={soup.find("div", attrs={"id": "ctl00_ContentPlaceHolder1_UpdatePanel2"})}')
            # ===============================================================================================
            data_to_send = {
                'ctl00$ContentPlaceHolder1$TextBoxAdvanced_new': str(model),
                'ctl00$ContentPlaceHolder1$ButtonSearch': 'Submit',
            }
            r = self.SESSION.post(
                self.SEARCH_URL,
                data={**data_to_send, **self.validation_data},
                headers=self.HEADERS)
            progress_callback.emit(20)
            soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
            progress_callback.emit(50)
            # print(f'{"*" * 80}\nSOUP_3_DEF={soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})}')
            part_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})
            progress_callback.emit(60)
            # self.fill_table_from_soup(part_table_soup, self.ui.table_parts, DK9_BG_P_COLOR1, DK9_BG_P_COLOR2)
            accessory_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView2"})
            # self.fill_table_from_soup(accessory_table_soup, self.ui.table_accesory, DK9_BG_A_COLOR1, DK9_BG_A_COLOR2)

            return part_table_soup, accessory_table_soup
            # ctl00$ContentPlaceHolder1$TextBoxAdvanced_new   строка поиска text
            # ctl00$ContentPlaceHolder1$ButtonSearch   кнопка поиска submit
            # ctl00_ContentPlaceHolder1_UpdatePanel2   div, внутри таблица,
            # ctl00_ContentPlaceHolder1_GridView1 - запчасти
            # ctl00_ContentPlaceHolder1_GridView2 - аксессуары
        except Exception as err:
            M.warning(f'Error while trying to search:\n{model}',
                      f'Message:\n{err}')
