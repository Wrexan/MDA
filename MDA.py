import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, \
    QHeaderView, qApp, QDialog, QMessageBox, QListWidget, QSizePolicy
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt

from MDA_classes.config import Config
from MDA_classes.dk9 import DK9Parser
from MDA_classes.price import Price
from MDA_classes.thread_worker import Worker, WorkerSignals
from MDA_UI.window_main import Ui_MainWindow
from MDA_UI.window_settings import Ui_settings_window
from MDA_UI.window_simple import Ui_Dialog


# class Conf(Config):
#     def __init__(self):
#         super(Conf, self).__init__()
#         self.error = QtCore.pyqtSignal(tuple)


C = Config()
DK9 = DK9Parser(C.DK9_LOGIN_URL, C.DK9_SEARCH_URL, C.DK9_HEADERS, C.data())


class App(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        qApp.focusChanged.connect(self.on_focusChanged)
        self.latin_process = False
        self.models = {}
        self.model_buttons = {}
        self.current_model_button_index = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model_list_widget = QListWidget()
        self.init_ui_statics()
        self.init_ui_dynamics()

        self.curr_type = ''
        self.curr_firm = ''
        self.curr_model = ''
        self.curr_description = ''

        self.search_again = False
        self.old_search = ''
        self.thread = QtCore.QThread
        self.worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        print('Loading Price')
        self.Price = None
        # self.Price = Price(C)
        print('Login to DK9')
        self.web_status = 0
        self.login_dk9()
        self.update_price_status()

    def init_ui_statics(self):

        self.resized.connect(self.fix_models_list_position)
        self.ui.input_search.textChanged[str].connect(self.prepare_and_search)
        self.ui.input_search.cursorPositionChanged.connect(self.upd_models_list)

        self.ui.chb_search_narrow.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_narrow.setToolTip('Вкл - поиск начинается с 2х символов\n'
                                             'Откл - позволяет найти отдельный символ (например украинскую С или Е)')

        self.ui.chb_search_smart.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_smart.setToolTip(
            'Вкл - запрос считается началом слова\n'
            'Откл - запрос ищется везде (позволяет найти A526 по запросу 52)')

        self.ui.chb_search_eng.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_search_eng.setToolTip('Вкл - Переводит символы алфавита в латиницу нижнего регистра.')

        self.ui.chb_price_name_only.stateChanged.connect(self.start_search_on_rule_change)
        self.ui.chb_price_name_only.setToolTip(
            'Вкл - запросом в интернет базу являются производитель и модель из прайса\n'
            'Откл - запросом в интернет базу является текст в строке ввода '
            '(позволяет по запросу 5 найти все модели всех фирм, содержащие 5)')

        self.ui.settings_button.clicked.connect(self.open_settings)

        self.ui.table_price.setHorizontalHeaderLabels(('Виды работ', 'Цена', 'Прим'))
        self.ui.table_parts.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                       'Цена', 'Шт', 'Дата', 'Где'))
        self.ui.table_accesory.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                          'Цена', 'Шт', 'Дата', 'Где'))

        self.ui.table_parts.doubleClicked.connect(self.copy_table_item)
        self.ui.table_accesory.doubleClicked.connect(self.copy_table_item)
        self.ui.table_price.clicked.connect(self.cash_table_element)
        self.ui.help.clicked.connect(self.open_help)
        # models list appearing on search
        self.model_list_widget.setParent(self)
        self.model_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.model_list_widget.setFixedWidth(self.ui.input_search.width())
        # self.model_list_widget.itemSelectionChanged.connect(self.scheduler)
        self.model_list_widget.itemClicked.connect(self.scheduler)
        self.model_list_widget.hide()

        # self.model_list_widget.setBaseSize(self.ui.input_search.width(), 26 * 10)

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
        self.ui.tf_work_name.setFont(font)
        self.ui.tf_work_descr.setFont(font)
        self.ui.tf_work_price.setFont(font)

        self.fix_models_list_position()
        self.model_list_widget.setFont(font)
        # self.model_list_widget.setMaximumSize(self.ui.input_search.width(), int(C.TABLE_FONT_SIZE * 1.5) * 6)

        # self.ui.table_parts.setMouseTracking(True)
        # self.ui.table_accesory.setMouseTracking(True)
        # self.ui.table_accesory.mouseMoveEvent(QtGui.QMouseEvent)

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

    # def search_on_narrow_change(self, state):
    #     C.NARROW_SEARCH = state
    #     self.search_and_upd_model_buttons(self.ui.input_search.text())
    #
    # def search_smart_change(self, state):
    #     C.SMART_SEARCH = state
    #     self.search_and_upd_model_buttons(self.ui.input_search.text())
    #
    # def search_latin_change(self, state):
    #     C.LATIN_SEARCH = state
    #     self.search_and_upd_model_buttons(self.ui.input_search.text())
    def fix_models_list_position(self):
        self.model_list_widget.move(int(self.ui.input_search.x() + 12),
                                    int(self.ui.HEAD.height() - 6))
        # self.model_list_widget.move(int(self.width() / 2 - self.ui.input_search.width() / 2),
        #                             int(self.ui.HEAD.height() - 6))

    def start_search_on_rule_change(self):
        C.NARROW_SEARCH = self.ui.chb_search_narrow.checkState()
        C.SMART_SEARCH = self.ui.chb_search_smart.checkState()
        C.LATIN_SEARCH = self.ui.chb_search_eng.checkState()
        self.prepare_and_search(self.ui.input_search.text(), True)

    def prepare_and_search(self, search_req, force_search=False):
        # print(f'{search_req=} {self.ui.input_search.isModified()=}')
        if self.ui.input_search.isModified() or force_search:
            if search_req == '':
                self.upd_models_list(True)
                return

            result_req = self.apply_rule_latin(search_req)
            result_req = self.apply_rule_narrow(result_req)

            if result_req:
                # print(f'{search_req=} {result_req=}')
                if self.Price is not None:
                    self.models = self.Price.search_price_models(search_req, C.MODEL_LIST_MAX_SIZE, C.SMART_SEARCH)
                else:
                    self.update_price_status()
                if self.models:
                    self.upd_models_list()
            else:
                self.upd_models_list(True)

    def apply_rule_latin(self, search_req):
        # LATIN RULE: Turn all input text into ascii
        result_req = ''
        if C.LATIN_SEARCH:
            # print(f'Applying LATIN to: {search_req}')
            lower_req = search_req.lower()
            for symbol in lower_req:
                if symbol in C.SYMBOL_TO_LATIN:
                    result_req = f'{result_req}{C.SYMBOL_TO_LATIN[symbol]}'
                else:
                    result_req = f'{result_req}{symbol}'
            self.ui.input_search.setText(result_req)
        else:
            result_req = search_req
        return result_req

    @staticmethod
    def apply_rule_narrow(in_req):
        # NARROW RULE: search only if search request longer then C.NARROW_SEARCH_LEN
        if C.NARROW_SEARCH and len(in_req) < C.NARROW_SEARCH_LEN:
            return
        return in_req

    def upd_models_list(self, clear=False):
        if clear or not self.models:
            self.model_list_widget.clear()
            self.model_list_widget.hide()
            return

        size = C.MODEL_LIST_MAX_SIZE if len(self.models) > C.MODEL_LIST_MAX_SIZE else len(self.models)
        # print(f'{size=}')
        self.model_list_widget.setFixedHeight(int(C.TABLE_FONT_SIZE * 1.6) * size)
        self.model_list_widget.show()
        if C.MODEL_LIST_REVERSED:
            models_list = reversed((self.models.keys()))
        else:
            models_list = (self.models.keys())

        self.model_list_widget.clear()
        self.model_list_widget.addItems(models_list)
        self.model_list_widget.setCurrentRow(0)
        # print(f'{models_list=}')

    # def search_and_upd_model_buttons(self, search_req):
    #     self.model_buttons = {}
    #     if self.latin_process:
    #         self.latin_process = False
    #         return
    #     lay = self.ui.scroll_models_layout.layout()
    #     self.clear_layout(lay)
    #     res_req = ''
    #     if C.LATIN_SEARCH:
    #         lower_req = search_req.lower()
    #         for symbol in lower_req:
    #             if symbol in C.SYMBOL_TO_LATIN:
    #                 res_req = f'{res_req}{C.SYMBOL_TO_LATIN[symbol]}'
    #             else:
    #                 res_req = f'{res_req}{symbol}'
    #         # self.latin_process = True
    #         # self.ui.input_search.setText(res_req)
    #     else:
    #         res_req = search_req
    #     if C.NARROW_SEARCH and len(res_req) < C.NARROW_SEARCH_LEN or len(res_req) <= 0:
    #         if C.LATIN_SEARCH:
    #             self.ui.input_search.setEditText(res_req)
    #         return
    #     # print(f'{len(res_req)=} {self.models=}')
    #
    #     # if not self.latin_process:
    #     self.models = self.Price.search_price_models(res_req, C.MODEL_LIST_SIZE, C.SMART_SEARCH)
    #     if self.models:
    #         self.upd_model_buttons(lay)
    #     elif DK9.addiction() and self.Price.APPROVED and res_req:
    #         self.add_search_button(lay, res_req)
    #     else:
    #         self.model_buttons = {}
    #     if C.LATIN_SEARCH:
    #         self.ui.input_search.setEditText(res_req)
    #     # self.latin_process = False

    # def upd_model_buttons(self, lay):
    # if C.MODEL_LIST_REVERSED:
    #     models_list = reversed((self.models.keys()))
    # else:
    #     models_list = (self.models.keys())

    # sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
    # lay.addItem(sp)
    # le = len(self.models)
    # self.model_buttons = {}
    # self.current_model_button_index = 0
    # for num, model in enumerate(models_list):
    #     self.model_buttons[num] = QPushButton(model)
    #     self.model_buttons[num].clicked.connect(self.scheduler)
    #     if num == 0:
    #         self.model_buttons[num].setDefault(True)
    #     lay.addWidget(self.model_buttons[num], 0)
    #     le -= 1

    # def add_search_button(self, lay, search_req: str):
    #     sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
    #     lay.addItem(sp)
    #     self.current_model_button_index = 0
    #     # print(f'{search_req=}')
    #     if search_req:
    #         self.model_buttons[0] = QPushButton(search_req)
    #         self.model_buttons[0].clicked.connect(self.scheduler)
    #         self.model_buttons[0].setDefault(True)
    #         lay.addWidget(self.model_buttons[0], 0)

    def update_price_status(self):
        if self.Price is None:
            self.ui.price_status.setText("Прайс не загружен")
        else:
            self.ui.price_status.setText(f'{self.Price.message if self.Price else "Прайс не найден"}')

    # @QtCore.pyqtSlot
    def scheduler(self, item):
        model = item.text()
        self.upd_models_list(True)
        # model = self.model_list_widget.itemClicked.text()
        print(f'Start sheduler: {model=}')
        self.update_price_table(model)
        if self.ui.input_search.text() and self.ui.input_search.text() != self.old_search:
            self.old_search = self.ui.input_search.text()
            model = (self.old_search.split())[0].lower()
            if model in C.NOT_FULL_MODEL_NAMES:  # For models with divided name like iPhone | 11
                self.curr_model = model
            else:
                self.curr_model = self.old_search
            self.search_dk9()

    def update_web_status(self, status: int):
        if status in C.WEB_STATUSES:
            self.web_status = status
            self.ui.web_status.setText(C.WEB_STATUSES[status])
            if status != 2:
                self.curr_model = ''
        else:
            print(f'Error: status code {status} not present {C.WEB_STATUSES=}')

    def search_dk9(self):
        if self.search_again:
            print(f'SEARCH AGAIN: {self.curr_model}')
            self.worker = Worker(DK9.adv_search, self.curr_type, self.curr_firm, self.curr_model, self.curr_description)
            self.search_again = False
        else:
            self.worker = Worker(DK9.adv_search, self.curr_type, self.curr_firm, self.curr_model, self.curr_description)
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

    def update_dk9_data(self, table_soups):
        if not table_soups or not table_soups[0]:
            self.update_web_status(0)

        if self.web_status == 2:
            self.load_progress(70)
            self.fill_table_from_soup(table_soups[0], self.ui.table_parts, C.DK9_BG_P_COLOR1, C.DK9_BG_P_COLOR2)
            self.load_progress(85)
            self.fill_table_from_soup(table_soups[1], self.ui.table_accesory, C.DK9_BG_A_COLOR1, C.DK9_BG_A_COLOR2)
        else:
            self.login_dk9()
        self.load_progress(100)

    def update_price_table(self, model):  # 'xiaomi mi a2 m1804d2sg'
        try:
            if model in self.models:
                position = self.models[model]  # [Sheet 27:<XIAOMI>, 813] - sheet, row
                # print(f'{position=}')
                # Take needed columns for exact model
                if position[0].name in C.PRICE_SEARCH_COLUMN_NUMBERS:
                    columns = C.PRICE_SEARCH_COLUMN_NUMBERS[position[0].name]  # [2, 4, 5]
                else:
                    columns = C.PRICE_SEARCH_COLUMN_NUMBERS['+']
                # print(f'{columns=}')
                row = Price.get_row_in_pos(position)
                row_len = len(row)
                # print(f'{row=}')

                new_row_num = 0
                self.ui.table_price.setRowCount(0)
                # self.ui.model_lable.setText(self.list_to_string(row))
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

                        # cells_text = [str(row[columns[0]]), str(row[columns[1]])]
                        if cells_texts[0] or len(cells_texts[1]) > 3:

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
                            row = position[0].row_values(i + 1, 0, 9)
                            if row[0] != '':
                                if row[0] not in C.PRICE_TRASH_IN_CELLS:
                                    return
                            # print(row[col[0]-1, col[1]-1, col[2]-1])
                        else:
                            return
        except Exception as _err:
            self.error((f'Error updating price table for:\n{model}', _err))

    def load_progress(self, progress):
        # if self.web_status not in (1, 2):
        #     self.ui.web_load_progress_bar.setValue(90)
        # else:
        self.ui.web_load_progress_bar.setValue(progress)

    def finished(self):
        if self.web_status not in (1, 2):
            self.ui.web_load_progress_bar.setValue(100)
        else:
            self.ui.web_load_progress_bar.setValue(0)
        # self.update_status()

    def fill_table_from_soup(self, soup, table, def_bg_color1, def_bg_color2):
        try:
            r = 0
            table.setRowCount(0)
            if not soup:
                # M.warning(f'Got zero soup:\n{table.objectName()}', 'still hungry :(')
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
                    table.insertRow(r)
                    for dk9_td in dk9_row.findAll('td'):
                        # if c == 3:
                        #     print(f'{dk9_td.string} {}')
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
                            # if 'align' in dk9_td.attrs:
                            #     align = str(dk9_td['align'])
                            #     if align == 'center':
                            #         self.ui.table_parts.item(r, c).setTextAlignment(1)
                            else:
                                dbgc = def_bg_color1 if r % 2 else def_bg_color2
                                table.item(r, c).setBackground(QtGui.QColor(dbgc[0], dbgc[1], dbgc[2]))
                        c += 1
                r += 1
        except Exception as _err:
            self.error((f'Error updating table:\n{table}', _err))

    def copy_table_item(self):
        font = QtGui.QFont()
        # font.setBold(True)
        font.setUnderline(True)
        selected_row = self.sender().selectedItems()
        text = ''
        for i in range(4):
            text = f'{text} {selected_row[i].text()} '
            # selected_row[i].setSelected(False)
            selected_row[i].setFont(font)
        clipboard.setText(text)

    def cash_table_element(self):
        font = QtGui.QFont()
        # font.setBold(True)
        # font.setUnderline(True)
        selected_row = self.sender().selectedItems()
        print(f'{selected_row=}')
        # text = ''
        # for i in range(3):
        self.ui.tf_work_name.setPlainText(selected_row[0].text())
        self.ui.tf_work_descr.setPlainText(selected_row[2].text())
        self.ui.tf_work_price.setPlainText(selected_row[1].text())
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
            self.ui.input_search.setFocus()
            # self.ui.input_search.text.selectAll()
            # self.update_status()
            # print(f"window is the active window: {self.isActiveWindow()}")

    # def event(self, event):
    #     # print(f'Event type: {event.type()}')
    #     if event.type() == QEvent.KeyPress:# and event.key() == Qt.Key_Tab:
    #         print(f'TAB {self.ui.tab_widget.currentIndex()=} {event.key()=}')
    #     return QMainWindow.event(self, event)

    # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
    #     index = event.pos()
    #     print(f'{index=}')

    def resizeEvent(self, event):
        self.resized.emit()
        return super(QMainWindow, self).resizeEvent(event)

    def keyPressEvent(self, event) -> None:
        # print(f'KEYPRESS: {event.key()}')
        if self.models \
                and (0 <= self.model_list_widget.currentRow() < len(self.models) or self.model_list_widget.isHidden()):
            # print(f'{self.current_model_button_index=} {self.model_buttons=} ')
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if self.model_list_widget.isHidden():
                    self.upd_models_list()
                    return
                self.scheduler(self.model_list_widget.currentItem())
            elif event.key() == Qt.Key_Up:
                idx = self.model_list_widget.currentRow() - 1
                if idx < 0:
                    idx = len(self.models) - 1
                self.model_list_widget.setCurrentRow(idx)
                # print('Wow, Up')
            elif event.key() == Qt.Key_Down:
                if self.model_list_widget.isHidden():
                    self.upd_models_list()
                    return
                idx = self.model_list_widget.currentRow() + 1
                if idx > len(self.models) - 1:
                    idx = 0
                self.model_list_widget.setCurrentRow(idx)
        # elif self.model_list_widget.isHidden() \
        #         and (event.key() == Qt.Key_Down
        #              or event.key() == Qt.Key_Return
        #              or event.key() == Qt.Key_Enter):
        #     self.model_list_widget.show()
        # if event.key() in (Qt.Key_Return, Qt.Key_Enter):
        #     self.model_buttons[self.current_model_button_index].click()
        # elif event.key() == Qt.Key_Up:
        #     self.model_buttons[self.current_model_button_index].setDefault(False)
        #     self.current_model_button_index -= 1
        #     if self.current_model_button_index < 0:
        #         self.current_model_button_index = len(self.model_buttons) - 1
        #     self.model_buttons[self.current_model_button_index].setDefault(True)
        #     self.model_buttons[self.current_model_button_index].setFocus()
        #     # print('Wow, Up')
        # elif event.key() == Qt.Key_Down:
        #     self.model_buttons[self.current_model_button_index].setDefault(False)
        #     self.current_model_button_index += 1
        #     if self.current_model_button_index > len(self.model_buttons) - 1:
        #         self.current_model_button_index = 0
        #     self.model_buttons[self.current_model_button_index].setDefault(True)
        #     self.model_buttons[self.current_model_button_index].setFocus()
        # print('Wow, Down')
        # self.ui.input_search.setFocus()
        # self.ui.input_search.selectAll()
        if event.key() == Qt.Key_Alt:
            # print(f'TAB {self.ui.tab_widget.currentIndex()=}')
            if self.ui.tab_widget.currentIndex() == 0:
                self.ui.tab_widget.setCurrentIndex(1)
            else:
                self.ui.tab_widget.setCurrentIndex(0)

        self.ui.input_search.setFocus()
        self.ui.input_search.selectAll()

    def open_settings(self):
        settings_ui = ConfigWindow(self.login_dk9)
        settings_ui.setWindowIcon(QtGui.QIcon(C.LOGO))
        settings_ui.exec_()
        settings_ui.show()

    @staticmethod
    def open_help():
        help_ui = HelpWindow()
        help_ui.setWindowIcon(QtGui.QIcon(C.LOGO))
        help_ui.exec_()
        help_ui.show()

    @staticmethod
    def error(errors: tuple):
        msg_box = QMessageBox()
        text, info = '', ''
        for i, e in enumerate(errors):
            if i == 1:
                text = str(e)
            else:
                info = f'{info}\n{str(e)}'
        print(f'{text}\n -> {info}')
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setInformativeText(str(info))
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        # msg_box.show()
        msg_box.exec_()
        msg_box.show()


class HelpWindow(QDialog):
    def __init__(self):
        super().__init__()
        print(f'Reading {C.HELP}')
        try:
            file = open(C.HELP, 'r', encoding='utf-8')
            with file:
                text = file.read()

            self.ui = Ui_Dialog()
            self.ui.setupUi(self)
            self.ui.text.setPlainText(text)
        except Exception as _err:
            App.error((f'Error while reading help file:\n{C.HELP}', _err))


class ConfigWindow(QDialog):
    def __init__(self, login_func):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.login_func = login_func
        self.ui = Ui_settings_window()
        self.ui.setupUi(self)
        self.ui.web_login.setText(C.DK9_LOGIN)
        self.ui.web_password.setText(C.DK9_PASSWORD)
        self.ui.chk_fullscreen.setCheckState(2 if C.FULLSCREEN else 0)
        self.ui.zebra_contrast.setValue(C.DK9_COL_DIFF)
        self.ui.tables_font_size.setValue(C.TABLE_FONT_SIZE)
        self.ui.colored_web_table.setCheckState(2 if C.DK9_COLORED else 0)
        self.ui.colored_price_table.setCheckState(2 if C.PRICE_COLORED else 0)
        # self.ui.wide_monitor.setCheckState(2 if C.WIDE_MONITOR else 0)
        # self.ui.column_width_max.setValue(C.TABLE_COLUMN_SIZE_MAX)
        # self.ui.buttonBox.button()..accept.connect(self.apply_settings())
        self.ui.buttonBox.accepted.connect(self.apply_settings)

    def apply_settings(self):
        print('Applying settings')
        login = False
        if C.DK9_LOGIN != self.ui.web_login.text() or C.DK9_PASSWORD != self.ui.web_password.text():
            login = True
        C.DK9_LOGIN = self.ui.web_login.text()
        C.DK9_PASSWORD = self.ui.web_password.text()
        C.FULLSCREEN = True if self.ui.chk_fullscreen.checkState() == 2 else False
        C.DK9_COL_DIFF = self.ui.zebra_contrast.value()
        C.TABLE_FONT_SIZE = self.ui.tables_font_size.value()
        C.DK9_COLORED = True if self.ui.colored_web_table.checkState() == 2 else False
        C.PRICE_COLORED = True if self.ui.colored_price_table.checkState() == 2 else False
        # C.WIDE_MONITOR = True if self.ui.wide_monitor.checkState() == 2 else False
        # C.TABLE_COLUMN_SIZE_MAX = self.ui.column_width_max.value()
        window.init_ui_dynamics()
        C.precalculate_color_diffs()
        try:
            C.save_user_config()
        except Exception as _err:
            App.error((f'Error while saving config file:\n{C.HELP}', _err))
        if login:
            DK9.change_data(C.data())
            print(f'{DK9.DATA=}')
            self.login_func()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(C.LOGO))
        clipboard = app.clipboard()
        window = App()
        window.setWindowIcon(QtGui.QIcon(C.LOGO))
        window.show()
        window.ui.input_search.setFocus()
        sys.exit(app.exec_())
    except Exception as err:
        App.error((f'Error:\nGLOBAL', err))
