import os
import sys
import configparser
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QSpacerItem, QSizePolicy, QTableWidgetItem, QHeaderView, qApp
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt

from content.dk9 import DK9Parser
from content.price import Price
from content.window_main import Ui_MainWindow

# from win32com.client import GetObject

# ============================================
# ==================SETTINGS==================
DK9_LOGIN = 'masterP'
DK9_PASSWORD = '4832101'

MODEL_LIST_SIZE = 15

# tables
PRICE_COLORED = True  # work slower if True
DK9_COLORED = True  # work slower if True
DK9_COL_DIFF = 14  # difference of odd/even bg
TABLE_FONT_SIZE = 12

# ============================================
# ====================MENU====================
STRICT_SEARCH = True
LATIN_SEARCH = True
# ============================================
# ====================VARS====================
PATH = QtCore.QFileInfo(__file__).absolutePath()
MODEL_LIST_REVERSED = False
STRICT_SEARCH_LEN = 2  # start search after 2 symbols
PRICE_SEARCH_COLUMN_NUMBERS = {'+': [3, 4, 5],
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
PRICE_TRASH_IN_CELLS = ('/', '\\', 'MI2/Mi2s', 'MI2a', 'mi3', 'Mi 9t', 'Mi Max 3',
                        'Red rice', 'Redmi 3', 'Redmi 4x', 'Redmi 6', 'Redmi 7', 'Redmi 7a',
                        'Redmi 8', 'Redmi 8a', 'Redmi Note 4', 'Redmi Note 5', 'Redmi Note 6',
                        'Redmi Note 6 Pro', 'Redmi Note 7', 'Redmi Note 8', 'Redmi note 9', 'Redmi Note 6')
PRICE_PATH = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\')
PRICE_PARTIAL_NAME = ('Прайс', '.xls')

# Preparing background colors for DK9
DK9_BG_P_COLOR1 = (204, 204, 255)
DK9_BG_P_COLOR2 = (DK9_BG_P_COLOR1[0] - DK9_COL_DIFF if DK9_BG_P_COLOR1[0] >= DK9_COL_DIFF else 0,
                   DK9_BG_P_COLOR1[1] - DK9_COL_DIFF if DK9_BG_P_COLOR1[1] >= DK9_COL_DIFF else 0,
                   DK9_BG_P_COLOR1[2] - DK9_COL_DIFF if DK9_BG_P_COLOR1[2] >= DK9_COL_DIFF else 0)
DK9_BG_A_COLOR1 = (204, 255, 153)
DK9_BG_A_COLOR2 = (DK9_BG_A_COLOR1[0] - DK9_COL_DIFF if DK9_BG_A_COLOR1[0] >= DK9_COL_DIFF else 0,
                   DK9_BG_A_COLOR1[1] - DK9_COL_DIFF if DK9_BG_A_COLOR1[1] >= DK9_COL_DIFF else 0,
                   DK9_BG_A_COLOR1[2] - DK9_COL_DIFF if DK9_BG_A_COLOR1[2] >= DK9_COL_DIFF else 0)

DK9_BG_COLORS = {'GreenYellow': (173, 255, 47),
                 'LightBlue': (173, 216, 230),
                 'Goldenrod': (218, 165, 32),
                 'Red': (255, 80, 80),
                 }
DK9_LOGIN_URL = "http://dimkak9-001-site1.htempurl.com/Login.aspx"
DK9_SEARCH_URL = "http://dimkak9-001-site1.htempurl.com/AllInOne.aspx"
DK9_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Firefox/10.0'}

DK9_LOGIN_DATA = {
    'TextBoxName': DK9_LOGIN,
    'TextBoxPassword': DK9_PASSWORD,
    'ButtonLogin': 'Submit',
}


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setFocus()
        self.setWindowIcon(QtGui.QIcon(f'{PATH}/content/start.png'))
        qApp.focusChanged.connect(self.on_focusChanged)

        # self.PRICE_DB = xlrd.open_workbook(sys.path[0] + '\\' + PRICE_PATH + PRICE_NAME, formatting_info=True)
        # self.PRICE_DB = xlrd.open_workbook(PRICE_PATH + price_name, formatting_info=True)
        self.prepare_columns()
        self.models = {}
        self.model_buttons = {}
        self.current_model_button_index = 0
        self.ui = Ui_MainWindow()
        self.initUI()
        self.SESSION = None
        self.validation_data = None
        self.old_search = ''
        # print('Creating DK9')
        self.DK9 = DK9Parser(DK9_LOGIN_URL, DK9_SEARCH_URL, DK9_HEADERS, DK9_LOGIN_DATA)
        print('Login to DK9')
        self.DK9.login()
        print('Loading Price')
        self.Price = Price(PRICE_PATH, PRICE_PARTIAL_NAME, PRICE_TRASH_IN_CELLS)
        self.ui.price_name.setText(self.Price.message)
        # self.update_dk9_data('mi8 lite')

    def initUI(self):
        self.ui.setupUi(self)

        font = QtGui.QFont()
        # font.setBold(True)
        font.setPixelSize(TABLE_FONT_SIZE)

        self.ui.input_search.textChanged[str].connect(self.search_and_upd_model_buttons)
        self.ui.table_left.verticalHeader().setDefaultSectionSize(TABLE_FONT_SIZE + 4)
        self.ui.table_parts.verticalHeader().setDefaultSectionSize(TABLE_FONT_SIZE + 4)
        self.ui.table_accesory.verticalHeader().setDefaultSectionSize(TABLE_FONT_SIZE + 4)
        self.ui.table_left.setFont(font)
        self.ui.table_parts.setFont(font)
        self.ui.table_accesory.setFont(font)
        self.ui.table_left.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_parts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_accesory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_left.setHorizontalHeaderLabels(('Виды работ', 'Цена', 'Примечание'))
        self.ui.table_parts.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                      'Цена', 'Шт', 'Дата', 'Где'))
        self.ui.table_accesory.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                         'Цена', 'Шт', 'Дата', 'Где'))

    def search_and_upd_model_buttons(self, search_req):
        if STRICT_SEARCH and len(search_req) < STRICT_SEARCH_LEN:
            return
        search_req = search_req.lower()
        self.models = self.Price.search_price_models(search_req, MODEL_LIST_SIZE)
        print(f'{self.models=}')
        lay = self.ui.scroll_models_layout.layout()
        self.clear_layout(lay)
        if self.models:
            self.upd_model_buttons(lay)

    def upd_model_buttons(self, lay):
        # lay = self.ui.scroll_models_layout.layout()
        # self.clear_layout(lay)
        sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addItem(sp)
        le = len(self.models)
        self.model_buttons = {}
        if MODEL_LIST_REVERSED:
            models_list = reversed((self.models.keys()))
            # models_list = reversed(list(self.models.keys()))
        else:
            models_list = (self.models.keys())
        for num, model in enumerate(models_list):
            self.model_buttons[num] = QPushButton(model)
            # b = QPushButton(model)
            self.model_buttons[num].clicked.connect(self.scheduler)
            if num == 0:
                self.model_buttons[num].setDefault(True)
                # b.setFocus()
                # b.setChecked(True)
            lay.addWidget(self.model_buttons[num], 0)
            le -= 1

    # @QtCore.pyqtSlot
    def scheduler(self):
        print('Start sheduler')
        model = self.sender().text()
        self.update_price_table(model)
        if self.ui.input_search.text() != self.old_search:
            self.old_search = self.ui.input_search.text()
            self.update_dk9_data(self.old_search)

    def update_dk9_data(self, search):
        part_table_soup, accessory_table_soup = self.DK9.search(search)
        self.fill_table_from_soup(part_table_soup, self.ui.table_parts, DK9_BG_P_COLOR1, DK9_BG_P_COLOR2)
        self.fill_table_from_soup(accessory_table_soup, self.ui.table_accesory, DK9_BG_A_COLOR1, DK9_BG_A_COLOR2)

    def update_price_table(self, model):  # 'xiaomi mi a2 m1804d2sg'
        position = self.models[model]  # [Sheet 27:<XIAOMI>, 813] - sheet, row
        # Take needed columns for exact model
        if position[0].name in PRICE_SEARCH_COLUMN_NUMBERS:
            columns = PRICE_SEARCH_COLUMN_NUMBERS[position[0].name]  # [2, 4, 5]
        else:
            columns = PRICE_SEARCH_COLUMN_NUMBERS['+']
        row = Price.get_row_by_model(model, position)

        new_row_num = 0
        self.ui.table_left.setRowCount(0)
        self.ui.model_lable.setText(self.list_to_string(row))
        for i in range(position[1], position[0].nrows - 1):
            # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
            if len(row) < (columns[2]):  # If row shorter, than we expect, then place all row in 0 column
                # print('SHORT row:' + str(row))
                self.ui.table_left.insertRow(new_row_num)
                self.ui.table_left.setItem(new_row_num, 0, QTableWidgetItem(self.list_to_string(row)))
                return
            else:
                # print(f'{i=} {columns[2]=} {c=} {self.PRICE_DB.xf_list[c.xf_index]=}')
                cells_text = [str(row[columns[0]]), str(row[columns[1]])]
                if cells_text[0] or len(cells_text[1]) > 3:
                    cells_text.append(str(row[columns[2]]))
                    self.ui.table_left.insertRow(new_row_num)
                    for j, txt in enumerate(cells_text):
                        self.ui.table_left.setItem(new_row_num, j, QTableWidgetItem(txt))
                        if PRICE_COLORED:
                            bgd = self.Price.DB.colour_map. \
                                get(self.Price.DB.xf_list[position[0].
                                    cell(i, columns[j]).xf_index].background.pattern_colour_index)
                            if bgd:
                                self.ui.table_left.item(new_row_num, j). \
                                    setBackground(QtGui.QColor(bgd[0], bgd[1], bgd[2]))
                    new_row_num += 1
                if i < position[0].nrows:
                    # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
                    row = position[0].row_values(i + 1, 0, 9)
                    if row[0] != '':
                        if row[0] not in PRICE_TRASH_IN_CELLS:
                            return
                    # print(row[col[0]-1, col[1]-1, col[2]-1])
                else:
                    return

    def prepare_columns(self):
        for k in PRICE_SEARCH_COLUMN_NUMBERS.keys():
            for i, c in enumerate(PRICE_SEARCH_COLUMN_NUMBERS[k]):
                PRICE_SEARCH_COLUMN_NUMBERS[k][i] = PRICE_SEARCH_COLUMN_NUMBERS[k][i] - 1
        # print(SEARCH_COLUMN_NUMBERS)

    def fill_table_from_soup(self, soup, table, def_bg_color1, def_bg_color2):
        r = 0
        table.setRowCount(0)
        if not soup:
            print(f'ERROR: Soup = {soup}')
            return
        for dk9_row in soup.tr.next_siblings:
            row_palette = None
            if repr(dk9_row)[0] != "'":
                # print(dk9_row)
                if dk9_row.attrs:
                    if 'style' in dk9_row.attrs:
                        style = str(dk9_row['style'])
                        row_palette = DK9_BG_COLORS[style[style.find(':') + 1: style.find(';')]]
                c = 0
                table.insertRow(r)
                for dk9_td in dk9_row.findAll('td'):
                    table.setItem(r, c, QTableWidgetItem(dk9_td.string))
                    if row_palette:
                        table.item(r, c). \
                            setBackground(QtGui.QColor(row_palette[0], row_palette[1], row_palette[2]))
                    elif dk9_td.attrs and 'style' in dk9_td.attrs:
                        style = str(dk9_td['style'])
                        td_palette = DK9_BG_COLORS[style[style.find(':') + 1: style.find(';')]]
                        table.item(r, c). \
                            setBackground(QtGui.QColor(td_palette[0], td_palette[1], td_palette[2]))
                    # if 'align' in dk9_td.attrs:
                    #     align = str(dk9_td['align'])
                    #     if align == 'center':
                    #         self.ui.table_parts.item(r, c).setTextAlignment(1)
                    else:
                        dbgc = def_bg_color1 if r % 2 else def_bg_color2
                        table.item(r, c).setBackground(QtGui.QColor(dbgc[0], dbgc[1], dbgc[2]))
                    c += 1
            r += 1

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
        if now is None:
            pass
            # print(f"\nwindow is the active window: {self.isActiveWindow()}")
            # self.setWindowState(QtCore.Qt.WindowMinimized)
        else:
            self.ui.input_search.setFocus()
            self.ui.input_search.selectAll()
            # print(f"window is the active window: {self.isActiveWindow()}")

    # def event(self, event):
    #     # print(f'Event type: {event.type()}')
    #     if event.type() == QEvent.KeyPress:# and event.key() == Qt.Key_Tab:
    #         print(f'TAB {self.ui.tab_widget.currentIndex()=} {event.key()=}')
    #     return QMainWindow.event(self, event)

    def keyPressEvent(self, event) -> None:
        # print(f'KEYPRESS: {event.key()}')
        if self.models:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.model_buttons[self.current_model_button_index].click()
            elif event.key() == Qt.Key_Up:
                self.model_buttons[self.current_model_button_index].setDefault(False)
                self.current_model_button_index -= 1
                if self.current_model_button_index < 0:
                    self.current_model_button_index = len(self.model_buttons) - 1
                self.model_buttons[self.current_model_button_index].setDefault(True)
                self.model_buttons[self.current_model_button_index].setFocus()
                # print('Wow, Up')
            elif event.key() == Qt.Key_Down:
                self.model_buttons[self.current_model_button_index].setDefault(False)
                self.current_model_button_index += 1
                if self.current_model_button_index > len(self.model_buttons) - 1:
                    self.current_model_button_index = 0
                self.model_buttons[self.current_model_button_index].setDefault(True)
                self.model_buttons[self.current_model_button_index].setFocus()
                # print('Wow, Down')
                # self.ui.input_search.setFocus()
                # self.ui.input_search.selectAll()
        if event.key() == Qt.Key_Alt:
            # print(f'TAB {self.ui.tab_widget.currentIndex()=}')
            if self.ui.tab_widget.currentIndex() == 0:
                self.ui.tab_widget.setCurrentIndex(1)
            else:
                self.ui.tab_widget.setCurrentIndex(0)

    def handle_config(self):
        config = configparser.ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/server'

    # @staticmethod
    # def close_cmd():
    #     WMI = GetObject('winmgmts:')
    #     processes = WMI.InstancesOf('Win32_Process')
    #
    #     for p in WMI.ExecQuery('select * from Win32_Process where Name="cmd.exe"'):
    #         print("Killing PID:", p.Properties_('ProcessId').Value)
    #         os.system("taskkill /pid " + str(p.Properties_('ProcessId').Value))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    window.ui.input_search.setFocus()
    sys.exit(app.exec_())
