from PyQt5 import QtCore, QtWidgets

from UI.window_first_start import Ui_start_window
from UI.window_settings import Ui_settings_window
from UI.window_help import Ui_Dialog
from UI.adv_search import Ui_Dialog as AdvSearchDialog
from utility.utils import PartFields, case_folded_or_none


class HelpWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent):
        super().__init__()
        print(f'Reading {C.HELP_FILE_PATH}')
        try:
            file = open(C.HELP_FILE_PATH, 'r', encoding='utf-8')
            with file:
                text = file.read()

            self.ui = Ui_Dialog()
            self.ui.setupUi(self)
            self.ui.text.setPlainText(text)
        except Exception as _err:
            Parent.error((f'Error while reading help file:\n{C.HELP_FILE_PATH}', _err))


class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent, DK9, L):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.C = C
        self.Parent = Parent
        self.DK9 = DK9
        self.L = L
        self.ui = Ui_settings_window()
        self.ui.setupUi(self)
        self.ui.web_login.setText(self.C.DK9_LOGIN)
        self.ui.web_password.setText(self.C.DK9_PASSWORD)
        self.ui.chb_dk9_caching.setCheckState(2 if self.C.DK9_CACHING else 0)
        self.ui.dk9_caching_minutes.setValue(self.C.DK9_CACHING_PERIOD)

        self.ui.cb_branch.addItems(self.C.BRANCHES.values())
        self.ui.cb_branch.setCurrentIndex(self.C.BRANCH)

        self.ui.cb_language.addItems(self.C.LANGS)
        self.ui.cb_language.setCurrentIndex(self.C.CURRENT_LANG)
        self.ui.cb_language.currentIndexChanged.connect(self.apply_selected_language)

        self.ui.chk_fullscreen.setCheckState(2 if C.FULLSCREEN else 0)
        self.ui.zebra_contrast.setValue(C.DK9_COL_DIFF)
        self.ui.tables_font_size.setValue(C.TABLE_FONT_SIZE)
        self.ui.colored_web_table.setCheckState(2 if C.DK9_COLORED else 0)
        self.ui.colored_price_table.setCheckState(2 if C.PRICE_COLORED else 0)
        self.ui.word_wrap_web_table.setCheckState(2 if C.WORD_WRAP_DK9 else 0)
        self.ui.word_wrap_price_table.setCheckState(2 if C.WORD_WRAP_PRICE else 0)

        # self.ui.chb_show_exact.setCheckState(2 if C.FILTER_SEARCH_RESULT else 0)
        # self.ui.chb_show_compatibility.setCheckState(2 if C.SHOW_COMPATIBILITY else 0)
        self.ui.chb_search_eng.setCheckState(2 if C.LATIN_SEARCH else 0)
        self.ui.chb_search_narrow.setCheckState(2 if C.NARROW_SEARCH else 0)

        self.ui.income_overprice_perc.setValue(C.INCOME_PARTS_MARGIN_PERC)
        # self.ui.wide_monitor.setCheckState(2 if C.WIDE_MONITOR else 0)
        # self.ui.column_width_max.setValue(C.TABLE_COLUMN_SIZE_MAX)
        # self.ui.buttonBox.button()..accept.connect(self.apply_settings())
        self.ui.buttonBox.accepted.connect(self.apply_settings)

    def apply_selected_language(self):
        self.C.CURRENT_LANG = self.ui.cb_language.currentIndex()
        self.L.load_language()
        self.L.apply_lang()
        self.L.translate_ConfigWindow_texts(self)
        self.Parent.upd_ui_static_texts()
        self.Parent.init_ui_dynamics()

    def apply_settings(self):
        print('Applying settings')
        login = False
        if self.C.DK9_LOGIN != self.ui.web_login.text() or self.C.DK9_PASSWORD != self.ui.web_password.text():
            login = True
        self.C.DK9_LOGIN = self.ui.web_login.text()
        self.C.DK9_PASSWORD = self.ui.web_password.text()
        self.C.DK9_CACHING = True if self.ui.chb_dk9_caching.checkState() == 2 else False
        self.C.DK9_CACHING_PERIOD = self.ui.dk9_caching_minutes.value()
        cbi = self.ui.cb_branch.currentIndex()
        self.C.BRANCH = cbi if self.C.BRANCHES.get(cbi) else 0

        self.C.FULLSCREEN = True if self.ui.chk_fullscreen.checkState() == 2 else False

        self.C.DK9_COL_DIFF = self.ui.zebra_contrast.value()
        self.C.TABLE_FONT_SIZE = self.ui.tables_font_size.value()
        self.C.DK9_COLORED = True if self.ui.colored_web_table.checkState() == 2 else False
        self.C.PRICE_COLORED = True if self.ui.colored_price_table.checkState() == 2 else False
        self.C.WORD_WRAP_DK9 = True if self.ui.word_wrap_web_table.checkState() == 2 else False
        self.C.WORD_WRAP_PRICE = True if self.ui.word_wrap_price_table.checkState() == 2 else False

        # self.C.FILTER_SEARCH_RESULT = True if self.ui.chb_show_exact.checkState() == 2 else False
        # self.C.SEARCH_BY_PRICE_MODEL = True if self.ui.chb_price_name_only.checkState() == 2 else False
        self.C.LATIN_SEARCH = True if self.ui.chb_search_eng.checkState() == 2 else False
        self.C.NARROW_SEARCH = True if self.ui.chb_search_narrow.checkState() == 2 else False
        # self.C.SHOW_COMPATIBILITY = True if self.ui.chb_show_compatibility.checkState() == 2 else False

        self.C.INCOME_PARTS_MARGIN_PERC = self.ui.income_overprice_perc.value()
        # C.WIDE_MONITOR = True if self.ui.wide_monitor.checkState() == 2 else False
        # C.TABLE_COLUMN_SIZE_MAX = self.ui.column_width_max.value()
        if self.C.BRANCH == 0:
            self.Parent.reset_stat_timer()
        if self.C.DK9_CACHING:
            self.Parent.dk9_upd_cache_restart_timer()
        else:
            self.Parent.dk9_cache_timer.stop()
        self.Parent.init_ui_dynamics()
        self.Parent.upd_username()
        self.C.precalculate_color_diffs()
        try:
            self.C.save_user_config()
        except Exception as _err:
            self.Parent.error((f'Error while saving config file:\n{self.C.USER_CONFIG}', _err))
        if login:
            self.DK9.change_data(self.C.c_data())
            print(f'{self.DK9.CDATA=}')
            self.Parent.dk9_login_start_worker()


class FirstStartWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent, DK9, L):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.C = C
        self.Parent = Parent
        self.DK9 = DK9
        self.L = L
        self.ui = Ui_start_window()
        self.ui.setupUi(self)
        self.ui.web_login.setText(C.DK9_LOGIN)
        self.ui.web_password.setText(C.DK9_PASSWORD)

        self.ui.cb_language.addItems(self.C.LANGS)
        self.ui.cb_language.setCurrentIndex(self.C.CURRENT_LANG)
        self.ui.cb_language.currentIndexChanged.connect(self.apply_selected_language)

        self.ui.pb_stat_0.clicked.connect(self.apply_stat)
        self.ui.pb_stat_1.clicked.connect(self.apply_stat)
        self.ui.pb_stat_2.clicked.connect(self.apply_stat)
        self.ui.pb_stat_3.clicked.connect(self.apply_stat)

    def apply_selected_language(self):
        self.C.CURRENT_LANG = self.ui.cb_language.currentIndex()
        self.L.load_language()
        self.L.apply_lang()
        self.L.translate_StartWindow_texts(self)
        self.Parent.upd_ui_static_texts()
        self.Parent.init_ui_dynamics()

    def apply_stat(self):
        button_num = int(self.sender().objectName()[-1])
        if button_num == 0:
            self.Parent.reset_stat_timer()
        self.C.BRANCH = button_num
        print(f'Chosen stat for: {self.C.BRANCHES[self.C.BRANCH]}')
        self.apply_settings()

    def apply_settings(self):
        print('Applying settings')
        login = False
        if self.ui.web_login.text() and self.ui.web_password.text():
            login = True
            self.C.DK9_LOGIN = self.ui.web_login.text()
            self.C.DK9_PASSWORD = self.ui.web_password.text()
            self.Parent.upd_username()
        try:
            self.C.save_user_config()
        except Exception as _err:
            self.Parent.error((f'Error while saving config file:\n{self.C.USER_CONFIG}', _err))
        if login:
            self.DK9.change_data(self.C.c_data())
            print(f'{self.DK9.CDATA=}')
            self.Parent.dk9_login_start_worker()
            # self.Parent.dk9_login_or_update_cache_on_start()
        self.close()


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
        advanced_search_fields = PartFields(
            part=case_folded_or_none(self.ui.inp_name.text()),
            brand=case_folded_or_none(self.ui.inp_manuf.text()),
            model=case_folded_or_none(self.ui.inp_model.text()),
            note=case_folded_or_none(self.ui.inp_descr.text()),
        )
        # {'type': self.ui.inp_name.text(),
        # 'manufacturer': self.ui.inp_manuf.text(),
        # 'model': self.ui.inp_model.text(),
        # 'description': self.ui.inp_descr.text()}
        self.Parent.dk9_search_start_worker(advanced_search_fields=advanced_search_fields)
