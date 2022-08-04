from PyQt5 import QtCore, QtWidgets

from MDA_UI.window_settings import Ui_settings_window
from MDA_UI.window_simple import Ui_Dialog
from MDA_UI.adv_search import Ui_Dialog as AdvSearchDialog


class HelpWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent):
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
            Parent.error((f'Error while reading help file:\n{C.HELP}', _err))


class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent, DK9):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.C = C
        self.Parent = Parent
        self.DK9 = DK9
        self.ui = Ui_settings_window()
        self.ui.setupUi(self)
        self.ui.web_login.setText(C.DK9_LOGIN)
        self.ui.web_password.setText(C.DK9_PASSWORD)
        self.ui.chk_fullscreen.setCheckState(2 if C.FULLSCREEN else 0)
        self.ui.zebra_contrast.setValue(C.DK9_COL_DIFF)
        self.ui.tables_font_size.setValue(C.TABLE_FONT_SIZE)
        self.ui.colored_web_table.setCheckState(2 if C.DK9_COLORED else 0)
        self.ui.colored_price_table.setCheckState(2 if C.PRICE_COLORED else 0)

        self.ui.chb_show_exact.setCheckState(2 if C.FILTER_SEARCH_RESULT else 0)
        self.ui.chb_price_name_only.setCheckState(2 if C.SEARCH_BY_PRICE_MODEL else 0)
        self.ui.chb_search_eng.setCheckState(2 if C.LATIN_SEARCH else 0)
        self.ui.chb_search_narrow.setCheckState(2 if C.NARROW_SEARCH else 0)
        # self.ui.wide_monitor.setCheckState(2 if C.WIDE_MONITOR else 0)
        # self.ui.column_width_max.setValue(C.TABLE_COLUMN_SIZE_MAX)
        # self.ui.buttonBox.button()..accept.connect(self.apply_settings())
        self.ui.buttonBox.accepted.connect(self.apply_settings)

    def apply_settings(self):
        print('Applying settings')
        login = False
        if self.C.DK9_LOGIN != self.ui.web_login.text() or self.C.DK9_PASSWORD != self.ui.web_password.text():
            login = True
        self.C.DK9_LOGIN = self.ui.web_login.text()
        self.C.DK9_PASSWORD = self.ui.web_password.text()

        self.C.FULLSCREEN = True if self.ui.chk_fullscreen.checkState() == 2 else False

        self.C.DK9_COL_DIFF = self.ui.zebra_contrast.value()
        self.C.TABLE_FONT_SIZE = self.ui.tables_font_size.value()
        self.C.DK9_COLORED = True if self.ui.colored_web_table.checkState() == 2 else False
        self.C.PRICE_COLORED = True if self.ui.colored_price_table.checkState() == 2 else False

        self.C.FILTER_SEARCH_RESULT = True if self.ui.chb_show_exact.checkState() == 2 else False
        self.C.SEARCH_BY_PRICE_MODEL = True if self.ui.chb_price_name_only.checkState() == 2 else False
        self.C.LATIN_SEARCH = True if self.ui.chb_search_eng.checkState() == 2 else False
        self.C.NARROW_SEARCH = True if self.ui.chb_search_narrow.checkState() == 2 else False
        # C.WIDE_MONITOR = True if self.ui.wide_monitor.checkState() == 2 else False
        # C.TABLE_COLUMN_SIZE_MAX = self.ui.column_width_max.value()
        self.Parent.init_ui_dynamics()
        self.C.precalculate_color_diffs()
        try:
            self.C.save_user_config()
        except Exception as _err:
            self.Parent.error((f'Error while saving config file:\n{self.C.HELP}', _err))
        if login:
            self.DK9.change_data(self.C.c_data())
            print(f'{self.DK9.CDATA=}')
            self.Parent.login_dk9()


class AdvancedSearchWindow(QtWidgets.QDialog):
    def __init__(self, Parent):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.Parent = Parent
        self.ui = AdvSearchDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.apply_search)

    def apply_search(self):
        print('Applying advanced search')
        search = {'_type': self.ui.inp_name.text(),
                  '_manufacturer': self.ui.inp_manuf.text(),
                  '_model': self.ui.inp_model.text(),
                  '_description': self.ui.inp_descr.text()}
        self.Parent.search_dk9(advanced=search)
