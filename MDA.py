import sys
import webbrowser
from datetime import datetime
import bs4
import traceback
import os
import re
from utility.utils import save_error_file

sys.path.append(os.path.join(os.getcwd(), 'PyQt5'))
# sys.path.append(os.path.join(os.getcwd(), 'PyQt5\\Qt5'))
# sys.path.append(os.path.join(os.getcwd(), 'PyQt5\\QtWidgets'))
# print(f'{sys.path=}')

os.add_dll_directory(os.getcwd())
# os.add_dll_directory(f'{os.getcwd()}\\PyQt5\\Qt5')
# os.add_dll_directory(f'{os.getcwd()}\\PyQt5\\QtWidgets')
# print(f'{os.path=}')

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMenu, QTableWidget, \
    QHeaderView, qApp, QMessageBox, QSizePolicy, QLineEdit, QSpacerItem, QPushButton, QLabel, QStyleFactory
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QEvent

from utility.config import Config, DK9_CACHE_FILE_PATH, VERSION_FILE_PATH, LOGO
from utility.dk9 import DK9Parser
from utility.price import Price, PriceColumns, MAX_PRICE_COLUMNS
from utility.statistic import MDAS
from utility.language import Language
from utility.modal_windows import ConfigWindow, HelpWindow, AdvancedSearchWindow, FirstStartWindow
from utility.modal_graph_win import GraphWindow
from utility.thread_worker import Worker, WorkerSignals
from utility.update_checker import is_update_available
from UI.window_main import Ui_MainWindow

C = Config()
DK9 = DK9Parser(C)
MDAS = MDAS(C)
L = Language(C)


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

        self.DK9_BG_COLOR_SEL_BY_PRICE = QtGui.QColor(*C.DK9_BG_COLOR_SEL_BY_PRICE)
        self.DK9_BG_COLOR_SEL_BY_PRICE_GRAD = QtGui.QLinearGradient(0, 0, 120, 0)
        # self.DK9_BG_COLOR_SEL_BY_PRICE_GRAD.setColorAt(0, Qt.red)
        self.DK9_BG_COLOR_SEL_BY_PRICE_GRAD.setColorAt(0.03,
                                                       self.DK9_BG_COLOR_SEL_BY_PRICE)  # QtGui.QColor(255, 255, 210))

        self.models = {}
        self.model_buttons = {}
        self.manufacturer_wheel = None
        self.current_model_button_index = 0
        # self.dk9_cache = {}
        # self.dk9_cache_update_time = 0
        self.ui = Ui_MainWindow()
        # self.ui = MainUI()
        self.ui.setupUi(self)
        DK9.CACHE.set_app(self)
        self.dk9_request_label = QLabel()
        self.work_cost_label = QLabel()

        self.search_input = SearchInput(self)
        self.search_input.setParent(self.ui.frame_3)
        self.ui.search_layout.addWidget(self.search_input)

        self.model_list_widget = QTableWidget()  # QListWidget()
        self.model_list_widget.setColumnCount(2)
        # self.model_list_widget.setHorizontalHeaderLabels('f')
        self.model_list_widget.verticalHeader().hide()
        self.model_list_widget.horizontalHeader().hide()
        self.ui.update_button.hide()
        # widget_width = self.search_input.width()
        # self.model_list_widget.setMaximumWidth(widget_width)
        # column_0_width = int(widget_width * 0.9)
        # self.model_list_widget.setColumnWidth(0, column_0_width)
        # self.model_list_widget.setColumnWidth(1, widget_width - column_0_width - 2)
        # self.model_list_widget.setHorizontalScrollBarPolicy(1)  # Allways off

        L.Parent = self.ui
        L.apply_lang()
        MDAS.error = self.error

        self.freeze_ui_update = True

        self.copied_table_items = {}
        self.selected_work_price = 0
        self.selected_part_price = 0
        # self.copied_table_item_colors = {}

        self.web_table_stylesheet_template = (
            "QTableWidget::item:hover{"
            f"background-color : rgb{C.DK9_BG_HOVER_COLOR};"
            "border-top: 1px solid #6a6ea9;border-bottom: 1px solid #6a6ea9;}"
            "QTableWidget::item:selected{"
            "background: qlineargradient"
            f"(x1: 0, y1: 0, x2: 0, y2: 0.8, stop: 0 rgb{C.DK9_BG_HOVER_COLOR}, stop: 1 rgb",
            ");border-top: 1px solid #6a6ea9;border-bottom: 1px solid #6a6ea9;}"
        )

        self.default_web_table_stylesheet = f"{self.web_table_stylesheet_template[0]}" \
                                            f"{C.DK9_BG_HOVER_COLOR});" \
                                            f"{self.web_table_stylesheet_template[1]}"

        self.upd_ui_static_texts()
        self.upd_username()
        self.init_ui_statics()
        self.apply_window_size()
        self.init_ui_dynamics()

        self.stat_send_timer = QtCore.QTimer()
        self.stat_send_timer.timeout.connect(self.stat_send_start_worker)

        self.dk9_cache_timer = QtCore.QTimer()
        self.dk9_cache_timer.timeout.connect(self.dk9_login_than_cash_update_workers_sequence)

        self.curr_manufacturer_idx: int = 0
        self.curr_manufacturer: str = ''
        # self.curr_manufacturers: tuple = ()
        self.curr_type: str = ''
        self.curr_model: str = ''  # --------------------------------------
        self.compatible_parts: list = []
        # self.curr_model_idx: int = 0
        self.curr_description: str = ''
        self.recursor = ' -> '

        self.statify_next_request: bool = False
        self.search_req_ruled: str = ''
        self.search_again = False
        self.got_login_on_search_try_relog = False
        # self.old_search = ''
        self.thread = QtCore.QThread
        self.dk9_cache_handler_worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        self.request_worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        self.file_io_worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        self.Price = Price(C)
        self.soup = None
        self.web_status = DK9.STATUS.NO_CONN
        self.price_status = 0

        # self.themes = ('windowsvista', 'Fusion', 'Windows')
        self.themes = (*QStyleFactory.keys(),)
        self.current_theme = 0
        # self.dk9_login_start_worker()
        self.update_web_status(0)
        # self.update_price_status()
        self.show()
        if C.FIRST_START:
            C.FIRST_START = False
            self.open_first_start()

    def upd_ui_static_texts(self):
        self.ui.pb_adv_search.setToolTip(L.pb_adv_search_ToolTip)
        self.ui.chb_show_exact.setToolTip(L.chb_show_exact_ToolTip)
        self.ui.chb_show_date.setToolTip(L.chb_show_date_ToolTip)
        # self.ui.chb_price_name_only.setToolTip(L.chb_price_name_only_ToolTip)
        self.ui.chb_search_eng.setToolTip(L.chb_search_eng_ToolTip)
        self.ui.chb_search_narrow.setToolTip(L.chb_search_narrow_ToolTip)
        self.ui.chb_show_compatibility.setToolTip(L.chb_show_compatibility_ToolTip)
        self.ui.table_price.setHorizontalHeaderLabels((L.table_price_HHL))
        self.ui.table_parts.setHorizontalHeaderLabels((L.table_parts_HHL))
        self.ui.table_accesory.setHorizontalHeaderLabels((L.table_accesory_HHL))

    def upd_username(self):
        if C.DK9_LOGIN:
            self.ui.lb_username.setText(C.DK9_LOGIN)
        else:
            self.ui.lb_username.setText('*****')

    def init_ui_statics(self):

        self.resized.connect(self.init_ui_dynamics)
        self.search_input.textChanged[str].connect(self.prepare_and_search)
        self.ui.bt_upd_web.clicked.connect(self.dk9_relog_or_update_cache_by_button)
        self.ui.bt_upd_price.clicked.connect(self.read_price_start_worker)
        self.ui.chb_show_exact.stateChanged.connect(self.upd_dk9_on_rule_change)
        self.ui.chb_show_date.stateChanged.connect(self.switch_n_upd_dk9_tables_grid)
        # self.ui.chb_price_name_only.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_show_compatibility.stateChanged.connect(self.switch_compat_upd_price_tables_grid)
        self.ui.chb_search_eng.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_narrow.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.pb_adv_search.clicked.connect(self.open_adv_search)
        self.ui.settings_button.clicked.connect(self.open_settings)
        self.ui.graph_button.clicked.connect(self.open_graphs)

        self.ui.le_cash_name.installEventFilter(self)
        self.ui.le_cash_name.selectionChanged.connect(lambda: self.ui.le_cash_name.setSelection(0, 0))
        self.ui.le_cash_price.installEventFilter(self)
        self.ui.le_cash_price.selectionChanged.connect(lambda: self.ui.le_cash_price.setSelection(0, 0))
        self.ui.le_cash_descr.installEventFilter(self)
        self.ui.le_cash_descr.selectionChanged.connect(lambda: self.ui.le_cash_descr.setSelection(0, 0))

        self.ui.table_parts.doubleClicked.connect(self.copy_web_table_items_connected)
        self.ui.table_accesory.doubleClicked.connect(self.copy_web_table_items_connected)
        self.ui.table_parts.itemSelectionChanged.connect(self.handle_web_table_item_selection_connected)
        self.ui.table_accesory.itemSelectionChanged.connect(self.handle_web_table_item_selection_connected)
        self.ui.table_parts.installEventFilter(self)
        self.ui.table_accesory.installEventFilter(self)
        self.ui.table_price.itemSelectionChanged.connect(self.handle_price_table_item_selection_connected)
        self.ui.table_price.doubleClicked.connect(self.copy_price_table_item_connected)
        self.ui.table_price.installEventFilter(self)
        self.ui.help.clicked.connect(self.open_help)

        self.dk9_request_label.setParent(self.ui.tab_widget)
        self.dk9_request_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.dk9_request_label.setFixedWidth(80)
        self.dk9_request_label.setAlignment(Qt.AlignRight)

        self.work_cost_label.setParent(self.ui.tab_widget)
        self.work_cost_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.work_cost_label.setFixedWidth(240)
        self.work_cost_label.setAlignment(Qt.AlignRight)

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
        self.model_list_widget.itemClicked.connect(self.filter_item_text_search_visualise)
        self.model_list_widget.hide()

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
        self.ui.table_price.setFont(self.tab_font)
        self.ui.table_parts.setFont(self.tab_font)
        self.ui.table_accesory.setFont(self.tab_font)
        self.ui.le_cash_name.setFont(self.tab_font)
        self.ui.le_cash_descr.setFont(self.tab_font)
        self.ui.le_cash_price.setFont(self.tab_font)
        self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                 num=0, tab_names=C.DK9_TABLE_NAMES, count_1=0, count_2=0)
        self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                 num=1, tab_names=C.DK9_TABLE_NAMES, count_1=0, count_2=0)

        self.model_list_widget.setFont(self.tab_font)
        self.fix_models_list_position()

        self.upd_dk9_tables_grid()
        self.upd_price_tables_grid()
        self.upd_tables_row_heights(force=True)

        self.freeze_ui_update = True
        self.ui.chb_show_exact.setCheckState(2 if C.FILTER_SEARCH_RESULT else 0)
        # self.ui.chb_price_name_only.setCheckState(2 if C.SEARCH_BY_PRICE_MODEL else 0)
        self.ui.chb_search_eng.setCheckState(2 if C.LATIN_SEARCH else 0)
        self.ui.chb_search_narrow.setCheckState(2 if C.NARROW_SEARCH else 0)
        self.ui.chb_show_compatibility.setCheckState(2 if C.SHOW_COMPATIBILITY else 0)
        self.freeze_ui_update = False

        self.dk9_request_label.move(self.ui.table_parts.width() - 84, 3)
        self.dk9_request_label.setFont(self.ui_font_bold)

        self.work_cost_label.move(self.ui.table_parts.width() - 340, 3)
        self.work_cost_label.setFont(self.ui_font_bold)

        self.ui.model_widget.setFixedWidth((self.width() - 6) // 2)  # model_buttons layout

        self.model_list_widget.setStyleSheet(
            "QTableWidget::item"
            "{"
            # "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 lightgreen, stop: 1 #DCF1DE);"
            "border: 1px solid #ffffff;"
            # "background-color : lightgreen;"
            "}"
            "QTableWidget::item:hover"
            "{"
            "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 lightgreen, stop: 1 #DCF1DE);"
            # "border: 1px solid #6a6ea9;"
            # "background-color : lightgreen;"
            "}"
            "QTableWidget::item:selected"
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

        self.ui.table_parts.setStyleSheet(self.default_web_table_stylesheet)

        self.ui.table_accesory.setStyleSheet(self.default_web_table_stylesheet)

        # self.ui.le_cash_name.setStyleSheet(
        #     "QPlainTextEdit"
        #     "{selection-background-color: #b5BfF3;"
        #     # "selection-color:white;"
        #     "}")
        #
        # self.ui.le_cash_price.setStyleSheet(
        #     "QPlainTextEdit"
        #     "{selection-background-color: #b5BfF3;}")
        #
        # self.ui.le_cash_descr.setStyleSheet(
        #     "QPlainTextEdit"
        #     "{selection-background-color: #b5BfF3;}")

    # =============================================================================================================

    def fix_models_list_position(self):
        widget_width = self.search_input.width()
        self.model_list_widget.setFixedWidth(widget_width)
        column_0_width = int(widget_width * 0.9)
        self.model_list_widget.setColumnWidth(0, column_0_width)
        self.model_list_widget.setColumnWidth(1, widget_width - column_0_width - 2)
        self.model_list_widget.move(int(self.ui.search_widget.x() + 12),
                                    int(self.ui.HEAD.height() - 6))

    def start_search_on_rule_change(self):
        if self.freeze_ui_update:
            return
        # C.SEARCH_BY_PRICE_MODEL = True if self.ui.chb_price_name_only.checkState() == 2 else False
        C.LATIN_SEARCH = True if self.ui.chb_search_eng.checkState() == 2 else False
        C.NARROW_SEARCH = True if self.ui.chb_search_narrow.checkState() == 2 else False
        C.SHOW_COMPATIBILITY = True if self.ui.chb_show_compatibility.checkState() == 2 else False
        self.prepare_and_search(search_req=self.search_input.text(), force_search=True)

    def upd_dk9_on_rule_change(self):
        if self.freeze_ui_update:
            return
        C.FILTER_SEARCH_RESULT = True if self.ui.chb_show_exact.checkState() == 2 else False
        if self.soup:
            self.dk9_fill_tables_from_soup(use_old_soup=True)

    def switch_compat_upd_price_tables_grid(self):
        C.SHOW_COMPATIBILITY = True if self.ui.chb_show_compatibility.checkState() == 2 else False
        self.upd_price_tables_grid()

    def upd_price_tables_grid(self):
        table_width = (self.width() - 6)//2
        # print(f'{----------------------------------table_width=}')
        if C.SHOW_COMPATIBILITY:
            self.ui.table_price.showColumn(2)
            table_width_n_percent = int(table_width / 5 + (table_width - 640) / 4)
            # self.ui.table_price.horizontalHeader().setSectionResizeMode(2, table_width_n_percent)
        else:
            self.ui.table_price.hideColumn(2)
            table_width_n_percent = int(table_width / 2.5 + (table_width - 640) / 4)

        self.ui.table_price.horizontalHeader().setDefaultSectionSize(table_width_n_percent)
        self.ui.table_price.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.table_price.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

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

    def upd_tables_row_heights(self, force: bool = False, dk9: bool = False, price: bool = False):
        if dk9 and C.WORD_WRAP_DK9:
            self.ui.table_parts.resizeRowsToContents()
            self.ui.table_accesory.resizeRowsToContents()
            return

        if price and C.WORD_WRAP_PRICE:
            self.ui.table_price.resizeRowsToContents()
            return

        if force:
            if C.WORD_WRAP_DK9:
                self.ui.table_parts.resizeRowsToContents()
                self.ui.table_accesory.resizeRowsToContents()
            else:
                self.ui.table_parts.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
                self.ui.table_accesory.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
            if C.WORD_WRAP_PRICE:
                self.ui.table_price.resizeRowsToContents()
            else:
                self.ui.table_price.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)

    def on_ui_loaded(self):
        print('Loading Price')
        self.read_price_start_worker()

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

        # self.search_req_ruled = result_req
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
        self.upd_manufacturer_wheel(increment=int(self.sender().objectName()[-1]) - 4)

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
        if self.model_list_widget.isHidden() or increment == 0:
            self.curr_manufacturer_idx = int(_len / 2)
        self.curr_manufacturer_idx += increment
        if self.curr_manufacturer_idx > _len:
            self.curr_manufacturer_idx = _len
        if self.curr_manufacturer_idx < 0:
            self.curr_manufacturer_idx = 0

        # print(f'{self.curr_manufacturer_idx=} {_len=}')
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
            # self.model_list_widget.items.addItems(models_list)
            self.model_list_widget.setRowCount(size)
            row_height = 24
            for row, model_ in enumerate(models_list):
                link_stat_1 = QTableWidgetItem(model_)
                link_stat_1.setData(1, model_)
                link_stat_2 = QTableWidgetItem('')
                link_stat_2.setData(1, model_)
                self.model_list_widget.setItem(row, 0, link_stat_1)
                self.model_list_widget.setItem(row, 1, link_stat_2)
                self.model_list_widget.setRowHeight(row, row_height)
                # self.model_list_widget.item(row, 0).setStyleSheet(self.model_list_widget_style)
            # self.model_list_widget.setCurrentRow(0)
            self.model_list_widget.setCurrentCell(0, 0)
            self.model_list_widget.setFixedHeight((row_height * size) + 2)
            # self.model_list_widget.setFixedHeight(self.model_list_widget.sizeHintForRow(0) * (size + 1))

    def upd_model_buttons(self, model_names):
        lay = self.ui.lay_model_buttons
        self.clear_layout(lay)

        le = len(self.models)
        self.model_buttons = {}
        self.current_model_button_index = 0
        for num, model in enumerate(model_names):
            self.model_buttons[num] = QPushButton(model)
            self.model_buttons[num].clicked.connect(self.dk9_search_by_button)
            if num == 0:
                self.model_buttons[num].setDefault(True)
                # self.curr_model = model
                # if self.web_status == DK9.STATUS.OK:
                #     if DK9.LOGIN_SUCCESS:
                #         self.dk9_search_start_worker()
                # else:
                #     self.dk9_login_start_worker()
            lay.addWidget(self.model_buttons[num], 0)
            le -= 1
        self.ui.model_widget.setFixedWidth((self.width() - 6) // 2)
        # sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        # lay.addItem(sp)

    def update_price_status(self, status: int):
        self.price_status = status
        if status in C.PRICE_STATUSES.keys():
            self.ui.price_status.setText(C.PRICE_STATUSES[status])
        else:
            self.ui.price_status.setText(self.Price.NAME)
        # print(f'{self.price_status=}')

    def schedule_statify(self, item):
        self.statify_next_request = True
        self.filter_item_text_search_visualise(item)

    # @QtCore.pyqtSlot
    def filter_item_text_search_visualise(self, item):
        if item.text():
            self.statify_next_request = True
        text_lower: str = item.data(1).lower()
        text_lower_orig = text_lower[:]
        # print(f'Scheduler: {text_lower=}')
        text_lower = self.filter_trash_from_models_string(text_lower)
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

        # if C.SEARCH_BY_PRICE_MODEL:
        #     self.curr_model = models_for_buttons[0]
        # else:
        #     self.curr_model = self.search_req_ruled

        self.curr_model = models_for_buttons[0]
        self.dk9_search_or_login()
        self.upd_models_list(clear=True)
        self.upd_model_buttons(models_for_buttons)
        self.update_price_table(text_lower_orig, recursive_model)
        self.upd_tables_row_heights(price=True)

    @staticmethod
    def filter_trash_from_models_string(_string: str):
        result_string = _string
        for i in range(len(result_string) - 2):
            remark_start = result_string.find('(')
            if remark_start >= 0:
                remark_end = result_string[remark_start:].find(')')
                # print(f'{text_lower[:remark_start]=}  {text_lower[ + remark_end:]=}')
                # print(f'{remark_start=}  {remark_end=}')
                result_string = f'{result_string[:remark_start]}' \
                                f'{result_string[remark_start + remark_end + 1:]}'
            else:
                break
        return result_string

    def read_price_start_worker(self):
        self.file_io_worker = Worker()
        signals = WorkerSignals()
        signals.finished.connect(self.price_read_finished)
        signals.progress.connect(self.price_read_finished)
        signals.status.connect(self.update_price_status)
        signals.error.connect(self.error)
        self.file_io_worker.add_task(self.Price.load_price, signals, 0)
        print('Starting thread to read price')
        self.thread.start(self.file_io_worker, priority=QtCore.QThread.Priority.HighestPriority)

    # =============================================== MDAS ======================================================

    def stat_send_start_worker(self):
        print('Starting thread to send stats')
        self.request_worker = Worker()
        signals = WorkerSignals()
        signals.finished.connect(self.stat_send_finished)
        self.request_worker.add_task(MDAS.send_statistic_cache, signals, 3)
        self.thread.start(self.request_worker)

    def stat_send_finished(self):
        if MDAS.cache_to_send:
            C.stat_delay = C.STAT_RESEND_DELAY
        else:
            self.reset_stat_timer()

    def reset_stat_timer(self):
        C.stat_delay = C.STAT_CACHE_DELAY
        self.stat_send_timer.stop()

    def add_to_statistic(self, branch, brand, model):
        if branch == 0 \
                or not self.statify_next_request \
                or not brand \
                or not self.curr_model:  # +++++prod
            return
        print(f'MDAS SCHEDULE TO SEND: {branch} {brand} {model}')
        # print(f'Add request to statistic: {self.curr_model}')
        self.statify_next_request = False
        self.stat_send_timer.stop()
        cache_full = MDAS.cache_item(branch=branch, brand=brand, model=model)  # +++++prod
        # self.stat_send_scheduled = True
        if cache_full == 0:  # Not full - standard delay
            self.stat_send_timer.start(C.STAT_CACHE_DELAY)
        elif cache_full == 1:  # Full+ - time to send
            self.stat_send_timer.stop()
            signals = WorkerSignals()
            signals.finished.connect(self.stat_send_finished)
            self.request_worker.add_task(MDAS.send_statistic_cache, signals, 1)
        else:  # Overflowing or STOPPED Overflow - no connection to stat server, longer delay
            self.stat_send_timer.start(C.STAT_RESEND_DELAY)

    # =============================================== DK9 ======================================================

    def update_web_status(self, status: int):
        if status in C.WEB_STATUSES:
            self.web_status = status
            if self.web_status in (DK9.STATUS.FILE_UPDATED, DK9.STATUS.FILE_USED_OFFLINE):
                datetime_formatted = DK9.CACHE.cache['updated']
                self.ui.web_status.setText(f'{C.WEB_STATUSES[status]} - {datetime_formatted}')
            else:
                self.ui.web_status.setText(C.WEB_STATUSES[status])
            if DK9.LAST_ERROR_PAGE_TEXT:
                self.ui.web_status.setToolTip(f'Error Page: '
                                              f'{DK9.LAST_ERROR_PAGE_TEXT}')
                DK9.LAST_ERROR_PAGE_TEXT = ''
        else:
            print(f'Error: status code {status} not present {C.WEB_STATUSES=}')

    # start by model button
    def dk9_search_by_button(self):
        if self.price_status == 6:
            self.curr_model = self.sender().text()
            self.dk9_search_or_login()

    # start by reconnect|reload button
    def dk9_relog_or_update_cache_by_button(self):
        print('dk9_relog_or_update_cache_by_button')
        if self.price_status == 6 and self.web_status not in \
                (
                        DK9.STATUS.CONNECTING,
                        DK9.STATUS.REDIRECT,
                        DK9.STATUS.FILE_READ,
                        DK9.STATUS.FILE_WRITE,
                        DK9.STATUS.UPDATING,
                        # DK9.STATUS.FILE_USED_OFFLINE
                ):  # Keep on, if manual cache reload is needed
            if C.DK9_CACHING:
                self.dk9_upd_cache_restart_timer()
            elif self.web_status != DK9.STATUS.OK:
                self.dk9_login_start_worker()

    # start on app start
    def dk9_login_or_update_cache_on_start(self):
        print('dk9_login_or_update_cache_on_start')
        if C.DK9_CACHING:
            self.dk9_read_cache_if_exist()
            self.dk9_login_start_worker(self.dk9_upd_cache_restart_timer)
        elif self.web_status != DK9.STATUS.OK:
            self.dk9_login_start_worker()

        # Check for updated version of the program
        upd_check_result = is_update_available(VERSION_FILE_PATH, C.UPDATE_URL)
        if upd_check_result is True:
            self.ui.update_button.show()
            self.ui.update_button.clicked.connect(self.open_update_page)
        elif upd_check_result is not False:
            self.update_price_progress_bar(progress=0, style_sheet=C.PB_STYLE_SHEET_WARN)
            save_error_file(f"Can't get update info from web server:\n{upd_check_result}")

    def open_update_page(self):
        self.ui.update_button.hide()
        webbrowser.open(C.UPDATE_URL)

    # @QtCore.pyqtSlot
    def dk9_search_or_login(self):
        print(f'dk9_search_or_login. {DK9.STATUS=}')
        if C.DK9_CACHING and DK9.CACHE.cache:
            self.dk9_search_start_worker()
        elif self.web_status in (DK9.STATUS.OK, DK9.STATUS.FILE_UPDATED):
            if DK9.LOGIN_SUCCESS:
                self.dk9_search_start_worker()
        elif self.web_status == DK9.STATUS.FILE_USED_OFFLINE:
            self.dk9_search_start_worker()
        else:
            # if C.DK9_CACHING:
            #     self.dk9_login_start_worker(next_method=self.dk9_upd_cache_restart_timer)
            # else:
            self.dk9_login_start_worker()

    def dk9_get_search_signals(self):
        signals = WorkerSignals()
        signals.result.connect(self.dk9_fill_tables_from_soup)
        signals.progress.connect(self.web_progress_bar)
        signals.status.connect(self.update_web_status)
        signals.finished.connect(self.dk9_finish_progress_bar_status)
        signals.error.connect(self.error)
        return signals

    def dk9_login_start_worker(self, next_method=None):
        self.request_worker = Worker()
        signals = WorkerSignals()
        signals.progress.connect(self.web_progress_bar)
        signals.status.connect(self.update_web_status)
        signals.error.connect(self.error)
        if not C.DK9_CACHING and self.curr_model:
            self.search_again = True
            signals.finished.connect(self.dk9_search_start_worker)
        else:
            signals.finished.connect(next_method or self.dk9_finish_progress_bar_status)
        print('Starting thread to login')
        self.request_worker.add_task(DK9.login, signals, 2)
        self.thread.start(self.request_worker)

    def dk9_search_start_worker(self, advanced: dict = None):

        print(f'STARTING SEARCH... {self.web_status=}  {self.price_status=} {DK9.LOGIN_SUCCESS=}')
        # -------------------ASUS brand name filter
        manufacturer = 'Asus' if 'asus' in self.curr_manufacturer.lower() else self.curr_manufacturer

        if C.DK9_CACHING:
            if DK9.CACHE.cache:
                self.dk9_fill_tables_from_cache_dict()
                # if C.SEARCH_BY_PRICE_MODEL:
                self.add_to_statistic(branch=C.BRANCH, brand=manufacturer, model=self.curr_model)
            else:
                if os.path.exists(DK9_CACHE_FILE_PATH):
                    self.dk9_read_cache_start_worker()
                else:
                    self.dk9_login_start_worker(self.dk9_upd_cache_restart_timer)
                # elif not DK9.LOGIN_SUCCESS:
                #     self.dk9_login_start_worker(self.dk9_upd_cache_restart_timer)
                # else:
                #     self.dk9_upd_cache_restart_timer()
            return

        if not DK9.LOGIN_SUCCESS or self.web_status not in \
                (
                        DK9.STATUS.OK,
                        DK9.STATUS.FILE_UPDATED,
                        DK9.STATUS.FILE_USED_OFFLINE,
                        DK9.STATUS.FILE_READ_ERR,
                        DK9.STATUS.FILE_WRITE_ERR,
                ):
            return

        # Auto reset filter on search
        C.FILTER_SEARCH_RESULT = False
        self.ui.chb_show_exact.setCheckState(2 if C.FILTER_SEARCH_RESULT else 0)
        self.request_worker = Worker()
        # TODO==============================================================================================================
        if advanced:
            signals = self.dk9_get_search_signals()
            self.request_worker.add_task(DK9.adv_search,
                                         signals,
                                         2,
                                         advanced['_type'],
                                         advanced['_manufacturer'],
                                         advanced['_model'],
                                         advanced['_description'])
        else:

            if self.search_again:
                self.search_again = False

            # ===========================  statistic  ==============================
            # elif manufacturer and self.curr_model and self.statify_next_request:  # -----test
            elif C.BRANCH > 0 and manufacturer and self.curr_model and self.statify_next_request:  # +++++prod
                self.add_to_statistic(branch=C.BRANCH, brand=manufacturer, model=self.curr_model)
            # if C.SEARCH_BY_PRICE_MODEL:
            #     self.add_to_statistic(branch=C.BRANCH, brand=manufacturer, model=self.curr_model)

            # ===========================  search in dk9  ==============================
            self.dk9_request_label.setText(self.curr_model)
            self.request_worker = Worker()
            signals = self.dk9_get_search_signals()
            self.request_worker.add_task(DK9.adv_search,
                                         signals,
                                         2,
                                         self.curr_type,
                                         manufacturer,
                                         self.curr_model,
                                         self.curr_description)
        self.thread.start(self.request_worker)

    def dk9_fill_tables_from_soup(self, table_soups: type(bs4.BeautifulSoup) = None, use_old_soup: bool = False):
        print(f'dk9_fill_tables_from_soup {self.web_status=} {use_old_soup=}')
        if not use_old_soup:
            if DK9.check_soups_is_broken(table_soups):
                return
            self.soup = table_soups
            # if not self.soup:
            #     self.update_web_status(DK9.STATUS.NO_CONN)
            # elif not self.soup[0]:
            #     self.update_web_status(DK9.STATUS.OK)

        if self.web_status in (DK9.STATUS.OK, DK9.STATUS.UPDATING):
            self.web_progress_bar(70)
            self.ui.table_parts.setSortingEnabled(False)
            self.ui.table_accesory.setSortingEnabled(False)
            self.dk9_fill_table_from_soup(self.soup, self.ui.table_parts, 0,
                                          C.DK9_TABLE_NAMES, C.DK9_BG_P_COLOR1, C.DK9_BG_P_COLOR2, 5,
                                          align={4: Qt.AlignRight | Qt.AlignVCenter})
            self.dk9_fill_table_from_soup(self.soup, self.ui.table_accesory, 1,
                                          C.DK9_TABLE_NAMES, C.DK9_BG_A_COLOR1, C.DK9_BG_A_COLOR2, 5,
                                          align={4: Qt.AlignRight | Qt.AlignVCenter})
            self.web_progress_bar(85)
            self.ui.table_parts.sortByColumn(3, Qt.SortOrder(0))
            self.ui.table_parts.sortByColumn(2, Qt.SortOrder(0))
            self.ui.table_parts.sortByColumn(0, Qt.SortOrder(0))
            self.ui.table_parts.setSortingEnabled(True)
            self.ui.table_accesory.sortByColumn(3, Qt.SortOrder(0))
            self.ui.table_accesory.sortByColumn(2, Qt.SortOrder(0))
            self.ui.table_accesory.sortByColumn(0, Qt.SortOrder(0))
            self.ui.table_accesory.setSortingEnabled(True)

            self.upd_tables_row_heights(dk9=True)
        else:
            self.dk9_login_start_worker()
        self.web_progress_bar(0) if use_old_soup else self.web_progress_bar(100)

    # ======================================== CACHE WEB DATABASE (DK9) ===============================================

    def dk9_upd_cache_restart_timer(self, period=C.DK9_CACHING_PERIOD * 60_000,
                                    allow_update=True):  # * 60_000============================
        print(f'dk9_upd_cache_restart_timer: {period // 60_000}minutes')
        self.dk9_cache_timer.stop()
        if allow_update:
            self.dk9_login_than_cash_update_workers_sequence()
            # self.dk9_cache_updater_start_worker()
        # self.dk9_update_cache_start_worker()
        self.dk9_cache_timer.start(period)  # * 60_000

    def dk9_upd_cache_stop_timer(self):
        print(f'dk9_upd_cache_stop_timer')
        self.dk9_cache_timer.stop()

    # def dk9_restart_caching_schedule(self):
    #     self.dk9_cache_timer.stop()
    #     self.dk9_cache_timer.start(C.DK9_CACHING_PERIOD)

    def dk9_fill_tables_from_cache_dict(self):
        print(f'dk9_fill_tables_from_cache_dict. {self.web_status=}')
        # if self.web_status == DK9.STATUS.FILE_USED_OFFLINE:
        self.web_progress_bar(70)
        self.ui.table_parts.setSortingEnabled(False)
        self.ui.table_accesory.setSortingEnabled(False)
        found_parts, found_accessories = DK9.CACHE.search_rows_in_cache_dict()
        # print(f'search result:\n{found_parts=}\n{found_accessories=}')
        self.dk9_fill_one_table_from_dict(found_parts, self.ui.table_parts, 0,
                                          C.DK9_TABLE_NAMES, C.DK9_BG_P_COLOR1, C.DK9_BG_P_COLOR2, 6,
                                          align={4: Qt.AlignRight | Qt.AlignVCenter})
        self.dk9_fill_one_table_from_dict(found_accessories, self.ui.table_accesory, 1,
                                          C.DK9_TABLE_NAMES, C.DK9_BG_A_COLOR1, C.DK9_BG_A_COLOR2, 6,
                                          align={4: Qt.AlignRight | Qt.AlignVCenter})

        self.web_progress_bar(85)
        self.ui.table_parts.sortByColumn(3, Qt.SortOrder(0))
        self.ui.table_parts.sortByColumn(2, Qt.SortOrder(0))
        self.ui.table_parts.sortByColumn(0, Qt.SortOrder(0))
        self.ui.table_parts.setSortingEnabled(True)
        self.ui.table_accesory.sortByColumn(3, Qt.SortOrder(0))
        self.ui.table_accesory.sortByColumn(2, Qt.SortOrder(0))
        self.ui.table_accesory.sortByColumn(0, Qt.SortOrder(0))
        self.ui.table_accesory.setSortingEnabled(True)

        self.upd_tables_row_heights(dk9=True)
        # else:
        #     self.dk9_login_start_worker()
        self.web_progress_bar(100)
        self.dk9_finish_progress_bar_status()

    def dk9_get_cache_update_signals(self, result_to=None, next_method=None):
        signals = WorkerSignals()
        if result_to:
            signals.result.connect(result_to)
        signals.progress.connect(self.web_progress_bar)
        if next_method:
            signals.finished.connect(next_method)
        else:
            signals.finished.connect(self.dk9_finish_search_worker)
        signals.error.connect(self.error)
        signals.status.connect(self.update_web_status)
        return signals

    def dk9_login_than_cash_update_workers_sequence(self):
        self.dk9_login_start_worker(next_method=self.dk9_cache_updater_start_worker)

    def dk9_cache_updater_start_worker(self):
        self.dk9_cache_handler_worker = Worker()
        signals = self.dk9_get_cache_update_signals()
        self.dk9_cache_handler_worker.add_task(DK9.CACHE.cache_search_parse_save_handler, signals, 2)
        print('Starting cache handler thread')
        self.thread.start(self.dk9_cache_handler_worker, priority=QtCore.QThread.Priority.HighestPriority)

    # def dk9_update_cache_start_worker(self):
    #     self.request_worker = Worker()
    #     signals = self.dk9_get_cache_update_signals(result_to=self.dk9_parse_and_start_saving)
    #     self.request_worker.add_task(DK9.adv_search, signals, 2, '', '', '', '')  # Empty request to get all
    #     print('Starting thread to search for dk9 cache')
    #     self.thread.start(self.request_worker, priority=QtCore.QThread.Priority.HighestPriority)

    def dk9_read_cache_start_worker(self):
        self.file_io_worker = Worker()
        signals = self.dk9_get_cache_update_signals(next_method=self.dk9_finish_progress_bar_status)
        self.file_io_worker.add_task(DK9.CACHE.read_cache_file, signals, 1)
        print('Starting thread to read dk9 cache')
        self.thread.start(self.file_io_worker, priority=QtCore.QThread.Priority.HighestPriority)

    # def dk9_write_cache_start_worker(self):
    #     self.file_io_worker = Worker()
    #     signals = self.dk9_get_cache_update_signals()
    #     self.file_io_worker.add_task(DK9.CACHE.write_cache_file, signals, 1)
    #     print('Starting thread to write dk9 cache')
    #     self.thread.start(self.file_io_worker, priority=QtCore.QThread.Priority.HighestPriority)

    # def dk9_parse_and_start_saving(self, soups):
    #     print(f'dk9_parse_and_start_saving. soups exist? {not not soups}')
    #     # self.dk9_restart_caching_schedule()
    #     if not soups:
    #         return
    #     self.dk9_parse_soups_to_dict(soups)
    #     self.dk9_write_cache_start_worker()

    def dk9_read_cache_if_exist(self):
        print(f'dk9_read_cache_if_exist')
        if not DK9.CACHE.cache and C.DK9_CACHING and self.web_status in (DK9.STATUS.NO_CONN,
                                                                         DK9.STATUS.CLI_ERR,
                                                                         DK9.STATUS.SERV_ERR,
                                                                         DK9.STATUS.CONN_ERROR):
            if os.path.exists(DK9_CACHE_FILE_PATH):
                self.dk9_read_cache_start_worker()

    def dk9_fill_one_table_from_dict(self, rows: list, table, tab_num: int, tab_names: tuple,
                                     def_bg_color1: tuple, def_bg_color2: tuple,
                                     count_column: int = None, align: dict = None):
        try:
            item_counter = 0
            r = 0
            zebra_colors = (def_bg_color1, def_bg_color2)
            current_zebra_color = 0
            dbgc = zebra_colors[current_zebra_color]
            first_cell_previous_text = ''
            self.clear_table(table)
            if count_column is not None:
                self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                         num=tab_num, tab_names=tab_names, count_1=0, count_2=0)
            for row in rows:
                row_palette = row[0]
                r = 0
                c = 0
                if C.FILTER_SEARCH_RESULT:
                    # print(f'{self.curr_model=}{row[2].string.lower()=}{row[3].string.lower()=}')
                    # Filter models different more than 1 symbol
                    curr_model_len = len(self.curr_model)
                    model_cell = row[3].string.lower()
                    model_cell_len = len(model_cell)
                    description_cell = row[4].string.lower()
                    description_cell_len = len(description_cell)
                    model_idx_in_desc = description_cell.find(self.curr_model)
                    # print(f'{description_cell=} {description_cell[model_idx_in_desc + curr_model_len]=} ')
                    if self.curr_model not in model_cell \
                            or model_cell_len > curr_model_len + 1 \
                            or 4 > model_cell_len > curr_model_len:
                        if model_idx_in_desc == -1:
                            continue
                        if model_idx_in_desc > 0 and description_cell[model_idx_in_desc - 1].isalpha():
                            continue
                        if model_idx_in_desc + curr_model_len < description_cell_len - 1:
                            _right_symbol = description_cell[model_idx_in_desc + curr_model_len]
                            if _right_symbol not in ' /,.)':
                                continue
                amount = row[count_column]
                if count_column is not None and amount.isdigit():
                    item_counter += int(amount)

                table.insertRow(r)
                for cell_value in row[1:]:
                    cell_bg_color = None
                    # print(f'{dk9_td.string} {self.curr_model=}')
                    if isinstance(cell_value, (list, tuple)):
                        cell_text = cell_value[0]
                        cell_bg_color = cell_value[1]
                    else:
                        cell_text = cell_value
                    table.setItem(r, c, QTableWidgetItem(cell_text))
                    table.item(r, c).setToolTip(cell_text)
                    if align and c in align:
                        table.item(r, c).setTextAlignment(align[c])
                    if 'ориг' in cell_text and 'вк ' not in cell_text:
                        table.item(r, c).setFont(self.tab_font_bold)
                    if C.DK9_COLORED:
                        if row_palette:
                            table.item(r, c).setBackground(QtGui.QColor(
                                row_palette[0], row_palette[1], row_palette[2]
                            ))
                        elif cell_bg_color:
                            table.item(r, c).setBackground(QtGui.QColor(
                                cell_bg_color[0], cell_bg_color[1], cell_bg_color[2]
                            ))
                        else:
                            if c == 0:
                                _text = cell_text.lower()
                                if _text != first_cell_previous_text:
                                    first_cell_previous_text = _text
                                    current_zebra_color = abs(current_zebra_color - 1)
                                    dbgc = zebra_colors[current_zebra_color]

                            # dbgc = def_bg_color1 if r % 2 else def_bg_color2
                            table.item(r, c).setBackground(QtGui.QColor(dbgc[0], dbgc[1], dbgc[2]))
                    c += 1
                r += 1
            if count_column is not None:
                self._update_dk9_tooltip(tab_widget=self.ui.tab_widget,
                                         num=tab_num, tab_names=tab_names, count_1=r - 1, count_2=item_counter)
        except Exception as _err:
            self.error((f'Error updating table:\n'
                        f'{table}',
                        f'{traceback.format_exc()}'))

    def dk9_fill_table_from_soup(self, soup, table, num: int, tab_names: tuple,
                                 def_bg_color1: tuple, def_bg_color2: tuple,
                                 count_column: int = None, align: dict = None):
        try:
            item_counter = 0
            r = 0
            zebra_colors = (def_bg_color1, def_bg_color2)
            current_zebra_color = 0
            dbgc = zebra_colors[current_zebra_color]
            first_cell_previous_text = ''
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
                                or model_cell_len > curr_model_len + 1 \
                                or 4 > model_cell_len > curr_model_len:
                            if model_idx_in_desc == -1:
                                continue
                            if model_idx_in_desc > 0 and description_cell[model_idx_in_desc - 1].isalpha():
                                continue
                            if model_idx_in_desc + curr_model_len < description_cell_len - 1:
                                _right_symbol = description_cell[model_idx_in_desc + curr_model_len]
                                if _right_symbol not in ' /,.)':
                                    continue
                        # elif model_cell_len > curr_model_len + 1:
                        #     continue

                        # if self.curr_model not in model_cell \
                        #         or (4 > model_cell_len > curr_model_len) \
                        #         or curr_model_len + 1 < model_cell_len:
                        #     if model_idx_in_desc == -1 \
                        #             or (model_idx_in_desc > 0
                        #                 and description_cell[model_idx_in_desc - 1].isalpha()) \
                        #             or (model_idx_in_desc + curr_model_len < description_cell_len - 1
                        #                 and (description_cell[model_idx_in_desc + curr_model_len] not in '/,.')):
                        #         continue
                    amt = row[count_column].string
                    if count_column is not None and amt.isdigit():
                        item_counter += int(amt)

                    table.insertRow(r)
                    for dk9_td in row:
                        # print(f'{dk9_td.string} {self.curr_model=}')
                        current_cell_text = dk9_td.string
                        table.setItem(r, c, QTableWidgetItem(current_cell_text))
                        table.item(r, c).setToolTip(current_cell_text)
                        if align and c in align:
                            table.item(r, c).setTextAlignment(align[c])
                        if 'ориг' in current_cell_text and 'вк ' not in current_cell_text:
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
                                if c == 0:
                                    _text = current_cell_text.lower()
                                    if _text != first_cell_previous_text:
                                        first_cell_previous_text = _text
                                        current_zebra_color = abs(current_zebra_color - 1)
                                        dbgc = zebra_colors[current_zebra_color]

                                # dbgc = def_bg_color1 if r % 2 else def_bg_color2
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

    def dk9_finish_search_worker(self):
        if self.web_status == DK9.STATUS.SERV_ERR:
            self.dk9_upd_cache_restart_timer(allow_update=False)
        if not DK9.LOGIN_SUCCESS:
            if not self.got_login_on_search_try_relog:
                self.got_login_on_search_try_relog = True
                self.dk9_login_start_worker(self.dk9_upd_cache_restart_timer)
                return
            else:
                self.got_login_on_search_try_relog = False
                # self.ui.web_status.setToolTip(f'Can`t relogin to DK9')
                self.dk9_upd_cache_restart_timer(allow_update=False)
            if self.web_status == DK9.STATUS.LOGIN_FAIL:
                self.dk9_upd_cache_stop_timer()
        self.dk9_finish_progress_bar_status()

    def dk9_finish_progress_bar_status(self):
        print(f'dk9_finish_progress_bar_status {self.web_status=}')

        if self.web_status in (DK9.STATUS.UPDATING, DK9.STATUS.OK, DK9.STATUS.FILE_UPDATED):
            # if self.web_status in (DK9.STATUS.CONNECTING, DK9.STATUS.OK):
            if self.web_status != DK9.STATUS.FILE_UPDATED:
                if C.DK9_CACHING and DK9.CACHE.cache:
                    self.update_web_status(DK9.STATUS.FILE_UPDATED)
                else:
                    self.update_web_status(DK9.STATUS.OK)
            if self.web_status == DK9.STATUS.FILE_UPDATED:
                self.ui.web_status.setToolTip(f'Using file: '
                                              f'{DK9_CACHE_FILE_PATH}')
            self.update_web_progress_bar(progress=0)

        elif C.DK9_CACHING or self.web_status == DK9.STATUS.FILE_USED_OFFLINE:
            if DK9.CACHE.cache:
                cache_day = int(DK9.CACHE.cache['updated'].split(' ')[1][0:2])
                current_day = datetime.now().day
                if cache_day == current_day:
                    self.update_web_progress_bar(progress=100, style_sheet=C.PB_STYLE_SHEET_WARN)
                else:
                    self.update_web_progress_bar(progress=100, style_sheet=C.PB_STYLE_SHEET_ERROR)
                if self.web_status == DK9.STATUS.LOGIN_FAIL:
                    self.ui.web_status.setToolTip(C.WEB_STATUSES[DK9.STATUS.LOGIN_FAIL])
                elif self.web_status not in (DK9.STATUS.CLI_ERR, DK9.STATUS.SERV_ERR, DK9.STATUS.NO_LOGIN):
                    self.ui.web_status.setToolTip(f'Loaded from file: {DK9_CACHE_FILE_PATH}\n'
                                                  f'{C.WEB_STATUSES[self.web_status]}')
                self.update_web_status(DK9.STATUS.FILE_USED_OFFLINE)
            else:
                self.update_web_progress_bar(progress=100, style_sheet=C.PB_STYLE_SHEET_ERROR)
        else:
            self.update_web_progress_bar(progress=100, style_sheet=C.PB_STYLE_SHEET_ERROR)

    def web_progress_bar(self, progress):
        if self.web_status == DK9.STATUS.FILE_READ:
            self.update_web_progress_bar(progress=progress, style_sheet=C.PB_STYLE_SHEET_FILE_READ)
        elif self.web_status == DK9.STATUS.FILE_WRITE:
            self.update_web_progress_bar(progress=progress, style_sheet=C.PB_STYLE_SHEET_FILE_WRITE)
        else:
            self.update_web_progress_bar(progress=progress, style_sheet=C.PB_STYLE_SHEET_DEFAULT)

    def dummy(self):
        pass

    def clear_table(self, table):
        self.copied_table_items = {}
        table.clearContents()
        table.setRowCount(0)

    # @staticmethod
    # def get_color_from_style(style):
    #     return C.DK9_BG_COLORS[style[style.find(':') + 1: style.find(';')]]

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
                            L.table_price_Item_not_found % recursive_model
                        ))
                        self.ui.table_price.item(0, 0).setFont(self.tab_font_bold)
                        return
            else:
                _models_of_manufacturer = self.models[self.curr_manufacturer]
                _model = model

            # print(f'{_models_of_manufacturer=}')
            # print(f'{_model=}')

            if _model in _models_of_manufacturer:
                # print(f'FOUND')
                # print(f'{_models_of_manufacturer=}')
                sheet, row_num, _ = _models_of_manufacturer[_model]  # [Sheet 27:<XIAOMI>, 813] - sheet, row

                # Take needed columns for exact model

                row = sheet.row_values(row_num, 0, MAX_PRICE_COLUMNS)
                row_len = len(row)
                new_row_num = 0
                # print(f'{row_len=} {row=}')
                # print(f'{cells_texts=}')
                columns_for_price_table = [
                    PriceColumns.work_type,
                    PriceColumns.price,
                    PriceColumns.compatible_part,
                    PriceColumns.note,
                ]

                # Add MODEL NAME row to the first table row
                if True:  # if model row must be shown in price table
                    cells_texts = [row[PriceColumns.model],
                                   row[PriceColumns.compatible_model]]
                    # print(f'{row=} {columns=} {cells_texts=} ')
                    self._add_price_table_row(table=self.ui.table_price, sheet=sheet,
                                              columns=[
                                                    PriceColumns.model,
                                                    PriceColumns.note,
                                              ],
                                              cells_texts=cells_texts,
                                              t_row_num=new_row_num, p_row_num=row_num,
                                              align={1: Qt.AlignRight | Qt.AlignVCenter},
                                              colored=C.PRICE_COLORED, bold=True)
                    new_row_num += 1

                # Add other PRICE rows to the table
                for i in range(row_num, sheet.nrows - 1):
                    # row = Price.get_row_in_pos(sheet=sheet, row_num=row_num)
                    print(f'{row=} {row_len=} {i=}')
                    if row_len < PriceColumns.note:  # If row shorter, than we expect, then place all row in 0 column
                        print('SHORT row:' + str(row))
                        cell_text = self.list_to_string(row)
                        self.ui.table_price.insertRow(new_row_num)
                        self.ui.table_price.setItem(new_row_num, 0, QTableWidgetItem(cell_text))
                        self.ui.table_price.item(new_row_num, 0).setToolTip(cell_text)
                        return
                    else:
                        # if cell is out of row, text will be empty
                        cells_texts = []
                        for column_num in columns_for_price_table:
                            if column_num < row_len:
                                cells_texts.append(row[column_num])
                            else:
                                cells_texts.append('')
                        print(f"{cells_texts=}")
                        if cells_texts[0]:  # or len(cells_texts[1]) > 3:
                            self._add_price_table_row(table=self.ui.table_price, sheet=sheet,
                                                      columns=columns_for_price_table, cells_texts=cells_texts,
                                                      t_row_num=new_row_num, p_row_num=i,
                                                      align={1: Qt.AlignRight | Qt.AlignVCenter},
                                                      colored=C.PRICE_COLORED)

                            new_row_num += 1
                        if i < sheet.nrows:
                            row = sheet.row_values(i + 1, 0, MAX_PRICE_COLUMNS)
                            if row[0] != '':
                                if row[0] not in C.PRICE_TRASH_IN_CELLS:
                                    return
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
            # print(f'{c=} {txt=}')
            if not isinstance(txt, str):
                if isinstance(txt, float):
                    txt = str(int(txt))
                else:
                    txt = ''  # str(txt)
            table.setItem(t_row_num, c, QTableWidgetItem(txt))
            table.item(t_row_num, c).setToolTip(txt)
            if align and c in align:
                table.item(t_row_num, c).setTextAlignment(align[c])
                # table.item(t_row_num, c).setTextAlignment(Qt.AlignVCenter)
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

    def price_read_finished(self, progress=None):
        if progress:
            self.update_price_progress_bar(progress=progress, style_sheet=C.PB_STYLE_SHEET_DEFAULT)
        else:
            if self.price_status == 6:
                self.update_price_progress_bar(progress=0)
                if self.web_status in (
                        DK9.STATUS.NO_CONN,
                        DK9.STATUS.CLI_ERR,
                        DK9.STATUS.SERV_ERR,
                        DK9.STATUS.CONN_ERROR,
                ):
                    self.dk9_login_or_update_cache_on_start()
            else:
                self.update_price_progress_bar(progress=100, style_sheet=C.PB_STYLE_SHEET_ERROR)

    def update_web_progress_bar(self, progress: int = 0, style_sheet: str = None):
        self.ui.web_progress_bar.setValue(progress)
        if style_sheet is not None:
            self.ui.price_progress_bar.setStyleSheet(style_sheet)

    def update_price_progress_bar(self, progress: int = 0, style_sheet: str = None):
        self.ui.price_progress_bar.setValue(progress)
        if style_sheet is not None:
            self.ui.price_progress_bar.setStyleSheet(style_sheet)

    @staticmethod
    def _update_dk9_tooltip(tab_widget, num: int, tab_names: tuple, count_1: int, count_2: int):
        # tab_widget.setTabText(num, f'{tab_names[num]}{count_1} / {count_2} ')
        tab_widget.setTabText(num, L.tab_widget_left_TabText % (tab_names[num], count_2))
        tab_widget.setTabToolTip(num, L.tab_widget_left_TabToolTip % (count_1, count_2))

    def update_work_cost(self):
        if self.selected_work_price == 0 or self.selected_part_price == 0:
            # or self.selected_work_price < self.selected_part_price:
            self.work_cost_label.setText('')
        else:
            self.work_cost_label.setText(
                L.work_cost_label_Text %
                (int(self.selected_work_price - self.selected_part_price * (1 + C.INCOME_PARTS_MARGIN_PERC / 100)),
                 int(self.selected_work_price - self.selected_part_price)))

    # WEB TABLE SELECTION
    def handle_web_table_item_selection_connected(self):
        self.change_table_item_bg_color_on_selection(table=self.sender())
        self.update_work_cost()

    # def change_table_item_colors(self, table: QtCore.QObject, items: int = 0):
    def change_table_item_bg_color_on_selection(self, table: QTableWidget):
        row = table.selectedItems()
        if row:
            _cost = row[4].text()
            self.selected_part_price = (int(_cost) if _cost.isdigit() else 0)
            if C.DK9_COLORED:
                last_cell_bg_color = (row[-1].background().color().red(),
                                      row[-1].background().color().green(),
                                      row[-1].background().color().blue())
            else:
                last_cell_bg_color = (200, 200, 200)
            # print(f'{row=} {last_cell_bg_color=}')
            # print(f"{self.web_table_stylesheet_template[0]}"
            #       f"{last_cell_bg_color}"
            #       f"{self.web_table_stylesheet_template[1]}")
            table.setStyleSheet(f"{self.web_table_stylesheet_template[0]}"
                                f"{last_cell_bg_color}"
                                f"{self.web_table_stylesheet_template[1]}")
        else:
            self.selected_part_price = 0

    # TABLE COPY
    def copy_web_table_items_connected(self):
        self.copy_table_items(table=self.sender(), items=4)

    def copy_price_table_item_connected(self):
        self.copy_table_items(table=self.sender(), items=1)

    def copy_table_items(self, table, items: int = 0):
        row = table.selectedItems()
        # print(f'{row=}')
        self.clear_table_items_on_new_copy()
        self.copied_table_items[table] = []
        texts = []
        for i in range(items if items else len(row)):
            texts.append(row[i].text())
            self.copied_table_items[table].append(row[i])
            if table is not self.ui.table_price and 'ориг' in row[i].text() and 'вк ' not in row[i].text():
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
                if table != self.ui.table_price and 'ориг' in item.text() and 'вк ' not in item.text():
                    item.setFont(self.tab_font_bold)
                else:
                    item.setFont(self.tab_font)
            del table

    def handle_price_table_item_selection_connected(self):
        # copy to cash
        selected_row = self.sender().selectedItems()
        selected_row_len = len(selected_row)
        self.ui.le_cash_name.setText(selected_row[0].text() if selected_row_len > 0 else '')
        _price = selected_row[1].text() if selected_row_len > 1 else ''
        self.ui.le_cash_price.setText(_price)
        self.ui.le_cash_descr.setText(selected_row[2].text() if selected_row_len > 2 else '')
        self.selected_work_price = (int(_price) if _price.isdigit() else 0)
        if selected_row:
            self.highlight_web_parts_by_part_name(selected_row[0].text())
        self.update_work_cost()
        # clipboard.setText(text)

    def highlight_web_parts_by_part_name(self, name: str):
        if not name:
            return
        founded_cell_first_letters = {}
        founded_cell_appropriation = {}
        # _exact_price_words = list(map(str.strip, re.split(r'[ \-+()]', name.lower(), maxsplit=7)))
        _exact_price_words = re.split(r'[ \-+()]', name.lower(), maxsplit=7)
        # print(f'{_exact_price_words=}')
        if len(_exact_price_words) == 1:
            _exact_price_words.append('')
        vk = True if 'вк' in _exact_price_words else False
        orig = True if 'ориг' in _exact_price_words else False
        _exact_first_word_len = len(_exact_price_words[0])
        _exact_price_words_len = len(_exact_price_words)
        _first_search_letters = _exact_price_words[0][:4] if _exact_first_word_len >= 4 else _exact_price_words[0]
        _found_exact_len = 0
        _found_big = False

        # Prepare table data
        for row_num in range(self.ui.table_parts.rowCount()):
            _cells = (*(self.ui.table_parts.item(row_num, i) for i in range(5)),)
            # _cell_0_lst = \
            #     list(map(str.strip, re.split(r'[ \-+()]',
            #                                  self.ui.table_parts.item(row_num, 0).text().lower(), maxsplit=5)))
            _cell_0_lst = re.split(r'[ \-+()]', self.ui.table_parts.item(row_num, 0).text().lower(), maxsplit=5)
            _cell_3_lst = re.split(r'[ \-+()]', self.ui.table_parts.item(row_num, 3).text().lower(), maxsplit=5)

            self._upd_bg_clr_sel_by_price(_cells, 0, 4, True)

            # Search for first 4 letters
            if _cell_0_lst[0].startswith(_first_search_letters):
                if len(_cell_0_lst) > 1 and _exact_price_words[1] in ('вк', 'ориг') \
                        and 'экран' not in _cell_0_lst:
                    continue

                vk_part = True if 'вк' in _cell_0_lst \
                                  or 'вк' in _cell_3_lst else False
                orig_part = True if 'ориг' in _cell_0_lst \
                                    or 'ориг' in _cell_3_lst \
                                    or 'ор' in _cell_3_lst else False
                vk_orig_part = True if vk_part and orig_part else False

                if orig and not vk and vk_part:
                    continue
                elif vk and not orig and orig_part and not vk_part:
                    continue
                elif vk and orig and not vk_orig_part:
                    continue
                # print(f'{_exact_price_words=} {_cell_0_lst=} {_cell_3_lst=} {row_num=}')

                _appropriation_of_part_row = 0

                for _price_word in _exact_price_words:
                    if _price_word not in ('', 'вк', 'ориг') \
                            and (_price_word in _cell_0_lst or _price_word in _cell_3_lst):
                        _appropriation_of_part_row += 1

                if _appropriation_of_part_row not in founded_cell_appropriation:
                    founded_cell_appropriation[_appropriation_of_part_row] = []
                founded_cell_appropriation[_appropriation_of_part_row].append(row_num)

                founded_cell_first_letters[row_num] = {
                    # 'len': _cell_0_len,
                    'text0': _cell_0_lst,
                    'text3': _cell_3_lst,
                    'cells': _cells
                }
        # print(f'{founded_cell_first_letters=}')
        # print(f'{founded_cell_appropriation=}')
        # Search for second word
        if founded_cell_first_letters:
            _max_appropriated_row = max(founded_cell_appropriation.keys())
            for row_num in founded_cell_appropriation[max(founded_cell_appropriation.keys())]:
                for _price_word_num in range(_exact_price_words_len):
                    if not _price_word_num or (_exact_price_words[_price_word_num] in ('', 'вк', 'ориг', 'с')):
                        continue
                    if _exact_price_words[_price_word_num] in founded_cell_first_letters[row_num]['text0'] \
                            or _exact_price_words[_price_word_num] in founded_cell_first_letters[row_num]['text3']:
                        self._upd_bg_clr_sel_by_price(founded_cell_first_letters[row_num]['cells'], 0, 4)
                        _found_big = True
                        break
            if _found_big:
                return
            for row_num, _cell_params in founded_cell_first_letters.items():
                self._upd_bg_clr_sel_by_price(founded_cell_first_letters[row_num]['cells'], 0, 4)

    # Highlighting parts that most fit to selected price position
    def _upd_bg_clr_sel_by_price(self, cells_to_change: tuple, first_cell: int, to_cell: int, default: bool = False):
        if C.DK9_COLORED:
            default_cell_bg_color = cells_to_change[to_cell].background().color()
        else:
            default_cell_bg_color = QtGui.QColor(250, 250, 250)

        if default:
            if cells_to_change[first_cell].background().color() != default_cell_bg_color:
                for column in range(first_cell, to_cell):
                    cells_to_change[column].setBackground(default_cell_bg_color)
            return
        for column in range(first_cell, to_cell):
            if column < to_cell - 1:
                cells_to_change[column].setBackground(self.DK9_BG_COLOR_SEL_BY_PRICE)
            else:
                self.DK9_BG_COLOR_SEL_BY_PRICE_GRAD.setColorAt(1, QtGui.QColor(default_cell_bg_color))
                cells_to_change[column].setBackground(self.DK9_BG_COLOR_SEL_BY_PRICE_GRAD)

        # color2.setColorAt(1, QtGui.QColor(second_cell_bg_color))

        # cell_to_change2.setBackground(color2)
        # for column in range(start, start + amt):
        #     cells_params[column].setForeground(color)
        #     cells_params[column].setFont(font)

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
            if source in (
                    self.ui.table_parts,
                    self.ui.table_accesory,
                    self.ui.table_price,
            ):
                # print(f'{source=}')
                row = source.selectedItems()
                # print(f'{row=}')
                if row:
                    # user = str(row[0].data())
                    contextMenu = QMenu(self)
                    copy_for_order = contextMenu.addAction(L.copy_for_order_contextMenu)
                    copy_full_row = contextMenu.addAction(L.copy_full_row_contextMenu)
                    action = contextMenu.exec_(event.globalPos())
                    if action == copy_for_order:
                        if source is self.ui.table_price:
                            self.copy_table_items(source, 1)
                        else:
                            self.copy_table_items(source, 4)
                    if action == copy_full_row:
                        self.copy_table_items(source)
        elif event.type() == QEvent.MouseButtonDblClick:
            if source in (self.ui.le_cash_name, self.ui.le_cash_descr, self.ui.le_cash_price):
                clipboard.setText(source.text())
        return super().eventFilter(source, event)

    def open_adv_search(self):
        adv_search_ui = AdvancedSearchWindow(self)
        adv_search_ui.setWindowIcon(QtGui.QIcon(LOGO))
        L.translate_AdvSearchDialog_texts(adv_search_ui)
        adv_search_ui.exec_()
        adv_search_ui.show()

    def open_settings(self):
        settings_ui = ConfigWindow(C, self, DK9, L)
        settings_ui.setWindowIcon(QtGui.QIcon(LOGO))
        L.translate_ConfigWindow_texts(settings_ui)
        settings_ui.exec_()
        settings_ui.show()

    def open_first_start(self):
        first_start_ui = FirstStartWindow(C, self, DK9, L)
        first_start_ui.setWindowIcon(QtGui.QIcon(LOGO))
        L.translate_StartWindow_texts(first_start_ui)
        first_start_ui.exec_()
        first_start_ui.show()

    def open_help(self):
        help_ui = HelpWindow(C, self)
        help_ui.setWindowIcon(QtGui.QIcon(LOGO))
        L.translate_HelpDialog_texts(help_ui)
        help_ui.exec_()
        help_ui.show()

    def open_graphs(self):
        graphs_ui = GraphWindow(C, self, MDAS, L)
        graphs_ui.setWindowIcon(QtGui.QIcon(LOGO))
        L.translate_GraphDialog_texts(graphs_ui)
        graphs_ui.exec_()
        graphs_ui.show()

    @staticmethod
    def error(errors: tuple):
        save_error_file(f'Error: {errors}')
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
        self.setMinimumSize(QtCore.QSize(80, 30))
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
                self.app.filter_item_text_search_visualise(self.app.model_list_widget.currentItem())

            elif event.key() == Qt.Key_Up:
                idx = self.app.model_list_widget.currentRow() - 1
                if idx < 0:
                    idx = len(self.app.models[self.app.curr_manufacturer]) - 1
                # self.app.model_list_widget.setCurrentRow(idx)
                self.app.model_list_widget.setCurrentCell(idx, 0)

            elif event.key() == Qt.Key_Down:
                if self.app.model_list_widget.isHidden():
                    self.app.upd_models_list()
                    return
                idx = self.app.model_list_widget.currentRow() + 1
                if idx > len(self.app.models[self.app.curr_manufacturer]) - 1:
                    idx = 0
                # self.app.model_list_widget.setCurrentRow(idx)
                self.app.model_list_widget.setCurrentCell(idx, 0)

            elif event.key() == Qt.Key_Shift:
                # self.app.model_list_widget.setCurrentRow(idx)
                self.app.model_list_widget.setCurrentCell(
                    self.app.model_list_widget.currentRow(),
                    abs(1 - self.app.model_list_widget.currentColumn()))

        if event.key() == Qt.Key_Right:
            self.app.upd_manufacturer_wheel(increment=1)

        if event.key() == Qt.Key_Left:
            self.app.upd_manufacturer_wheel(increment=-1)


def set_application_style(style):
    app.setStyle(style)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(LOGO))
        clipboard = app.clipboard()
        window = App()
        window.setWindowIcon(QtGui.QIcon(LOGO))
        QtCore.QTimer.singleShot(1, window.on_ui_loaded)
        window.search_input.setFocus()
        sys.exit(app.exec_())
    except Exception as err:
        App.error((f'Global Error',
                   f'{traceback.format_exc()}'))
        save_error_file(f'Global Error: {traceback.format_exc()}')
