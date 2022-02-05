import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import xlrd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QSpacerItem, QSizePolicy, QTableWidgetItem, QHeaderView, qApp
from PyQt5 import QtCore
from bs4 import BeautifulSoup

from window_main import Ui_MainWindow

# ============================================
# ==================SETTINGS==================
REVERS_MODEL_LIST = False
STRICT_SEARCH_LEN = 2

DK9_LOGIN = 'masterP'  # admin
DK9_PASSWORD = '4832101'  # 123456

# ============================================
# ====================MENU====================
STRICT_SEARCH = True
LATIN_SEARCH = True
# ============================================
# ====================VARS====================
SEARCH_COLUMN_NUMBERS = {'+': [3, 4, 5],
                         'Alcatel': [2, 4, 7],
                         'Asus-тел': [2, 4, 7],
                         'Asus-планш': [2, 4, 7],
                         'doogee': [2, 3, 4],
                         'Huawei': [2, 5, 6],
                         'iPad': [1, 3, 5],
                         'iPhone': [1, 3, 5],
                         'Lenovo': [2, 4, 7],
                         'LG': [3, 4, 9],
                         'Meizu': [2, 3, 4],
                         'Motorola': [2, 8, 9],
                         'Nokia': [3, 5, 6],
                         'OPPO': [3, 4, 5],
                         'OnePlus': [3, 4, 5],
                         'Oukitel': [3, 4, 5],
                         'PIXEL': [3, 4, 5],
                         'Realme': [3, 4, 5],
                         'Samsung': [3, 5, 6],
                         'Sony': [2, 4, 5],
                         'XIAOMI': [2, 4, 5],
                         'ZTE': [3, 4, 5],
                         }
TRASH_IN_CELLS = ['/', '\\', 'MI2/Mi2s', 'MI2a', 'mi3', 'Mi 9t', 'Mi Max 3',
                  'Red rice', 'Redmi 3', 'Redmi 4x', 'Redmi 6', 'Redmi 7', 'Redmi 7a',
                  'Redmi 8', 'Redmi 8a', 'Redmi Note 4', 'Redmi Note 5', 'Redmi Note 6',
                  'Redmi Note 6 Pro', 'Redmi Note 7', 'Redmi Note 8', 'Redmi note 9', 'Redmi Note 6']
PRICE_PATH = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\')
PRICE_PARTIAL_NAME = ['Прайс', '.xls']


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setFocus()
        qApp.focusChanged.connect(self.on_focusChanged)

        # self.PRICE_DB = xlrd.open_workbook(sys.path[0] + '\\' + PRICE_PATH + PRICE_NAME, formatting_info=True)
        # self.PRICE_DB = xlrd.open_workbook(PRICE_PATH + price_name, formatting_info=True)
        self.models = {}
        self.ui = Ui_MainWindow()
        self.initUI()
        self.PRICE_DB = self.load_price()
        print(self.login())
        self.temp()

    def initUI(self):
        self.ui.setupUi(self)

        self.ui.input_search.textChanged[str].connect(self.search_and_upd_model_buttons)
        self.ui.table_left.verticalHeader().setDefaultSectionSize(14)
        self.ui.table_parts.verticalHeader().setDefaultSectionSize(14)
        self.ui.table_accesory.verticalHeader().setDefaultSectionSize(14)
        self.ui.table_left.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_parts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_accesory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_left.setHorizontalHeaderLabels(['Виды работ', 'Цена', 'Примечание'])
        self.ui.table_parts.setHorizontalHeaderLabels(['Тип', 'Фирма', 'Модель', 'Примечание',
                                                       'Цена', 'К-во', 'Дата', 'Где'])
        self.ui.table_accesory.setHorizontalHeaderLabels(['Тип', 'Фирма', 'Модель', 'Примечание',
                                                          'Цена', 'К-во', 'Дата', 'Где'])

    def search_and_upd_model_buttons(self, search_req):
        self.search_price_models(search_req)
        lay = self.ui.scroll_models_layout.layout()
        self.clear_layout(lay)
        if self.models:
            self.upd_model_buttons(lay)

    def search_price_models(self, search_req):
        search_req_len = len(search_req)
        if STRICT_SEARCH and search_req_len < STRICT_SEARCH_LEN: return
        search_req = search_req.lower()  # input('Введите модель: ').lower()
        # print(search_req)
        self.models = {}
        for sheet in self.PRICE_DB:
            for row_num in range(sheet.nrows):
                cell_value = sheet.row_values(row_num, 0, 2)
                # print(f'{cell_value=} {len(cell_value)=}')
                if not cell_value or not cell_value[0] or len(cell_value) < 2 or cell_value[0] in TRASH_IN_CELLS:
                    continue
                # print(f'{cell_value_0}')
                name_cell = str(cell_value[0]).strip().lower()
                a, b, = 0, len(name_cell)
                while a < b:
                    found_pos = name_cell.find(search_req, a, b)
                    # print(f'{a=} {b=} {found_pos=} {name_cell=}')
                    if found_pos == -1: break
                    # if search request > 3 symbols, cut everything from left
                    # for smaller, cut from both sides (more strict)
                    # print(f'{len(self.models)=} {self.models=} {name_cell=} {sheet=} {row_num=}')  # ERROR LOG
                    if (search_req_len > 2  # and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
                            or (search_req_len < 3 and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
                                and (found_pos + search_req_len == b or
                                     name_cell[found_pos + search_req_len] in '/\\ ' or
                                     search_req[-1] == ' '))):
                        le = len(self.models)
                        # print(f'{le=} {self.models=} {name_cell=} {sheet=} {row_num=}')
                        if le < 10:
                            self.models[name_cell] = [sheet, row_num]
                            if le == 10:
                                return
                        else:
                            return

                        # print(f'=========={name_cell}==========')
                        break
                    else:
                        a += found_pos + search_req_len

    def upd_model_buttons(self, lay):
        # lay = self.ui.scroll_models_layout.layout()
        # self.clear_layout(lay)
        sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addItem(sp)
        le = len(self.models)
        if REVERS_MODEL_LIST:
            ml = reversed(list(self.models.keys()))
        else:
            ml = list(self.models.keys())
        for model in ml:
            b = QPushButton(model)
            b.clicked.connect(self.upd_price_table)
            lay.addWidget(b, 0)
            le -= 1

    def upd_price_table(self):  # 'xiaomi mi a2 m1804d2sg'
        b = self.sender().text()
        # print(b)
        position = self.models[b]  # [Sheet 27:<XIAOMI>, 813]
        # print(f'{position=}')
        # print(f'{position[0].name=}')
        if position[0].name in SEARCH_COLUMN_NUMBERS:
            col = SEARCH_COLUMN_NUMBERS[position[0].name]  # [2, 4, 5]
        else:
            col = SEARCH_COLUMN_NUMBERS['+']
        # print(f'{col=}')
        row = position[0].row_values(position[1], 0, 9)  # ['Xiaomi Mi A2 M1804D2SG ', '', '', 0.0, '', '', '', '', '']
        # if position[1] == position[0].nrows or position[0].row_values(position[1]+1, 0, 1):
        #     print(f'{row=} {position[1] == position[0].nrows=} {position[0].row_values(position[1]+1, 0, 1)=}')
        #     return
        r = 0
        # self.ui.table_left.clearContents()
        self.ui.table_left.setRowCount(0)
        self.ui.model_lable.setText(self.list_to_string(row))
        # self.ui.table_left.setItem(r, 0, QTableWidgetItem(str(row[0])))
        # self.ui.table_left.setItem(r, 1, QTableWidgetItem(str(row[col[1] - 1])))
        for i in range(position[1], position[0].nrows - 1):
            # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
            if len(row) < (col[2]):
                # print('SHORT row:' + str(row))
                self.ui.table_left.insertRow(r)
                self.ui.table_left.setItem(r, 0, QTableWidgetItem(self.list_to_string(row)))
                return
            else:
                # print(row)
                r0 = str(row[col[0] - 1])
                r1 = str(row[col[1] - 1])
                if r0 or len(r1) > 3:
                    self.ui.table_left.insertRow(r)
                    self.ui.table_left.setItem(r, 0, QTableWidgetItem(r0))
                    self.ui.table_left.setItem(r, 1, QTableWidgetItem(r1))
                    self.ui.table_left.setItem(r, 2, QTableWidgetItem(str(row[col[2] - 1])))
                    r += 1
                    # print(row[col[0] - 1], row[col[1] - 1], row[col[2] - 1])
                if i < position[0].nrows:
                    # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
                    row = position[0].row_values(i + 1, 0, 9)
                    if row[0] != '':
                        if row[0] not in TRASH_IN_CELLS:
                            return
                    # print(row[col[0]-1, col[1]-1, col[2]-1])
                else:
                    return

    def load_price(self):
        price_name = ''
        for name in os.listdir(PRICE_PATH):
            if name[-4:] == PRICE_PARTIAL_NAME[1] and PRICE_PARTIAL_NAME[0] in name:
                price_name = name
                break
        if price_name:
            self.ui.price_name.setText(price_name)
            return xlrd.open_workbook(PRICE_PATH + price_name, formatting_info=True)
        else:
            self.ui.model_lable.setText('ОШИБКА! Файл "Прайс..xls" не найден')
            self.ui.price_name.setText('Расположите файл "Прайс..xls" на рабочем столе')
            return ''

    def login(self):
        return requests.get('http://dimkak9-001-site1.htempurl.com/Login.aspx', auth=('masterP', '4832101'))
        # response = requests.get(url, params=params, headers=headers)

    def temp(self):
        # dburi = 'http://localhost:8086/write?db=pesdb'
        # dbuser = 'pesuser'
        # dbpass = 'pespass'

        headers = {
            # 'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0'
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }

        LoginData = {
            'TextBoxName': DK9_LOGIN,
            'TextBoxPassword': DK9_PASSWORD,
            'ButtonLogin': 'Submit',
            # 'ctl00$ContentPlaceHolder1$TextBoxManufacture': 'mi8',
            # 'ctl00$ContentPlaceHolder1$ButtonSearch': 'Submit',
        }

        with requests.Session() as s:
            url = "http://dimkak9-001-site1.htempurl.com/Login.aspx"
            r = s.get(url, headers=headers)
            # print(r.text)
            soup = BeautifulSoup(r.content, 'html.parser')

            # LoginData['__VIEWSTATE'] = soup.find('input', attrs={'id': '__VIEWSTATE'})['value']
            # LoginData['__VIEWSTATEGENERATOR'] = soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value']
            # LoginData['__EVENTVALIDATION'] = soup.find('input', attrs={'id': '__EVENTVALIDATION'})['value']
            VData = {
                '__VIEWSTATE': soup.find('input', attrs={'id': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', attrs={'id': '__EVENTVALIDATION'})['value']}

            # print(f'{LoginData=} {headers=}')
            data = {**LoginData, **VData}
            r = s.post(url, data=data, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            # LoginData['Button2'] = 'Submit'
            print(f'{data=}')
            print(f'SOUP_1={soup}')


            PushButton2Data = {
                'Button2': 'submit'
            }
            data = {**PushButton2Data, **VData}
            r = s.post(url, data=data, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            # tables = soup.find_all('table')
            # print(f'{LoginData=}')
            print(f'{data=}')
            print(f'SOUP_2={soup}')
            inputs = soup.find_all('input', attrs={'type': 'text'})

            # print(f'{tables=}')
            print(f'{inputs=}')

            # MeterID = soup.find("span", id="MainContent_lblMeterID").contents[0]

            # print(f'{soup=}')
            # iframe = soup.find('iframe', attrs={'id': 'myIframe1'})
            # print(f'{iframe=}')
            # inside_frame = iframe.find('input', attrs={'name': 'ctl00$ContentPlaceHolder1$TextBoxManufacture'})
            # print(f'{inside_frame=}')

            PushSearchData = {
                'ctl00$ContentPlaceHolder1$TextBoxManufacture': 'mi8'
            }

            r = s.post(url, data=PushSearchData, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')

            # tables = soup.find_all('table')
            # tables = soup.find_all('table', attrs={'id': 'ctl00_ContentPlaceHolder1_GridView1'})

            inputs = soup.find_all('input', attrs={'type': 'text'})

            # print(f'{tables=}')
            print(f'{inputs=}')

            # print(f'{soup=}')

            # GetSearchData = {
            #     'ctl00_ContentPlaceHolder1_GridView1': 'mi8'
            # }

            # r = s.get(url, headers=headers)
            # soup = BeautifulSoup(r.content, 'html.parser')
            # table = soup.find('table', attrs={'id': 'ctl00_ContentPlaceHolder1_GridView1'})
            #
            # print(f'{table=}')
            # dbres = requests.post(dburi, data=dbpayload, auth=HTTPBasicAuth(dbuser, dbpass))
            # print(dbres.status_code)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                # print(child.widget())
                child.widget().deleteLater()

    def list_to_string(self, lst):
        return ' '.join([str(elem) for elem in lst if len(str(elem)) > 3])

    @QtCore.pyqtSlot("QWidget*", "QWidget*")
    def on_focusChanged(self, old, now):
        if now == None:
            pass
            # print(f"\nwindow is the active window: {self.isActiveWindow()}")
            # self.setWindowState(QtCore.Qt.WindowMinimized)
        else:
            self.ui.input_search.setFocus()
            self.ui.input_search.selectAll()
            # print(f"window is the active window: {self.isActiveWindow()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    window.ui.input_search.setFocus()
    sys.exit(app.exec_())
