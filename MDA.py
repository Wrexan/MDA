import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QSpacerItem, QSizePolicy, QTableWidgetItem, QHeaderView, qApp, QDialog, QMessageBox
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt

from MDA_content.config import Config
from MDA_content.dk9 import DK9Parser
from MDA_content.price import Price
from MDA_content.window_main import Ui_MainWindow
from MDA_content.window_settings import Ui_settings_window
from MDA_content.window_simple import Ui_Dialog

C = Config()
DK9 = DK9Parser(C.DK9_LOGIN_URL, C.DK9_SEARCH_URL, C.DK9_HEADERS, C.DK9_LOGIN_DATA)


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setFocus()
        # self.setWindowIcon(QtGui.QIcon(f'content/start_test.ico'))
        qApp.focusChanged.connect(self.on_focusChanged)

        # self.PRICE_DB = xlrd.open_workbook(sys.path[0] + '\\' + PRICE_PATH + PRICE_NAME, formatting_info=True)
        # self.PRICE_DB = xlrd.open_workbook(PRICE_PATH + price_name, formatting_info=True)
        # self.prepare_columns()
        self.models = {}
        self.model_buttons = {}
        self.current_model_button_index = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui_statics()
        self.init_ui_dynamics()


        # self.SESSION = None
        # self.validation_data = None
        self.next_model = ''
        self.curr_model = ''
        self.old_search = ''
        self.thread = QtCore.QThread
        self.worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        print('Loading Price')
        self.Price = Price(C.PATH, C.PRICE_PATH, C.PRICE_PARTIAL_NAME, C.PRICE_TRASH_IN_CELLS)
        print('Login to DK9')
        print(f'{C.DK9_LOGIN=} {C.DK9_PASSWORD=} {C.DK9_LOGIN_DATA=} ')
        self.web_status = 0
        self.login_dk9()
        self.update_price_status()
        # self.thread.start(self.worker)
        # self.update_dk9_data('mi8 lite')

    def init_ui_statics(self):
        self.ui.input_search.textChanged[str].connect(self.search_and_upd_model_buttons)
        self.ui.chb_search_strict.stateChanged[int].connect(self.search_on_strict_change)
        self.ui.chb_search_strict.setToolTip('Запрещает поиск по одному символу.')
        self.ui.smart_search.stateChanged[int].connect(self.search_smart_change)
        self.ui.smart_search.setToolTip('Применяет к запросу фильтр и выдает более релевантный результат.\n'
                                        'Отключение позволит найти всё, но может приводить к неожиданным последствиям.')
        self.ui.chb_search_eng.stateChanged[int].connect(self.search_latin_change)
        self.ui.chb_search_eng.setToolTip('Переводит символы алфавита в латиницу нижнего регистра.')
        self.ui.settings_button.clicked.connect(self.open_settings)

        self.ui.table_left.setHorizontalHeaderLabels(('', 'Виды работ', 'Цена', 'Прим', '', ''))
        self.ui.table_parts.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                       'Цена', 'Шт', 'Дата', 'Где'))
        self.ui.table_accesory.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                          'Цена', 'Шт', 'Дата', 'Где'))

        self.ui.table_parts.doubleClicked.connect(self.copy_table_item)
        self.ui.table_accesory.doubleClicked.connect(self.copy_table_item)
        self.ui.help.clicked.connect(self.open_help)

    def init_ui_dynamics(self):
        font = QtGui.QFont()
        # font.setBold(True)
        font.setPixelSize(C.TABLE_FONT_SIZE)

        self.ui.table_left.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_left.verticalHeader().setMaximumWidth(self.ui.table_left.width())
        # [self.ui.table_left.verticalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents) for i in range(5)]
        self.ui.table_parts.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_accesory.verticalHeader().setDefaultSectionSize(C.TABLE_FONT_SIZE + 4)
        self.ui.table_left.setFont(font)
        self.ui.table_parts.setFont(font)
        self.ui.table_accesory.setFont(font)
        self.ui.table_left.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_parts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_accesory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_left.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.table_parts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_accesory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        if not C.WIDE_MONITOR:
            self.ui.table_left.horizontalHeader().setMaximumSectionSize(int(C.TABLE_COLUMN_SIZE_MAX * 1.4))
            self.ui.table_parts.horizontalHeader().setMaximumSectionSize(C.TABLE_COLUMN_SIZE_MAX)
            self.ui.table_accesory.horizontalHeader().setMaximumSectionSize(C.TABLE_COLUMN_SIZE_MAX)
        else:
            self.ui.table_left.horizontalHeader().setMaximumSectionSize(2000)
            self.ui.table_parts.horizontalHeader().setMaximumSectionSize(2000)
            self.ui.table_accesory.horizontalHeader().setMaximumSectionSize(2000)

    def search_on_strict_change(self, state):
        C.STRICT_SEARCH = state
        self.search_and_upd_model_buttons(self.ui.input_search.text())

    def search_smart_change(self, state):
        C.SMART_SEARCH = state
        self.search_and_upd_model_buttons(self.ui.input_search.text())

    def search_latin_change(self, state):
        C.LATIN_SEARCH = state
        self.search_and_upd_model_buttons(self.ui.input_search.text())

    def search_and_upd_model_buttons(self, search_req):
        lay = self.ui.scroll_models_layout.layout()
        self.clear_layout(lay)
        if C.LATIN_SEARCH:
            lower_req = search_req.lower()
            res_req = ''
            for symbol in lower_req:
                if symbol in C.SYMBOL_TO_LATIN:
                    res_req = f'{res_req}{C.SYMBOL_TO_LATIN[symbol]}'
                else:
                    res_req = f'{res_req}{symbol}'
            self.ui.input_search.setText(res_req)
        if C.STRICT_SEARCH and len(search_req) < C.STRICT_SEARCH_LEN or len(search_req) <= 0:
            return
        # print(f'{len(search_req)=} {C.STRICT_SEARCH=}')
        search_req = search_req.lower()
        self.models = self.Price.search_price_models(search_req, C.MODEL_LIST_SIZE, C.SMART_SEARCH)
        if self.models:
            self.upd_model_buttons(lay)
        else:
            self.model_buttons = {}

    def upd_model_buttons(self, lay):
        # lay = self.ui.scroll_models_layout.layout()
        # self.clear_layout(lay)
        sp = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addItem(sp)
        le = len(self.models)
        self.model_buttons = {}
        self.current_model_button_index = 0
        if C.MODEL_LIST_REVERSED:
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

    def update_price_status(self):
        self.ui.price_status.setText(f'{self.Price.message if self.Price else "Прайс не найден"}')

    # @QtCore.pyqtSlot
    def scheduler(self):
        # print('Start sheduler')
        model = self.sender().text()
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
        print(f'SEARCH AGAIN: {self.next_model=} {self.curr_model}')
        if self.next_model:
            self.worker = Worker(DK9.search, self.next_model)
            self.next_model = ''
        else:
            self.worker = Worker(DK9.search, self.curr_model)
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
            self.next_model = self.curr_model
            print(f'GO TO SEARCH AGAIN: {self.next_model=} {self.curr_model}')
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
            self.ui.table_left.setRowCount(0)
            self.ui.model_lable.setText(self.list_to_string(row))
            for i in range(position[1], position[0].nrows - 1):
                # print(row[col[0] - 1, col[1] - 1, col[2] - 1])
                if row_len < columns[-1]:  # If row shorter, than we expect, then place all row in 0 column
                    # print('SHORT row:' + str(row))
                    cell_text = self.list_to_string(row)
                    self.ui.table_left.insertRow(new_row_num)
                    self.ui.table_left.setItem(new_row_num, 0, QTableWidgetItem(cell_text))
                    self.ui.table_left.item(new_row_num, 0).setToolTip(cell_text)
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

                        self.ui.table_left.insertRow(new_row_num)
                        for j, txt in enumerate(cells_texts):
                            self.ui.table_left.setItem(new_row_num, j, QTableWidgetItem(txt))
                            self.ui.table_left.item(new_row_num, j).setToolTip(txt)

                            if C.PRICE_COLORED and txt:
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
                            if row[0] not in C.PRICE_TRASH_IN_CELLS:
                                return
                        # print(row[col[0]-1, col[1]-1, col[2]-1])
                    else:
                        return
        except Exception as err:
            self.error((f'Error updating price table for:\n{model}', err))

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
        except Exception as err:
            self.error((f'Error updating table:\n{table}', err))

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
            self.ui.input_search.selectAll()
            # self.update_status()
            # print(f"window is the active window: {self.isActiveWindow()}")

    # def event(self, event):
    #     # print(f'Event type: {event.type()}')
    #     if event.type() == QEvent.KeyPress:# and event.key() == Qt.Key_Tab:
    #         print(f'TAB {self.ui.tab_widget.currentIndex()=} {event.key()=}')
    #     return QMainWindow.event(self, event)

    def keyPressEvent(self, event) -> None:
        # print(f'KEYPRESS: {event.key()}')
        if self.models and 0 <= self.current_model_button_index < len(self.model_buttons):
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

        self.ui.input_search.setFocus()
        self.ui.input_search.selectAll()

    @staticmethod
    def open_settings():
        settings_ui = ConfigWindow()
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


# class MessageBox(QMessageBox):
#     def __init__(self):
#         super().__init__()


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
        except Exception as err:
            App.error((f'Error while reading help file:\n{C.HELP}', err))


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.ui = Ui_settings_window()
        self.ui.setupUi(self)
        self.ui.web_login.setText(C.DK9_LOGIN)
        self.ui.web_password.setText(C.DK9_PASSWORD)
        self.ui.ui_models_num.setValue(C.MODEL_LIST_SIZE)
        self.ui.zebra_contrast.setValue(C.DK9_COL_DIFF)
        self.ui.tables_font_size.setValue(C.TABLE_FONT_SIZE)
        self.ui.colored_web_table.setCheckState(2 if C.DK9_COLORED else 0)
        self.ui.colored_price_table.setCheckState(2 if C.PRICE_COLORED else 0)
        self.ui.wide_monitor.setCheckState(2 if C.WIDE_MONITOR else 0)
        self.ui.column_width_max.setValue(C.TABLE_COLUMN_SIZE_MAX)
        # self.ui.buttonBox.button()..accept.connect(self.apply_settings())
        self.ui.buttonBox.accepted.connect(self.apply_settings)

    def apply_settings(self):
        print('Applying settings')
        C.DK9_LOGIN = self.ui.web_login.text()
        C.DK9_PASSWORD = self.ui.web_password.text()
        C.MODEL_LIST_SIZE = self.ui.ui_models_num.value()
        C.DK9_COL_DIFF = self.ui.zebra_contrast.value()
        C.TABLE_FONT_SIZE = self.ui.tables_font_size.value()
        C.DK9_COLORED = True if self.ui.colored_web_table.checkState() == 2 else False
        C.PRICE_COLORED = True if self.ui.colored_price_table.checkState() == 2 else False
        C.WIDE_MONITOR = True if self.ui.wide_monitor.checkState() == 2 else False
        C.TABLE_COLUMN_SIZE_MAX = self.ui.column_width_max.value()
        window.init_ui_dynamics()
        C.precalculate_color_diffs()
        C.save_user_config()


class Worker(QtCore.QThread):
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress'] = self.signals.progress
        self.kwargs['error'] = self.signals.error
        self.kwargs['status'] = self.signals.status

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as err:
            # traceback.print_exc()
            # App.error(f'Error while executing thread using:\n{self.args}\n{self.kwargs}', err)
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, err))  # traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    status = QtCore.pyqtSignal(int)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


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
