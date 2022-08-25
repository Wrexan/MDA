import sys
import bs4
import traceback
import os

sys.path.append(os.path.join(os.getcwd(), 'PyQt5'))
sys.path.append(os.path.join(os.getcwd(), 'PyQt5\\Qt'))
sys.path.append(os.path.join(os.getcwd(), 'PyQt5\\QtWidgets'))
# print(f'{sys.path=}')

os.add_dll_directory(f'{os.getcwd()}\\PyQt5')
os.add_dll_directory(f'{os.getcwd()}\\PyQt5\\Qt')
os.add_dll_directory(f'{os.getcwd()}\\PyQt5\\QtWidgets')
# print(f'{os.path=}')

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMenu, \
    QHeaderView, qApp, QMessageBox, QListWidget, QSizePolicy, QLineEdit, QSpacerItem, QPushButton, QLabel, QStyleFactory
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt, QEvent

from MDA_classes.config import Config
from MDA_classes.dk9 import DK9Parser
from MDA_classes.price import Price
from MDA_classes.modal_windows import ConfigWindow, HelpWindow, AdvancedSearchWindow
from MDA_classes.thread_worker import Worker
from MDA_UI.window_main import Ui_MainWindow

C = Config()
DK9 = DK9Parser(C)


class App(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        qApp.focusChanged.connect(self.on_focusChanged)
        self.tab_font = QtGui.QFont()

        self.tab_font_bold = QtGui.QFont()
        # self.tab_font_bold.setWeight(196)
        self.tab_font_bold.setBold(True)

        self.tab_font_under = QtGui.QFont()
        self.tab_font_under.setUnderline(True)

        self.tab_font_bold_under = QtGui.QFont()
        self.tab_font_bold_under.setBold(True)
        self.tab_font_bold_under.setUnderline(True)

        self.ui_font = QtGui.QFont()
        self.ui_font_bold = QtGui.QFont()
        self.ui_font_bold.setBold(True)

        self.models = {}
        self.model_buttons = {}
        self.manufacturer_wheel = None
        self.current_model_button_index = 0
        self.ui = Ui_MainWindow()
        # self.ui = MainUI()
        self.ui.setupUi(self)
        self.model_list_widget = QListWidget()
        self.dk9_request_label = QLabel()

        self.search_input = SearchInput(self)
        self.search_input.setParent(self.ui.frame_3)
        self.ui.search_layout.addWidget(self.search_input)

        self.freeze_ui_update = True

        self.copied_table_items = {}

        self.init_ui_statics()
        self.apply_window_size()
        self.init_ui_dynamics()

        self.curr_manufacturer_idx: int = 0
        self.curr_manufacturer: str = ''
        # self.curr_manufacturers: tuple = ()
        self.curr_type: str = ''
        self.curr_model: str = ''  # --------------------------------------
        self.curr_model_idx: int = 0
        self.curr_description: str = ''
        self.recursor = ' -> '

        self.search_req_ruled: str = ''
        self.search_again = False
        # self.old_search = ''
        self.thread = QtCore.QThread
        self.worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        self.Price = Price(C)
        self.soup = None
        self.web_status = 0
        self.price_status = 0

        # self.themes = ('windowsvista', 'Fusion', 'Windows')
        self.themes = (*QStyleFactory.keys(),)
        self.current_theme = 0
        # self.login_dk9()
        self.update_web_status(0)
        # self.update_price_status()
        self.show()

    def init_ui_statics(self):

        self.resized.connect(self.init_ui_dynamics)
        self.search_input.textChanged[str].connect(self.prepare_and_search)

        self.ui.pb_adv_search.setToolTip(
            'Необходимо для поиска в веб базе в конкретных полях')

        self.ui.chb_show_exact.stateChanged.connect(self.upd_dk9_on_rule_change)
        self.ui.chb_show_exact.setToolTip(
            'Вкл - отображает максимально релевантные модели\n'
            'Откл - отображается все, что выдает база (Mi8 lite по запросу Mi8)')

        self.ui.chb_show_date.stateChanged.connect(self.switch_n_upd_dk9_tables_grid)
        self.ui.chb_show_date.setToolTip(
            'Вкл - отображает дату поступления товара\n'
            'Откл - дата поступления товара урезана (появляется при наведении курсора)')

        self.ui.chb_price_name_only.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_price_name_only.setToolTip(
            'Вкл - запросом в интернет базу являются производитель и модель из прайса\n'
            'Откл - запросом в интернет базу является текст в строке ввода '
            '(позволяет по запросу 5 найти все модели всех фирм, содержащие 5)')

        self.ui.chb_search_eng.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_eng.setToolTip(
            'Вкл - переводит символы алфавита в латиницу нижнего регистра')

        self.ui.chb_search_narrow.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_narrow.setToolTip(
            'Вкл - поиск начинается с 2х символов\n'
            'Откл - позволяет найти отдельный символ (например украинскую С или Е)')

        self.ui.pb_adv_search.clicked.connect(self.open_adv_search)
        self.ui.settings_button.clicked.connect(self.open_settings)

        self.ui.table_price.setHorizontalHeaderLabels(('Виды работ', 'Цена', 'Прим'))
        self.ui.table_parts.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                       'Цена', 'Шт', 'Дата', 'Где'))
        self.ui.table_accesory.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                          'Цена', 'Шт', 'Дата', 'Где'))

        self.ui.table_parts.doubleClicked.connect(self.copy_web_table_items_connected)
        self.ui.table_accesory.doubleClicked.connect(self.copy_web_table_items_connected)
        self.ui.table_parts.installEventFilter(self)
        self.ui.table_accesory.installEventFilter(self)
        self.ui.table_price.clicked.connect(self.cash_table_element)
        self.ui.table_price.doubleClicked.connect(self.copy_price_table_item_connected)
        self.ui.table_price.installEventFilter(self)
        self.ui.help.clicked.connect(self.open_help)

        self.dk9_request_label.setParent(self.ui.tab_widget)
        self.dk9_request_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.dk9_request_label.setFixedWidth(80)
        self.dk9_request_label.setAlignment(Qt.AlignRight)

        self.manufacturer_wheel = (self.ui.manufacturer_1,
                                   self.ui.manufacturer_2,
                                   self.ui.manufacturer_3,
                                   self.ui.manufacturer_4,
                                   self.ui.manufacturer_5,
                                   self.ui.manufacturer_6,
                                   self.ui.manufacturer_7)
        for manuf_label in self.manufacturer_wheel:
            manuf_label.clicked.connect(self.upd_manufacturer_wheel_connect)
        # models list appearing on search
        self.model_list_widget.setParent(self)
        self.model_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.model_list_widget.setFixedWidth(self.search_input.width())
        self.model_list_widget.setMinimumSize(20, 20)
        self.model_list_widget.itemClicked.connect(self.scheduler)
        self.model_list_widget.hide()

        self.model_list_widget.setStyleSheet(
            "QListView::item"
            "{"
            # "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 lightgreen, stop: 1 #DCF1DE);"
            "border: 1px solid #ffffff;"
            # "background-color : lightgreen;"
            "}"
            "QListView::item:hover"
            "{"
            "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 lightgreen, stop: 1 #DCF1DE);"
            # "border: 1px solid #6a6ea9;"
            # "background-color : lightgreen;"
            "}"
            "QListView::item:selected"
            "{"
            "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #b5BfF3, stop: 1 #E5E8F9);"
            "border: 1px solid #6a6ea9;"
            # "background-color : lightgreen;"
            "}")

        self.ui.table_price.setStyleSheet(
            # "QTableWidget::item"
            # "{"
            # # "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 lightgreen, stop: 1 #DCF1DE);"
            # "border: 1px solid #ffffff;"
            # # "background-color : lightgreen;"
            # "}"
            "QTableWidget::item:hover"
            "{"
            # "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #DCF1DE, stop: 1 #DCF1DE);"
            # "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 lightgreen, stop: 1 #DCF1DE);"
            # "border-top: 1px solid #6a6ea9;"
            # "border-bottom: 1px solid #6cde6e;"
            "background-color : #cCFEcE;"
            "}"
            "QTableWidget::item:selected"
            "{"
            # "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #b5BfF3, stop: 1 #E5E8F9);"
            "border-top: 1px solid #6a6ea9;"
            "border-bottom: 1px solid #6a6ea9;"
            "background-color : #b5BfF3;"
            "}")

        self.ui.pt_cash_name.setStyleSheet(
            "QPlainTextEdit"
            "{selection-background-color: #b5BfF3;"
            # "selection-color:white;"
            "}")

        self.ui.pt_cash_price.setStyleSheet(
            "QPlainTextEdit"
            "{selection-background-color: #b5BfF3;}")

        self.ui.pt_cash_descr.setStyleSheet(
            "QPlainTextEdit"
            "{selection-background-color: #b5BfF3;}")

    def apply_window_size(self):
        if C.FULLSCREEN:
            self.showMaximized()
        else:
            self.showNormal()

    def init_ui_dynamics(self):
        self.tab_font.setPixelSize(C.TABLE_FONT_SIZE)
        self.tab_font_bold.setPixelSize(C.TABLE_FONT_SIZE)
        self.tab_font_under.setPixelSize(C.TABLE_FONT_SIZE)
        self.tab_font_bold_under.setPixelSize(C.TABLE_FONT_SIZE)
        self.ui_font.setPixelSize(C.SMALL_FONT_SIZE)
        self.ui_font_bold.setPixelSize(C.SMALL_FONT_SIZE)
        self.ui.table_price.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_parts.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_accesory.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_price.setFont(self.tab_font)
        self.ui.table_parts.setFont(self.tab_font)
        self.ui.table_accesory.setFont(self.tab_font)
        self.ui.pt_cash_name.setFont(self.tab_font)
        self.ui.pt_cash_descr.setFont(self.tab_font)
        self.ui.pt_cash_price.setFont(self.tab_font)
        self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                 num=0, tab_names=C.DK9_TABLE_NAMES, count_1=0, count_2=0)
        self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                 num=1, tab_names=C.DK9_TABLE_NAMES, count_1=0, count_2=0)

        self.model_list_widget.setFont(self.tab_font)
        self.fix_models_list_position()

        self.upd_dk9_tables_grid()

        table_width = self.ui.table_price.width()
        table_width_n_percent = int(table_width / 3.5 + (table_width - 640) / 4)
        self.ui.table_price.horizontalHeader().setDefaultSectionSize(table_width_n_percent)
        self.ui.table_price.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.table_price.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.freeze_ui_update = True
        self.ui.chb_show_exact.setCheckState(2 if C.FILTER_SEARCH_RESULT else 0)
        self.ui.chb_price_name_only.setCheckState(2 if C.SEARCH_BY_PRICE_MODEL else 0)
        self.ui.chb_search_eng.setCheckState(2 if C.LATIN_SEARCH else 0)
        self.ui.chb_search_narrow.setCheckState(2 if C.NARROW_SEARCH else 0)
        self.freeze_ui_update = False

        self.dk9_request_label.move(self.ui.table_parts.width() - 84, 3)
        self.dk9_request_label.setFont(self.ui_font_bold)
        # self.dk9_request_label.setText("Redmi AAAA")

    # =============================================================================================================

    def fix_models_list_position(self):
        self.model_list_widget.move(int(self.ui.search_widget.x() + 12),
                                    int(self.ui.HEAD.height() - 6))

    def start_search_on_rule_change(self):
        if self.freeze_ui_update:
            return
        C.SEARCH_BY_PRICE_MODEL = True if self.ui.chb_price_name_only.checkState() == 2 else False
        C.LATIN_SEARCH = True if self.ui.chb_search_eng.checkState() == 2 else False
        C.NARROW_SEARCH = True if self.ui.chb_search_narrow.checkState() == 2 else False
        self.prepare_and_search(self.search_input.text(), True)

    def upd_dk9_on_rule_change(self):
        if self.freeze_ui_update:
            return
        C.FILTER_SEARCH_RESULT = True if self.ui.chb_show_exact.checkState() == 2 else False
        if self.soup:
            self.update_dk9_data(use_old_soup=True)

    def switch_n_upd_dk9_tables_grid(self):
        C.SHOW_DATE = True if self.ui.chb_show_date.checkState() == 2 else False
        self.upd_dk9_tables_grid()

    def upd_dk9_tables_grid(self):
        if C.SHOW_DATE:
            self.ui.table_parts.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
            self.ui.table_accesory.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        else:
            self.ui.table_parts.horizontalHeader().setDefaultSectionSize(int(C.TABLE_FONT_SIZE * 1.2 + 6))
            self.ui.table_accesory.horizontalHeader().setDefaultSectionSize(int(C.TABLE_FONT_SIZE * 1.2 + 6))
            for i in range(self.ui.table_parts.columnCount()):
                if i == 3:
                    self.ui.table_parts.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
                    self.ui.table_accesory.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
                elif i != 6 or C.SHOW_DATE:
                    self.ui.table_parts.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
                    self.ui.table_accesory.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
                else:
                    self.ui.table_parts.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
                    self.ui.table_accesory.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)

    def on_ui_loaded(self):
        print('Loading Price')
        self.read_price()
        print('Login to DK9')
        # self.login_dk9()

    def prepare_and_search(self, search_req: str, force_search: bool = False):
        # print(f'{search_req=} {self.search_input.isModified()=}')
        if search_req == '':
            self.models = {}
            self.curr_model = ''
            self.upd_manufacturer_wheel(clear=True)
            return

        if self.search_input.isModified() or force_search:  # Only if user type something or by event
            result_req = self.apply_rule_latin(search_req)
            result_req = self.apply_rule_narrow(result_req)
        else:
            result_req = search_req

        # print(f'{result_req=} {self.price_status=} {len(C.PRICE_STATUSES)=}')

        self.search_req_ruled = result_req
        if result_req:
            if force_search:
                self.search_input.selectAll()
            # print(f'{search_req=} {result_req=}')
            if self.price_status >= len(C.PRICE_STATUSES):
                self.models = self.Price.search_price_models(result_req, C.MODEL_LIST_MAX_SIZE)
            if self.models:
                # print(f'prepare_and_search: {self.models.items()=}')
                self.upd_manufacturer_wheel(hide_list=force_search)
            else:
                self.upd_manufacturer_wheel(clear=True)
        else:
            self.upd_manufacturer_wheel(clear=True)

    def apply_rule_latin(self, search_req: str):
        # LATIN RULE: Turn all input text into ascii
        if not search_req:
            return
        result_req: list = []
        if C.LATIN_SEARCH:
            # print(f'Applying LATIN to: {search_req}')
            lower_req = search_req.lower()
            for symbol in lower_req:
                if symbol in C.SYMBOL_TO_LATIN:
                    result_req.append(C.SYMBOL_TO_LATIN[symbol])
                else:
                    result_req.append(symbol)
            result_str = ''.join(result_req)
            self.search_input.setText(result_str)
        else:
            result_str = search_req
        return result_str

    @staticmethod
    def apply_rule_narrow(in_req: str):
        # NARROW RULE: search only if search request longer then C.NARROW_SEARCH_LEN
        if C.NARROW_SEARCH and len(in_req) < C.NARROW_SEARCH_LEN:
            return
        return in_req

    def upd_manufacturer_wheel_connect(self):
        self.upd_manufacturer_wheel(increment=int(self.sender().objectName()[-1])-4)

    def upd_manufacturer_wheel(self, increment: int = 0, clear: bool = False, hide_list: bool = False):
        # print(f'upd_manufacturer_wheel({increment=}, {clear=}, {hide_list=}, ')
        for label in self.manufacturer_wheel:
            label.setText('')
        if clear:
            self.curr_manufacturer = ''
            self.curr_manufacturer_idx = 0
            self.upd_models_list(clear=True)
            return

        _len = len(self.models) - 1
        self.curr_manufacturer_idx += increment
        if self.curr_manufacturer_idx > _len:
            self.curr_manufacturer_idx = _len
        if self.curr_manufacturer_idx < 0:
            self.curr_manufacturer_idx = 0

        # print(f'{self.curr_manufacturer_idx=}')
        for m, manufacturer in enumerate(self.models):
            manufs_aside = int((len(self.manufacturer_wheel) - 1) / 2)
            if self.curr_manufacturer_idx + manufs_aside >= m >= self.curr_manufacturer_idx - manufs_aside:
                self.manufacturer_wheel[m - self.curr_manufacturer_idx + manufs_aside].setText(manufacturer)
                if m == self.curr_manufacturer_idx:
                    self.curr_manufacturer = manufacturer
                    self.upd_models_list(hide_list=hide_list)

    def upd_models_list(self, clear: bool = False, hide_list: bool = False):
        if clear or not self.models or not self.curr_manufacturer:
            # self.curr_manufacturer_idx = 0
            self.model_list_widget.clear()
            self.model_list_widget.hide()
            return
        # print(f'Upd_models_list: {self.models[self.curr_manufacturer].items()=}')
        curr_models = [
            f'{model}{self.recursor}{params[2]}' if params[2] else model
            for model, params in self.models[self.curr_manufacturer].items()]
        # print(f'{curr_models=} {hide_list=} {self.models[self.curr_manufacturer].items()=}')
        size = C.MODEL_LIST_MAX_SIZE if len(curr_models) > C.MODEL_LIST_MAX_SIZE else len(curr_models)
        self.model_list_widget.show()
        models_list = curr_models

        if hide_list:
            self.model_list_widget.clear()
            self.model_list_widget.hide()
        else:
            self.model_list_widget.clear()
            self.model_list_widget.addItems(models_list)
            self.model_list_widget.setCurrentRow(0)
            self.model_list_widget.setFixedHeight(self.model_list_widget.sizeHintForRow(0) * (size + 1))

    def upd_model_buttons(self, model_names):
        lay = self.ui.lay_model_buttons
        self.clear_layout(lay)

        le = len(self.models)
        self.model_buttons = {}
        self.current_model_button_index = 0
        for num, model in enumerate(model_names):
            self.model_buttons[num] = QPushButton(model)
            self.model_buttons[num].clicked.connect(self.search_dk9_by_button)
            if num == 0:
                self.model_buttons[num].setDefault(True)
                # self.curr_model = model
                if self.web_status == 2:
                    if DK9.LOGIN_SUCCESS:
                        self.search_dk9()
                else:
                    self.login_dk9()
            lay.addWidget(self.model_buttons[num], 0)
            le -= 1
        sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addItem(sp)

    def update_price_status(self, status: int):
        self.price_status = status
        if status in C.PRICE_STATUSES.keys():
            self.ui.price_status.setText(C.PRICE_STATUSES[status])
        else:
            self.ui.price_status.setText(self.Price.NAME)
        # print(f'{self.price_status=}')

    # @QtCore.pyqtSlot
    def scheduler(self, item):
        text_lower: str = item.text().lower()
        text_lower_orig = text_lower[:]
        # print(f'Scheduler: {text_lower=}')
        for i in range(len(text_lower) - 2):
            remark_start = text_lower.find('(')
            if remark_start >= 0:
                remark_end = text_lower[remark_start:].find(')')
                # print(f'{text_lower[:remark_start]=}  {text_lower[ + remark_end:]=}')
                # print(f'{remark_start=}  {remark_end=}')
                text_lower = f'{text_lower[:remark_start]}' \
                             f'{text_lower[remark_start + remark_end + 1:]}'
            else:
                break
        # print(f'CUT: {text_lower=}')
        manufacturer_lower = self.curr_manufacturer.lower()
        if 'asus' in manufacturer_lower:  # -------------------ASUS
            manufacturer_lower = 'asus'  # -------------------ASUS

        models_str = text_lower. \
            replace(manufacturer_lower, ''). \
            replace('телефон', ''). \
            replace('планшет', ''). \
            replace('с', 'c'). \
            replace('е', 'e')
        recursor_idx = models_str.find(self.recursor)
        recursive_model = ''

        if recursor_idx >= 0:
            recursive_model = models_str[recursor_idx + len(self.recursor):].strip()
            models_str = models_str[:recursor_idx]
        models_for_buttons = [m.strip() for m in models_str.split(',', 4)]
        # print(f'Recursive: {models_str=} {recursor_idx=} {recursive_model=} {models_for_buttons=}')
        if recursive_model:
            for m in self.models[self.curr_manufacturer]:
                if m != text_lower and recursive_model in m:
                    text_lower = m.lower()

            models_for_buttons.append(models_for_buttons[0])
            models_for_buttons[0] = recursive_model
        # print(f'{models_for_buttons=}  {text_lower=}')
        # print(f'{C.SEARCH_BY_PRICE_MODEL=} {recursive_model=} {self.search_req_ruled=} ')
        if C.SEARCH_BY_PRICE_MODEL:
            self.curr_model = models_for_buttons[0]
        else:
            self.curr_model = self.search_req_ruled
        self.upd_models_list(clear=True)
        self.upd_model_buttons(models_for_buttons)
        self.update_price_table(text_lower_orig, recursive_model)

    def update_web_status(self, status: int):
        if status in C.WEB_STATUSES:
            self.web_status = status
            self.ui.web_status.setText(C.WEB_STATUSES[status])
            # if status != 2:
            #     self.curr_model = ''
        else:
            print(f'Error: status code {status} not present {C.WEB_STATUSES=}')

    def read_price(self):
        self.worker = Worker(self.Price.load_price)
        # self.worker.signals.result.connect(self.update_dk9_data)
        # self.worker.signals.progress.connect(self.load_progress)
        self.worker.signals.finished.connect(self.login_dk9)
        self.worker.signals.error.connect(self.error)
        self.worker.signals.status.connect(self.update_price_status)
        print('Starting thread to read price')
        self.thread.start(self.worker, priority=QtCore.QThread.Priority.HighestPriority)

    def search_dk9_by_button(self):
        self.curr_model = self.sender().text()
        # print(f'SEARCH BY BUTTON: {self.curr_model}')
        self.search_dk9()

    def search_dk9(self, advanced: dict = None):
        if advanced:
            self.worker = Worker(DK9.adv_search,
                                 advanced['_type'],
                                 advanced['_manufacturer'],
                                 advanced['_model'],
                                 advanced['_description'])
        else:
            if not DK9.LOGIN_SUCCESS or self.web_status != 2:
                return
            if not C.SEARCH_BY_PRICE_MODEL or 'asus' in self.curr_manufacturer.lower():  # -------------------ASUS
                manufacturer = ''
            else:
                manufacturer = self.curr_manufacturer

            if self.search_again:
                print(f'SEARCH AGAIN: {self.curr_model}')
                self.search_again = False
            self.dk9_request_label.setText(self.curr_model)
            self.worker = Worker(DK9.adv_search,
                                 self.curr_type,
                                 manufacturer,
                                 self.curr_model,
                                 self.curr_description)
        self.worker.signals.result.connect(self.update_dk9_data)
        self.worker.signals.progress.connect(self.load_progress)
        self.worker.signals.finished.connect(self.finished)
        self.worker.signals.error.connect(self.error)
        self.worker.signals.status.connect(self.update_web_status)

        self.thread.start(self.worker)

    def login_dk9(self):
        self.worker = Worker(DK9.login)
        self.worker.signals.progress.connect(self.load_progress)
        self.worker.signals.status.connect(self.update_web_status)
        self.worker.signals.error.connect(self.error)
        if self.curr_model:
            self.search_again = True
            self.worker.signals.finished.connect(self.search_dk9)
        else:
            self.worker.signals.finished.connect(self.finished)
        print('Starting thread to login')

        self.thread.start(self.worker)

    def update_dk9_data(self, table_soups: type(bs4.BeautifulSoup) = None, use_old_soup: bool = False):
        if not use_old_soup:
            self.soup = table_soups
            if not self.soup:
                self.update_web_status(0)
            elif not self.soup[0]:
                self.update_web_status(2)

        if self.web_status == 2:
            self.load_progress(70)
            self.fill_table_from_soup(self.soup, self.ui.table_parts, 0,
                                      C.DK9_TABLE_NAMES, C.DK9_BG_P_COLOR1, C.DK9_BG_P_COLOR2, 5,
                                      align={4: Qt.AlignRight})
            self.load_progress(85)
            self.fill_table_from_soup(self.soup, self.ui.table_accesory, 1,
                                      C.DK9_TABLE_NAMES, C.DK9_BG_A_COLOR1, C.DK9_BG_A_COLOR2, 5,
                                      align={4: Qt.AlignRight})
        else:
            self.login_dk9()
        self.load_progress(0) if use_old_soup else self.load_progress(100)

    def dummy(self):
        pass

    def clear_table(self, table):
        self.copied_table_items = {}
        table.clearContents()
        table.setRowCount(0)

    def update_price_table(self, model, recursive_model: str = ''):  # 'xiaomi mi a2 m1804d2sg'
        try:
            # print(f'{model=}\n{self.models=}\n{self.curr_model_idx=}\n'
            #       f'{self.curr_manufacturer=}\n{self.curr_manufacturer_idx=}')
            self.clear_table(self.ui.table_price)

            _models_of_manufacturer: dict = {}
            _model: str = ''

            if recursive_model:
                recursive_model = recursive_model.replace('   ', ' ').replace('  ', ' ')
                if self.price_status >= len(C.PRICE_STATUSES):
                    _rec_model_dict = self.Price.search_price_models(recursive_model, 5, True)
                    # print(f'{model=}  {_rec_model_dict=}')

                    if _rec_model_dict:
                        if self.curr_manufacturer in _rec_model_dict:
                            _models_of_manufacturer_all_compatible \
                                = dict(_rec_model_dict[self.curr_manufacturer].items())
                        else:
                            _models_of_manufacturer_all_compatible \
                                = dict(_rec_model_dict.items())

                        # print(f'{_models_of_manufacturer_all_compatible=}')
                        if len(_models_of_manufacturer_all_compatible) > 1:
                            recursive_model_len = len(recursive_model)
                            closest_delta_len = 10
                            for _m in _models_of_manufacturer_all_compatible.items():

                                _main_model = _m[0].split(',')[0].strip().replace('   ', ' ').replace('  ', ' ')
                                # print(f'{_main_model=}')
                                if recursive_model not in _main_model:
                                    continue

                                _manufacturer_lower = self.curr_manufacturer.lower()
                                if _manufacturer_lower in _main_model:
                                    if 'asus' in _manufacturer_lower:  # -------------------ASUS
                                        _manufacturer_lower = 'asus'  # -------------------ASUS
                                    _m_manuf_cut = _main_model.replace(_manufacturer_lower, '').strip()
                                    this_delta_len = abs(recursive_model_len - len(_m_manuf_cut))
                                    # print(f'CUTTING {_manufacturer_lower=} => {_m_manuf_cut=}  {this_delta_len=}')
                                else:
                                    this_delta_len = abs(recursive_model_len - len(_main_model))
                                if this_delta_len < closest_delta_len:
                                    closest_delta_len = this_delta_len
                                    _models_of_manufacturer[_m[0]] = _m[1]
                                    _model = _m[0]
                                    # print(f'FOUND {this_delta_len=}  {_model=}  {_models_of_manufacturer=}')

                            if not _models_of_manufacturer:
                                _models_of_manufacturer = list(_rec_model_dict.values())[0]
                                _model = next(iter(_models_of_manufacturer.keys()))
                        else:
                            _models_of_manufacturer = list(_rec_model_dict.values())[0]
                            _model = next(iter(_models_of_manufacturer.keys()))
                    else:
                        self.ui.table_price.insertRow(0)
                        self.ui.table_price.setItem(0, 0, QTableWidgetItem(
                            f'Модель {recursive_model} не найдена в прайсе'))
                        self.ui.table_price.item(0, 0).setFont(self.tab_font_bold)
                        return
            else:
                _models_of_manufacturer = self.models[self.curr_manufacturer]
                _model = model

            # print(f'{_models_of_manufacturer=}')
            # print(f'{_model=}')

            if _model in _models_of_manufacturer:
                # print(f'FOUND')
                position = _models_of_manufacturer[_model]  # [Sheet 27:<XIAOMI>, 813] - sheet, row
                # print(f'{position=}')

                # Take needed columns for exact model
                if self.curr_manufacturer in C.PRICE_SEARCH_COLUMN_NUMBERS:
                    columns = C.PRICE_SEARCH_COLUMN_NUMBERS[self.curr_manufacturer]  # [2, 6, 7]
                else:
                    columns = C.PRICE_SEARCH_COLUMN_NUMBERS['+']
                # print(f'{columns=}')

                row = Price.get_row_in_pos(position)
                row_len = len(row)
                cells_texts = [row[0],
                               row[columns[1]] if columns[1] < row_len else '',
                               row[columns[2]] if columns[2] < row_len else '']
                new_row_num = 0
                # print(f'{row=}')

                if True:  # if model row must be shown in price table
                    # print(f'{row=} {columns=} {cells_texts=} ')
                    self._add_price_table_row(table=self.ui.table_price, sheet=position[0],
                                              columns=columns, cells_texts=cells_texts,
                                              t_row_num=new_row_num, p_row_num=position[1],
                                              align={1: Qt.AlignRight}, colored=C.PRICE_COLORED, bold=True)
                    new_row_num += 1

                for i in range(position[1], position[0].nrows - 1):
                    # print(f'{row=} {row_len=} {i=} {columns[-1]=} {columns=} ')
                    if row_len < columns[-1] + 1:  # If row shorter, than we expect, then place all row in 0 column
                        # print('SHORT row:' + str(row))
                        cell_text = self.list_to_string(row)
                        self.ui.table_price.insertRow(new_row_num)
                        self.ui.table_price.setItem(new_row_num, 0, QTableWidgetItem(cell_text))
                        self.ui.table_price.item(new_row_num, 0).setToolTip(cell_text)
                        return
                    else:
                        # if cell is out of row, text will be empty
                        cells_texts = []
                        for c in range(len(columns)):
                            if columns[c] < row_len:
                                cells_texts.append(row[columns[c]])
                            else:
                                cells_texts.append('')
                        # print(f"{cells_texts=}")
                        if cells_texts[0]:  # or len(cells_texts[1]) > 3:
                            self._add_price_table_row(table=self.ui.table_price, sheet=position[0],
                                                      columns=columns, cells_texts=cells_texts,
                                                      t_row_num=new_row_num, p_row_num=i,
                                                      align={1: Qt.AlignRight}, colored=C.PRICE_COLORED)

                            new_row_num += 1
                        if i < position[0].nrows:
                            # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
                            row = position[0].row_values(i + 1, 0, 7)
                            if row[0] != '':
                                if row[0] not in C.PRICE_TRASH_IN_CELLS:
                                    return
                            # print(row[col[0]-1, col[1]-1, col[2]-1])
                        else:
                            return
        except Exception as _err:
            self.error((f'Error updating price table for:\n'
                        f'{model}',
                        f'{traceback.format_exc()}'))

    def _add_price_table_row(self, table, sheet, columns, cells_texts: list, t_row_num: int, p_row_num: int,
                             align: dict = None, colored: bool = False, bold: bool = False):
        table.insertRow(t_row_num)
        # bold_font = None
        # if bold:
        #     bold_font = QtGui.QFont()
        #     bold_font.setBold(True)
        for c, txt in enumerate(cells_texts):
            if not isinstance(txt, str):
                if isinstance(txt, float):
                    txt = str(int(txt))
                else:
                    txt = str(txt)
            table.setItem(t_row_num, c, QTableWidgetItem(txt))
            table.item(t_row_num, c).setToolTip(txt)
            if align and c in align:
                table.item(t_row_num, c).setTextAlignment(align[c])
            if colored and columns[c] < sheet.row_len(p_row_num):  # c < len(columns):
                # print(f' colour: {p_row_num=}  {columns=}  {txt=}\n'
                #       f'{sheet.cell(p_row_num, columns[c]).xf_index=}\n'
                #       f'{len(self.Price.DB.xf_list)=}\n')
                bgd = self.Price.DB.colour_map. \
                    get(self.Price.DB.xf_list[sheet.cell(p_row_num, columns[c]).xf_index].
                        background.pattern_colour_index)
                if not bgd:
                    bgd = C.P_BG_COLOR1 if t_row_num % 2 else C.P_BG_COLOR2
                table.item(t_row_num, c).setBackground(QtGui.QColor(bgd[0], bgd[1], bgd[2]))
                # print(f' colour: {p_row_num=}  {columns[j]=}  {txt=}  {bgd=}')
            if bold:
                table.item(t_row_num, c).setFont(self.tab_font_bold if bold else self.tab_font)

    def load_progress(self, progress):
        self.ui.web_load_progress_bar.setValue(progress)

    def finished(self):
        if self.web_status not in (1, 2):
            self.ui.web_load_progress_bar.setValue(100)
        else:
            self.ui.web_load_progress_bar.setValue(0)

    def fill_table_from_soup(self, soup, table, num: int, tab_names: tuple,
                             def_bg_color1: tuple, def_bg_color2: tuple,
                             count_column: int = None, align: dict = None):
        try:
            item_counter = 0
            r = 0
            self.clear_table(table)
            if not soup[num]:
                if count_column is not None:
                    self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                             num=num, tab_names=tab_names, count_1=0, count_2=0)
                return
            for dk9_row in soup[num].tr.next_siblings:
                row_palette = None
                if repr(dk9_row)[0] != "'":
                    # print(dk9_row)
                    if C.DK9_COLORED and dk9_row.attrs:
                        if 'style' in dk9_row.attrs:
                            style = str(dk9_row['style'])
                            row_palette = C.DK9_BG_COLORS[style[style.find(':') + 1: style.find(';')]]
                    c = 0
                    row = dk9_row.findAll('td')
                    if C.FILTER_SEARCH_RESULT:
                        # print(f'{self.curr_model=}{row[2].string.lower()=}{row[3].string.lower()=}')
                        # Filter models different more than 1 symbol
                        curr_model_len = len(self.curr_model)
                        model_cell = row[2].string.lower()
                        model_cell_len = len(model_cell)
                        description_cell = row[3].string.lower()
                        description_cell_len = len(description_cell)
                        model_idx_in_desc = description_cell.find(self.curr_model)
                        # print(f'{description_cell=} {description_cell[model_idx_in_desc + curr_model_len]=} ')
                        if self.curr_model not in model_cell \
                                or (4 > model_cell_len > curr_model_len) \
                                or curr_model_len + 1 < model_cell_len:
                            if self.curr_model not in description_cell \
                                    or (model_idx_in_desc > 0
                                        and description_cell[model_idx_in_desc - 1].isalpha()) \
                                    or (model_idx_in_desc + curr_model_len < description_cell_len - 1
                                        and (description_cell[model_idx_in_desc + curr_model_len] not in '/,.')):
                                continue
                    amt = row[count_column].string
                    if count_column is not None and amt.isdigit():
                        item_counter += int(amt)

                    table.insertRow(r)
                    for dk9_td in row:
                        # print(f'{dk9_td.string} {self.curr_model=}')
                        table.setItem(r, c, QTableWidgetItem(dk9_td.string))
                        table.item(r, c).setToolTip(dk9_td.string)
                        if align and c in align:
                            table.item(r, c).setTextAlignment(align[c])
                        if 'ориг' in table.item(r, c).text():
                            table.item(r, c).setFont(self.tab_font_bold)
                        if C.DK9_COLORED:
                            if row_palette:
                                table.item(r, c). \
                                    setBackground(QtGui.QColor(row_palette[0], row_palette[1], row_palette[2]))
                            elif dk9_td.attrs and 'style' in dk9_td.attrs:
                                style = str(dk9_td['style'])
                                td_palette = C.DK9_BG_COLORS[style[style.find(':') + 1: style.find(';')]]
                                table.item(r, c). \
                                    setBackground(QtGui.QColor(td_palette[0], td_palette[1], td_palette[2]))
                            else:
                                dbgc = def_bg_color1 if r % 2 else def_bg_color2
                                table.item(r, c).setBackground(QtGui.QColor(dbgc[0], dbgc[1], dbgc[2]))
                        c += 1
                r += 1
            if count_column is not None:
                self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                         num=num, tab_names=tab_names, count_1=r - 1, count_2=item_counter)
        except Exception as _err:
            self.error((f'Error updating table:\n'
                        f'{table}',
                        f'{traceback.format_exc()}'))

    @staticmethod
    def _update_dk9_tooltip(tab_widget, num: int, tab_names: tuple, count_1: int, count_2: int):
        # tab_widget.setTabText(num, f'{tab_names[num]}{count_1} / {count_2} ')
        tab_widget.setTabText(num, f'{tab_names[num]} {count_2} шт')
        tab_widget.setTabToolTip(num, f'{count_1} позиций/ {count_2} штук')

    def copy_web_table_items_connected(self):
        self.copy_table_items(table=self.sender(), items=4)

    def copy_price_table_item_connected(self):
        self.copy_table_items(table=self.sender(), items=1)

    def copy_table_items(self, table: QtCore.QObject, items: int = 0):
        row = table.selectedItems()
        print(f'{row=}')
        self.clear_table_items_on_new_copy()
        self.copied_table_items[table] = []
        texts = []
        for i in range(items if items else len(row)):
            texts.append(row[i].text())
            self.copied_table_items[table].append(row[i])
            if table is not self.ui.table_price and 'ориг' in row[i].text():
                row[i].setFont(self.tab_font_bold_under)
            else:
                row[i].setFont(self.tab_font_under)

        clipboard.setText(' '.join(texts))
        # print(f'Copied: {" ".join(texts)}')

    def clear_table_items_on_new_copy(self):
        if not self.copied_table_items:
            return
        for table in self.copied_table_items.keys():
            if not self.copied_table_items[table]:
                return
            for item in self.copied_table_items[table]:
                if table != self.ui.table_price and 'ориг' in item.text():
                    item.setFont(self.tab_font_bold)
                else:
                    item.setFont(self.tab_font)
            del table

    def cash_table_element(self):
        selected_row = self.sender().selectedItems()
        selected_row_len = len(selected_row)
        self.ui.pt_cash_name.setPlainText(selected_row[0].text() if selected_row_len > 0 else '')
        self.ui.pt_cash_price.setPlainText(selected_row[1].text() if selected_row_len > 1 else '')
        self.ui.pt_cash_descr.setPlainText(selected_row[2].text() if selected_row_len > 2 else '')
        # clipboard.setText(text)

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                # print(child.widget())
                child.widget().deleteLater()

    @staticmethod
    def list_to_string(lst):
        return ' '.join([str(elem) for elem in lst if len(str(elem)) > 3])

    @QtCore.pyqtSlot("QWidget*", "QWidget*")
    def on_focusChanged(self, old, now):
        if now is None:
            pass
            # print(f"\nwindow is the active window: {self.isActiveWindow()}")
            # self.setWindowState(QtCore.Qt.WindowMinimized)
        else:
            self.model_list_widget.hide()
            self.search_input.setFocus()
            self.search_input.selectAll()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(QMainWindow, self).resizeEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Alt:
            # print(f'TAB {self.ui.tab_widget.currentIndex()=}')
            if self.ui.tab_widget.currentIndex() == 0:
                self.ui.tab_widget.setCurrentIndex(1)
            else:
                self.ui.tab_widget.setCurrentIndex(0)
        if event.key() == Qt.Key_Escape:
            # print(f'TAB {self.ui.tab_widget.currentIndex()=}')
            self.model_list_widget.hide()

        if event.key() == Qt.Key_F2:
            if self.current_theme < len(self.themes) - 1:
                self.current_theme += 1
            else:
                self.current_theme = 0
            set_application_style(self.themes[self.current_theme])

        self.search_input.setFocus()
        self.search_input.selectAll()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # print(f'{self.ui.HEAD.height()=}   {event.y()=}')
        if self.model_list_widget.isHidden():
            if event.y() > self.ui.HEAD.height():
                return
            if self.models and (0 <= self.model_list_widget.currentRow() < len(self.models[self.curr_manufacturer])):
                self.upd_models_list()

        if event.angleDelta().y() < 0:
            self.upd_manufacturer_wheel(increment=1)
        if event.angleDelta().y() > 0:
            self.upd_manufacturer_wheel(increment=-1)

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu:
            if source in (self.ui.table_parts, self.ui.table_accesory, self.ui.table_price):
                row = source.selectedItems()
                # print(f'{row=}')
                if row:
                    # user = str(row[0].data())
                    contextMenu = QMenu(self)
                    copy_for_order = contextMenu.addAction("Копировать для заказа")
                    copy_full_row = contextMenu.addAction("Копировать всю строку")
                    action = contextMenu.exec_(event.globalPos())
                    if action == copy_for_order:
                        if source is self.ui.table_price:
                            self.copy_table_items(source, 1)
                        else:
                            self.copy_table_items(source, 4)
                    if action == copy_full_row:
                        self.copy_table_items(source)
        return super().eventFilter(source, event)

    def open_adv_search(self):
        settings_ui = AdvancedSearchWindow(self)
        settings_ui.setWindowIcon(QtGui.QIcon(C.LOGO))
        settings_ui.exec_()
        settings_ui.show()

    def open_settings(self):
        settings_ui = ConfigWindow(C, self, DK9)
        settings_ui.setWindowIcon(QtGui.QIcon(C.LOGO))
        settings_ui.exec_()
        settings_ui.show()

    def open_help(self):
        help_ui = HelpWindow(C, self)
        help_ui.setWindowIcon(QtGui.QIcon(C.LOGO))
        help_ui.exec_()
        help_ui.show()

    @staticmethod
    def error(errors: tuple):
        msg_box = QMessageBox()
        text, info = '', ''
        for i, e in enumerate(errors):
            if i == 0:
                text = str(e)
            else:
                info = f'{info}\n{str(e)}'
        print(f'{text}\n -> {info}')
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setInformativeText(str(info))
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        msg_box.show()


class SearchInput(QLineEdit):
    def __init__(self, main_app: type(App)):
        super().__init__()
        self.app = main_app
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(540, 30))
        self.setMaximumSize(QtCore.QSize(540, 30))
        self.setBaseSize(QtCore.QSize(540, 30))

        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(17)
        self.setFont(font)
        self.setMaxLength(32)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("search_input")

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.app.models \
                and (0 <= self.app.model_list_widget.currentRow() < len(self.app.models[self.app.curr_manufacturer])
                     or self.app.model_list_widget.isHidden()):

            if self.app.model_list_widget.isHidden():
                self.app.upd_models_list()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super(SearchInput, self).keyPressEvent(event)
        if self.app.models \
                and (0 <= self.app.model_list_widget.currentRow() < len(self.app.models[self.app.curr_manufacturer])
                     or self.app.model_list_widget.isHidden()):

            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if self.app.model_list_widget.isHidden():
                    self.app.upd_models_list()
                    return
                self.app.scheduler(self.app.model_list_widget.currentItem())

            elif event.key() == Qt.Key_Up:
                idx = self.app.model_list_widget.currentRow() - 1
                if idx < 0:
                    idx = len(self.app.models[self.app.curr_manufacturer]) - 1
                self.app.model_list_widget.setCurrentRow(idx)

            elif event.key() == Qt.Key_Down:
                if self.app.model_list_widget.isHidden():
                    self.app.upd_models_list()
                    return
                idx = self.app.model_list_widget.currentRow() + 1
                if idx > len(self.app.models[self.app.curr_manufacturer]) - 1:
                    idx = 0
                self.app.model_list_widget.setCurrentRow(idx)

        if event.key() == Qt.Key_Right:
            self.app.upd_manufacturer_wheel(increment=1)

        if event.key() == Qt.Key_Left:
            self.app.upd_manufacturer_wheel(increment=-1)


def set_application_style(style):
    app.setStyle(style)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(C.LOGO))
        clipboard = app.clipboard()
        window = App()
        window.setWindowIcon(QtGui.QIcon(C.LOGO))
        QtCore.QTimer.singleShot(1, window.on_ui_loaded)
        window.search_input.setFocus()
        sys.exit(app.exec_())
    except Exception as err:
        App.error((f'Global Error',
                   f'{traceback.format_exc()}'))
