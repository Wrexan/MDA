import encodings.mac_iceland

import requests
from bs4 import BeautifulSoup


class DK9Parser:

    def __init__(self, login_url: str, search_url: str, headers: dict, login_data: dict):
        self.LOGIN_URL = login_url
        self.SEARCH_URL = search_url
        self.HEADERS = headers
        self.LOGIN_DATA = login_data
        self.SESSION: type(requests)
        self.validation_data: dict

    def get_validation_data(self, soup: type(BeautifulSoup)):
        return {
            '__VIEWSTATE': soup.find('input', attrs={'id': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', attrs={'id': '__EVENTVALIDATION'})['value']}

    def login(self):
        try:
            self.SESSION = requests.Session()
            r = self.SESSION.get(self.LOGIN_URL, headers=self.HEADERS)
            soup = BeautifulSoup(r.content, 'html.parser')
            # print(f'{"*"*80}\nSOUP_LOGIN={soup}')
            # ===============================================================================================
            self.SESSION.post(
                self.LOGIN_URL,
                data={**self.LOGIN_DATA, **self.get_validation_data(soup)},
                headers=self.HEADERS)
            # soup = BeautifulSoup(r.content, 'html.parser')
            # print(f'{"*" * 80}\nSOUP_1_ANS={soup}')
            # encodings.mac_iceland.decoding_table
            # ===============================================================================================
            r = self.SESSION.get(self.SEARCH_URL, headers=self.HEADERS)
            self.validation_data = self.get_validation_data(BeautifulSoup(r.content, 'html.parser'))
        except Exception as err:
            print(f'ERROR while trying to login {self.LOGIN_URL} -> {err}')

    def search(self, model: str) -> tuple:
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
            soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
            # print(f'{"*" * 80}\nSOUP_3_DEF={soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})}')
            part_table_soup = soup.find("table", attrs={"id": "ctl00_ContentPlaceHolder1_GridView1"})
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
            print(f'ERROR while trying to search {self.SEARCH_URL} -> {err}')
