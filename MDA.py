import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QSpacerItem, QSizePolicy, QTableWidgetItem, QHeaderView, qApp, QDialog, QWidget, QLabel, QHBoxLayout
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt

from content.config import Config
from content.dk9 import DK9Parser
from content.price import Price
from content.window_main import Ui_MainWindow
from content.window_settings import Ui_settings_window

# try:
#     # Включите в блок try/except, если вы также нацелены на Mac/Linux
#     from PyQt5.QtWinExtras import QtWin  # !!!
#     myappid = 'mycompany.myproduct.subproduct.version'  # !!!
#     QtWin.setCurrentProcessExplicitAppUserModelID(myappid)  # !!!
# except ImportError:
#     pass

C = Config()


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
        self.SESSION = None
        self.validation_data = None
        self.old_search = ''
        self.thread = QtCore.QThread
        self.worker = None  # Worker(self.update_dk9_data, 'mi8 lite')
        # print('Creating DK9')
        self.DK9 = DK9Parser(C.DK9_LOGIN_URL, C.DK9_SEARCH_URL, C.DK9_HEADERS, C.DK9_LOGIN_DATA)
        print('Login to DK9')
        self.login_dk9()
        print('Loading Price')
        self.Price = Price(C.PATH, C.PRICE_PATH, C.PRICE_PARTIAL_NAME, C.PRICE_TRASH_IN_CELLS)
        self.ui.price_name.setText(self.Price.message)
        # self.thread.start(self.worker)
        # self.update_dk9_data('mi8 lite')

    def init_ui_statics(self):
        self.ui.input_search.textChanged[str].connect(self.search_and_upd_model_buttons)
        self.ui.chb_search_strict.stateChanged[int].connect(self.search_on_strict_change)
        self.ui.settings_button.clicked.connect(self.open_settings)

        self.ui.table_left.setHorizontalHeaderLabels(('', 'Виды работ', 'Цена', 'Прим', '', ''))
        self.ui.table_parts.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                       'Цена', 'Шт', 'Дата', 'Где'))
        self.ui.table_accesory.setHorizontalHeaderLabels(('Тип', 'Фирма', 'Модель', 'Примечание',
                                                          'Цена', 'Шт', 'Дата', 'Где'))

        # widget = QWidget()
        # self.setCentralWidget(widget)
        # pixmap1 = QtGui.QPixmap('/content/start_test.png')
        # # pixmap1 = pixmap1.scaledToWidth(self.windowsize.width())
        # pixmap1 = pixmap1.scaledToWidth(100)
        # self.image = QLabel()
        # self.image.setPixmap(pixmap1)

        # layout_box = QHBoxLayout(widget)
        # layout_box.setContentsMargins(0, 0, 0, 0)
        # layout_box.addWidget(self.image)

        # pixmap2 = QtGui.QPixmap('/content/start_test.png')
        # self.image2 = QLabel(self.ui.table_left)
        # self.image2.setPixmap(pixmap2)
        # self.image2.setFixedSize(pixmap2.size())
        # self.ui.table_left.addWidget(self.image2)

        self.ui.table_parts.doubleClicked.connect(self.copy_table_item)
        self.ui.table_accesory.doubleClicked.connect(self.copy_table_item)

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
        # print(f'{C.STRICT_SEARCH=} {state=}')
        self.search_and_upd_model_buttons(self.ui.input_search.text())

    def search_and_upd_model_buttons(self, search_req):
        lay = self.ui.scroll_models_layout.layout()
        self.clear_layout(lay)
        if C.STRICT_SEARCH and len(search_req) < C.STRICT_SEARCH_LEN or len(search_req) <= 0:
            return
        # print(f'{len(search_req)=} {C.STRICT_SEARCH=}')
        search_req = search_req.lower()
        self.models = self.Price.search_price_models(search_req, C.MODEL_LIST_SIZE)
        if self.models:
            self.upd_model_buttons(lay)

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

    def login_dk9(self):
        self.worker = Worker(self.DK9.login)
        # self.worker.signals.result.connect(self.update_dk9_data)
        self.worker.signals.progress.connect(self.load_progress)
        self.worker.signals.finished.connect(self.finished)

        self.thread.start(self.worker)
    # @QtCore.pyqtSlot
    def scheduler(self):
        # print('Start sheduler')
        model = self.sender().text()
        self.update_price_table(model)
        if self.ui.input_search.text() and self.ui.input_search.text() != self.old_search:
            self.old_search = self.ui.input_search.text()
            model = (self.old_search.split())[0].lower()
            if model in C.NOT_FULL_MODEL_NAMES:  # For models with divided name like iPhone | 11
                curr_model = model
                # self.update_dk9_data(model)
            else:
                curr_model = self.old_search
                # self.update_dk9_data(self.old_search)

            self.worker = Worker(self.DK9.search, curr_model)
            self.worker.signals.result.connect(self.update_dk9_data)
            self.worker.signals.progress.connect(self.load_progress)
            self.worker.signals.finished.connect(self.finished)

            self.thread.start(self.worker)

    def update_dk9_data(self, table_soups):
        # self.worker = Worker(self.DK9.search, search)
        # self.thread.start(self.worker)
        # part_table_soup, accessory_table_soup = *self.worker.result  #self.DK9.search(search)
        self.load_progress(70)
        self.fill_table_from_soup(table_soups[0], self.ui.table_parts, C.DK9_BG_P_COLOR1, C.DK9_BG_P_COLOR2)
        self.load_progress(85)
        self.fill_table_from_soup(table_soups[1], self.ui.table_accesory, C.DK9_BG_A_COLOR1, C.DK9_BG_A_COLOR2)
        self.load_progress(100)

    def update_price_table(self, model):  # 'xiaomi mi a2 m1804d2sg'
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

    def load_progress(self, progress):
        self.ui.web_load_progress_bar.setValue(progress)

    def finished(self):
        self.ui.web_load_progress_bar.setValue(0)

    @staticmethod
    def fill_table_from_soup(soup, table, def_bg_color1, def_bg_color2):
        r = 0
        table.setRowCount(0)
        if not soup:
            print(f'ERROR: Soup = {soup}')
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

    # @staticmethod
    # def close_cmd():
    #     WMI = GetObject('winmgmts:')
    #     processes = WMI.InstancesOf('Win32_Process')
    #
    #     for p in WMI.ExecQuery('select * from Win32_Process where Name="cmd.exe"'):
    #         print("Killing PID:", p.Properties_('ProcessId').Value)
    #         os.system("taskkill /pid " + str(p.Properties_('ProcessId').Value))

    # class Settings(QDialog):
    #     def __init__(self):
    #         super().__init__()
    def open_settings(self):
        # settings_ui = QDialog()
        # settings_ui.win = Ui_settings_window()
        # settings_ui.win.setupUi(self)
        # settings_ui.buttonBox.accepted.connect()
        # settings_ui.buttonBox.accepted.connect()
        settings_ui = ConfigWindow()
        settings_ui.setWindowIcon(QtGui.QIcon(f'content/start_test.png'))
        settings_ui.exec_()
        settings_ui.show()

    def accept(self):
        print(f'ACCEPTED')

    def reject(self):
        print(f'REJECTED')


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
        # print(f'{C.DK9_COL_DIFF}')
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
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as err:
            # traceback.print_exc()
            print(err)
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, err))  # traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(f'content/start_test.png'))
    clipboard = app.clipboard()
    window = App()
    window.setWindowIcon(QtGui.QIcon(f'content/start_test.png'))
    window.show()
    window.ui.input_search.setFocus()
    sys.exit(app.exec_())
