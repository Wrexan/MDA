import sys
import bs4
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, \
    QHeaderView, qApp, QMessageBox, QListWidget, QSizePolicy, QLineEdit, QSpacerItem, QPushButton
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt

from MDA_classes.config import Config
from MDA_classes.dk9 import DK9Parser
from MDA_classes.price import Price
from MDA_classes.modal_windows import ConfigWindow, HelpWindow
from MDA_classes.thread_worker import Worker
from MDA_UI.window_main import Ui_MainWindow

C = Config()
DK9 = DK9Parser(C)


class App(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        qApp.focusChanged.connect(self.on_focusChanged)
        self.models = {}
        self.model_buttons = {}
        self.manufacturer_wheel = None
        self.current_model_button_index = 0
        self.ui = Ui_MainWindow()
        # self.ui = MainUI()
        self.ui.setupUi(self)
        self.model_list_widget = QListWidget()

        self.search_input = SearchInput(self)
        self.search_input.setParent(self.ui.frame_3)
        self.ui.search_layout.addWidget(self.search_input)

        self.init_ui_statics()
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
        # self.login_dk9()
        self.update_web_status(0)
        # self.update_price_status()
        self.show()

    def init_ui_statics(self):

        self.resized.connect(self.fix_models_list_position)
        # self.ui.input_search.textChanged[str].connect(self.prepare_and_search)
        # self.ui.input_search.cursorPositionChanged.connect(self.upd_models_list)
        self.search_input.textChanged[str].connect(self.prepare_and_search)
        # self.search_input.cursorPositionChanged.connect(self.upd_models_list)

        self.ui.pb_adv_search.setToolTip(
            'Необходимо для поиска в веб базе в конкретных полях. Актуальность под вопросом')

        self.ui.chb_show_exact.stateChanged.connect(self.upd_dk9_on_rule_change)
        self.ui.chb_show_exact.setToolTip(
            'Вкл - отображает максимально релевантные модели\n'
            'Откл - отображаются похожие модели (Mi8 lite по запросу Mi8)')

        self.ui.chb_price_name_only.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_price_name_only.setToolTip(
            'Вкл - запросом в интернет базу являются производитель и модель из прайса\n'
            'Откл - запросом в интернет базу является текст в строке ввода '
            '(позволяет по запросу 5 найти все модели всех фирм, содержащие 5)')

        self.ui.chb_search_eng.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_eng.setToolTip(
            'Вкл - переводит символы алфавита в латиницу нижнего регистра.')

        self.ui.chb_search_narrow.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_narrow.setToolTip(
            'Вкл - поиск начинается с 2х символов\n'
            'Откл - позволяет найти отдельный символ (например украинскую С или Е)')

        self.ui.settings_button.clicked.connect(self.open_settings)

        self.ui.table_price.setHorizontalHeaderLabels(('Виды работ', 'Цена', 'Прим'))
        self.ui.table_parts.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                       'Цена', 'Шт', 'Дата', 'Где'))
        self.ui.table_accesory.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                          'Цена', 'Шт', 'Дата', 'Где'))

        self.ui.table_parts.doubleClicked.connect(self.copy_web_table_items)
        self.ui.table_accesory.doubleClicked.connect(self.copy_web_table_items)
        self.ui.table_price.clicked.connect(self.cash_table_element)
        self.ui.table_price.doubleClicked.connect(self.copy_price_table_item)
        self.ui.help.clicked.connect(self.open_help)

        self.manufacturer_wheel = (self.ui.manufacturer_1,
                                   self.ui.manufacturer_2,
                                   self.ui.manufacturer_3,
                                   self.ui.manufacturer_4,
                                   self.ui.manufacturer_5)
        # models list appearing on search
        self.model_list_widget.setParent(self)
        self.model_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.model_list_widget.setFixedWidth(self.search_input.width())
        self.model_list_widget.setMinimumSize(20, 20)
        self.model_list_widget.itemClicked.connect(self.scheduler)
        self.model_list_widget.hide()

    def init_ui_dynamics(self):
        font = QtGui.QFont()
        # font.setBold(True)
        font.setPixelSize(C.TABLE_FONT_SIZE)

        if C.FULLSCREEN:
            self.showMaximized()
        else:
            self.showNormal()
        self.ui.table_price.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_parts.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_accesory.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_price.setFont(font)
        self.ui.table_parts.setFont(font)
        self.ui.table_accesory.setFont(font)
        self.ui.pt_cash_name.setFont(font)
        self.ui.pt_cash_descr.setFont(font)
        self.ui.pt_cash_price.setFont(font)

        self.model_list_widget.setFont(font)
        self.fix_models_list_position()

        for i in range(self.ui.table_parts.columnCount()):
            if i == 3:
                self.ui.table_parts.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
                self.ui.table_accesory.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                self.ui.table_parts.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
                self.ui.table_accesory.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        for i in range(self.ui.table_price.columnCount()):
            if i == 2:
                self.ui.table_price.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                self.ui.table_price.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

    # =============================================================================================================

    def fix_models_list_position(self):
        self.model_list_widget.move(int(self.ui.search_widget.x() + 12),
                                    int(self.ui.HEAD.height() - 6))

    def start_search_on_rule_change(self):
        C.SEARCH_BY_PRICE_MODEL = self.ui.chb_price_name_only.checkState()
        C.LATIN_SEARCH = self.ui.chb_search_eng.checkState()
        C.NARROW_SEARCH = self.ui.chb_search_narrow.checkState()
        self.prepare_and_search(self.search_input.text(), True)

    def upd_dk9_on_rule_change(self):
        C.FILTER_SEARCH_RESULT = self.ui.chb_show_exact.checkState()
        if self.soup:
            self.update_dk9_data(use_old_soup=True)

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
                self.upd_manufacturer_wheel(hide_list=force_search)
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
            if self.curr_manufacturer_idx + 2 >= m >= self.curr_manufacturer_idx - 2:
                self.manufacturer_wheel[m - self.curr_manufacturer_idx + 2].setText(manufacturer)
                if m == self.curr_manufacturer_idx:
                    self.curr_manufacturer = manufacturer
                    self.upd_models_list(hide_list=hide_list)

    def upd_models_list(self, clear: bool = False, hide_list: bool = False):
        if clear or not self.models:
            self.curr_manufacturer_idx = 0
            self.model_list_widget.clear()
            self.model_list_widget.hide()
            return

        curr_models = [
            f'{model}{self.recursor}{params[2]}' if isinstance(params[2], str) and 'см' in params[2] else model
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

        models_str = text_lower. \
            replace(self.curr_manufacturer.lower(), ''). \
            replace('телефон', ''). \
            replace('планшет', ''). \
            replace('с', 'c'). \
            replace('е', 'e')
        recursive_model_idx = models_str.find('см')
        recursive_model = ''
        if recursive_model_idx >= 0:
            recursive_model = models_str[recursive_model_idx + 2:].strip()
            models_str = models_str[:recursive_model_idx].replace(self.recursor, '')
        models_for_buttons = [m.strip() for m in models_str.split(',', 4)]

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
        self.update_price_table(text_lower)

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

    def search_dk9(self):
        if not DK9.LOGIN_SUCCESS:
            return
        manufacturer = '' if not C.SEARCH_BY_PRICE_MODEL else self.curr_manufacturer
        if self.search_again:
            print(f'SEARCH AGAIN: {self.curr_model}')
            self.search_again = False
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
            self.fill_table_from_soup(self.soup[0], self.ui.table_parts, C.DK9_BG_P_COLOR1, C.DK9_BG_P_COLOR2)
            self.load_progress(85)
            self.fill_table_from_soup(self.soup[1], self.ui.table_accesory, C.DK9_BG_A_COLOR1, C.DK9_BG_A_COLOR2)
        else:
            self.login_dk9()
        self.load_progress(0) if use_old_soup else self.load_progress(100)

    def dummy(self):
        pass

    def update_price_table(self, model):  # 'xiaomi mi a2 m1804d2sg'
        try:
            # print(f'{model=}\n{self.models=}\n{self.curr_model_idx=}\n'
            #       f'{self.curr_manufacturer=}\n{self.curr_manufacturer_idx=}')
            if model in self.models[self.curr_manufacturer]:
                # print(f'FOUND')
                position = self.models[self.curr_manufacturer][model]  # [Sheet 27:<XIAOMI>, 813] - sheet, row
                # print(f'{position=}')
                # Take needed columns for exact model
                if position[0].name in C.PRICE_SEARCH_COLUMN_NUMBERS:
                    columns = C.PRICE_SEARCH_COLUMN_NUMBERS[position[0].name]  # [2, 4, 5]
                else:
                    columns = C.PRICE_SEARCH_COLUMN_NUMBERS['+']
                row = Price.get_row_in_pos(position)
                row_len = len(row)
                # print(f'{row=}')

                new_row_num = 0
                self.ui.table_price.setRowCount(0)
                for i in range(position[1], position[0].nrows - 1):
                    # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
                    if row_len < columns[-1]:  # If row shorter, than we expect, then place all row in 0 column
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
                                cells_texts.append(str(row[columns[c]]))
                            else:
                                cells_texts.append('')

                        if cells_texts[0]:  # or len(cells_texts[1]) > 3:

                            self.ui.table_price.insertRow(new_row_num)
                            for j, txt in enumerate(cells_texts):
                                self.ui.table_price.setItem(new_row_num, j, QTableWidgetItem(txt))
                                self.ui.table_price.item(new_row_num, j).setToolTip(txt)

                                if C.PRICE_COLORED and txt:
                                    bgd = self.Price.DB.colour_map. \
                                        get(self.Price.DB.xf_list[position[0].
                                            cell(i, columns[j]).xf_index].background.pattern_colour_index)
                                    if bgd:
                                        self.ui.table_price.item(new_row_num, j). \
                                            setBackground(QtGui.QColor(bgd[0], bgd[1], bgd[2]))

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

    def load_progress(self, progress):
        self.ui.web_load_progress_bar.setValue(progress)

    def finished(self):
        if self.web_status not in (1, 2):
            self.ui.web_load_progress_bar.setValue(100)
        else:
            self.ui.web_load_progress_bar.setValue(0)

    def fill_table_from_soup(self, soup, table, def_bg_color1, def_bg_color2):
        try:
            r = 0
            table.setRowCount(0)
            if not soup:
                return
            for dk9_row in soup.tr.next_siblings:
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
                        if self.curr_model not in row[2].string.lower() \
                                or len(self.curr_model) + 1 < len(row[2].string.lower()):
                            if self.curr_model not in row[3].string.lower():
                                continue
                    table.insertRow(r)
                    for dk9_td in row:
                        # print(f'{dk9_td.string} {self.curr_model=}')
                        table.setItem(r, c, QTableWidgetItem(dk9_td.string))
                        table.item(r, c).setToolTip(dk9_td.string)
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
        except Exception as _err:
            self.error((f'Error updating table:\n'
                        f'{table}',
                        f'{traceback.format_exc()}'))

    def copy_web_table_items(self):
        font = QtGui.QFont()
        font.setUnderline(True)
        selected_row = self.sender().selectedItems()
        text = ''
        for i in range(4):
            text = f'{text} {selected_row[i].text()} '
            # selected_row[i].setSelected(False)
            selected_row[i].setFont(font)
        clipboard.setText(text)

    def copy_price_table_item(self):
        font = QtGui.QFont()
        font.setUnderline(True)
        selected_row = self.sender().selectedItems()
        selected_row[0].setFont(font)
        clipboard.setText(selected_row[0].text())

    def cash_table_element(self):
        selected_row = self.sender().selectedItems()
        self.ui.pt_cash_name.setPlainText(selected_row[0].text())
        self.ui.pt_cash_descr.setPlainText(selected_row[2].text())
        self.ui.pt_cash_price.setPlainText(selected_row[1].text())
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

        self.search_input.setFocus()
        self.search_input.selectAll()

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
        self.setMinimumSize(QtCore.QSize(520, 30))
        self.setMaximumSize(QtCore.QSize(520, 30))
        self.setBaseSize(QtCore.QSize(520, 30))

        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(17)
        self.setFont(font)
        self.setMaxLength(32)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("search_input")

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
