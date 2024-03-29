import os
import configparser
from enum import IntEnum

from win32comext.shell import shell, shellcon

from secured.confidential_data import *

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONTENT_PATH = os.path.join(PROJECT_PATH, 'content')
MDAS_PATH = os.path.join(PROJECT_PATH, 'mdas')
LANG_PATH = os.path.join(CONTENT_PATH, 'languages')
VERSION_FILE_PATH = os.path.join(CONTENT_PATH, 'version.md')

LOGO = os.path.join(CONTENT_PATH, 'MDA.ico')
USER_CONFIG_FILE_PATH = os.path.join(CONTENT_PATH, 'user_config.ini')
ERROR_FOLDER_PATH = os.path.join(CONTENT_PATH, 'Errors')
# ConnectTimeoutError
ERRORS_TO_IGNORE = '[Errno 110', '[WinError 10060]', 'timed out', 'Connection aborted'

PRICE_PATH = os.path.join(os.environ['USERPROFILE'], 'Desktop')
PRICE_PATH_ALT = f'{shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)}'
PRICE_GD_PATH = ''

DK9_CACHE_FILE_PATH = os.path.join(CONTENT_PATH, 'dk_tables.cache')


class Config:
    FILTER_SEARCH_RESULT = None

    def __init__(self):
        self.error = None
        # self.PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        # self.CONTENT_PATH = os.path.join(self.PATH, 'content')
        # self.MDAS_PATH = os.path.join(self.PATH, 'mdas')
        # self.LANG_PATH = os.path.join(self.CONTENT_PATH, 'languages')
        # self.VERSION_FILE_PATH = os.path.join(self.CONTENT_PATH, 'version.md')
        #
        # self.LOGO = os.path.join(self.CONTENT_PATH, 'MDA.ico')
        # self.USER_CONFIG = os.path.join(self.CONTENT_PATH, 'user_config.ini')
        # self.ERROR_FOLDER_PATH = os.path.join(self.CONTENT_PATH, 'Errors')

        self.CURRENT_LANG = 1
        self.LANGS: tuple = (*os.listdir(LANG_PATH),)
        self.HELP_FILE_PATH: str
        self.upd_help_file_path()

        # ===============================================================
        # =============  CONFIDENTIAL, SECURED DATA  ====================
        # ===============================================================
        self.MDAS_URL = MDAS_URL
        self.MDAS_KEY = MDAS_KEY
        self.MDAS_HEADER = MDAS_HEADER
        self.DK9_LOGIN_URL = DK9_LOGIN_URL
        self.DK9_LOGGED_IN_URL = DK9_LOGGED_IN_URL
        self.DK9_SEARCH_URL = DK9_SEARCH_URL
        self.UPDATE_URL = UPDATE_URL

        # =================================================
        # ==================  CLIENT  =====================
        # =================================================
        self.FIRST_START: bool = False
        self.BRANCH: int = 0
        self.BRANCHES: dict = \
            {
                0: '---',
                1: 'ДРН',
                2: 'ПЛТ',
                3: 'ПЗН',
            }
        self.STAT_CACHE_DELAY: int = 180_000  # 3 min
        self.STAT_RESEND_DELAY: int = 300_000  # 5 min
        self.stat_delay: int = 180_000  # 3 min by default, more on delivery fail
        self.STAT_CACHE_SIZE: int = 5

        # =================================================
        # ===============  APP SETTINGS  ==================
        # ====================  UI  =======================
        self.FULLSCREEN = False
        self.MODEL_LIST_MAX_SIZE = 20

        self.FILTER_SEARCH_RESULT = False  # filter, from start
        # self.SHOW_COMPATIBILITY = False
        self.NARROW_SEARCH = True  # from n symbols
        self.LATIN_SEARCH = True

        self.SHOW_DATE = False

        # tables
        self.PRICE_COLORED = True  # work slower if True
        self.DK9_COLORED = True  # work slower if True
        self.DK9_COL_DIFF = 16  # difference of odd/even bg
        self.TABLE_FONT_SIZE = 12
        self.SMALL_FONT_SIZE = 12
        self.WORD_WRAP_DK9 = False
        self.WORD_WRAP_PRICE = True

        self.SEARCH_HISTORY_LEN = 10

        self.INCOME_PARTS_MARGIN_PERC = 4

        # ====================PRICE====================
        # self.PRICE_CONFIG = f'{self.CONTENT_PATH}price_config.ini'
        self.NARROW_SEARCH_LEN = 2  # start search from 2 symbols
        self.APPROVED = False
        # self.PRICE_SEARCH_COLUMN_SYMBOLS = {'+': 'BFGH',
        #                                     # 'Alcatel': 'BCDE',
        #                                     # 'Asus-тел': 'XBFG',
        #                                     'Asus-планш': 'BDH',
        #                                     # 'BlackBerry': 'ABCFG',
        #                                     # 'Blackview': 'XBEF',
        #                                     # 'Fly': 'XBCHI',
        #                                     # 'doogee': 'XBCDE',
        #                                     # 'HTC': 'BCEFH',
        #                                     # 'Huawei': 'XBGHIJ',
        #                                     # 'iPad': 'XAFGI',
        #                                     # 'iPhone': 'XBHI',
        #                                     # 'Lenovo': 'XBFGH',
        #                                     # 'LG': 'BCDI',
        #                                     # 'Meizu': 'XBEFG',
        #                                     # 'Motorola': 'XBJKQ',
        #                                     # 'Nokia': 'BCGHJ',
        #                                     # 'Nomi': 'XBCEF',
        #                                     # 'OPPO': 'BCFGH',
        #                                     # 'OnePlus': 'BCFGH',
        #                                     # 'Oukitel': 'BCFGL',
        #                                     # 'PIXEL': 'BCFGH',
        #                                     # 'Realme': 'BCFGH',
        #                                     # 'Samsung': 'BCGH',
        #                                     # 'Sony': 'XBFGH',
        #                                     # 'Tecno': 'BCFG',
        #                                     # 'vivo': 'BCDEF',
        #                                     # 'TP-Link': 'BCDE',
        #                                     # 'XIAOMI': 'XBFG',
        #                                     # 'ZTE': 'BCFGH',
        #                                     }
        # self.PRICE_SEARCH_COLUMN_NUMBERS = PriceColumns
        # self.convert_columns_to_nums()
        self.PRICE_TRASH_IN_CELLS = ()
        # self.PRICE_TRASH_IN_CELLS = ('/', '\\', 'MI2/Mi2s', 'MI2a', 'mi3', 'Mi 9t', 'Mi Max 3',
        #                              'Red rice', 'Redmi 3', 'Redmi 4x', 'Redmi 6', 'Redmi 7', 'Redmi 7a',
        #                              'Redmi 8', 'Redmi 8a', 'Redmi Note 4', 'Redmi Note 5', 'Redmi Note 6',
        #                              'Redmi Note 6 Pro', 'Redmi Note 7', 'Redmi Note 8',
        #                              'Redmi note 9', 'Redmi Note 6')
        # self.NOT_FULL_MODEL_NAMES = ('ipad', 'iphone')  # ------------------------------------
        self.MODEL_NAME_BLACKLIST = ('телефон', 'планшет')
        self.MANUFACTURER_BLACKLIST = ('Alcatel', 'BlackBerry', 'Fly', 'HTC')
        self.PRICE_PARTIAL_NAME = ('Прайс', '.xls')

        self.PRICE_STATUSES = {0: 'Не загружен', 1: 'Не найден', 2: 'Загрузка',
                               3: 'Ошибка загрузки', 4: 'Чтение', 5: 'Ошибка чтения'}

        # Background colors for Price
        self.P_BG_COLOR1 = (255, 255, 255)
        self.P_BG_COLOR2 = (0, 0, 0)

        # ====================DK9====================
        # Preparing background colors for DK9
        self.DK9_BG_P_COLOR1 = (204, 204, 255)
        self.DK9_BG_P_COLOR2 = (0, 0, 0)
        self.DK9_BG_A_COLOR1 = (204, 255, 153)
        self.DK9_BG_A_COLOR2 = (0, 0, 0)
        self.precalculate_color_diffs()

        self.DK9_BG_COLOR_SEL_BY_PRICE = (240, 200, 240)
        self.DK9_BG_HOVER_COLOR = (250, 250, 250)

        self.DK9_BG_COLORS = {'GreenYellow': (173, 255, 47),
                              'LightBlue': (173, 216, 230),
                              'Goldenrod': (218, 165, 32),
                              'Red': (255, 80, 80),
                              }
        self.DK9_FG_COLOR_COMPATIBLE = (115, 25, 10)
        # self.DK9_FG_COLOR_COMPATIBLE = (10, 25, 115)
        # self.DK9_FG_COLOR_COMPATIBLE = (20, 115, 20)

        self.PB_STYLE_SHEET_DEFAULT = ""
        self.PB_STYLE_SHEET_WARN = "QProgressBar::chunk {background-color: orange;}"
        self.PB_STYLE_SHEET_ERROR = "QProgressBar::chunk {background-color: orangered;}"
        self.PB_STYLE_SHEET_FILE_READ = "QProgressBar::chunk {background-color: yellow;}"
        self.PB_STYLE_SHEET_FILE_WRITE = "QProgressBar::chunk {background-color: cyan;}"

        self.DK9_TABLE_NAMES = (' ЗАПЧАСТИ - ', ' АКСЕССУАРЫ - ')

        self.DK9_LOGIN, self.LOGIN = '', ''
        self.DK9_PASSWORD, self.PASSWORD = '', ''
        self.DK9_LOGIN_DATA = {}

        self.DK9_CACHING = True
        self.DK9_CACHING_PERIOD = 30  # 1_800_000 ms = 30 min * 60_000

        self.DK9_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Firefox/10.0'}

        # self.DK9_LOGIN_DATA = self.data()

        self.WEB_STATUSES = {0: 'Нет соединения', 1: 'Подключение...', 2: 'Подключен',
                             3: 'Перенаправление', 4: 'Запрос отклонен', 5: 'Ошибка сервера',
                             6: 'Не подключен', 7: 'Ошибка соединения', 8: 'Чтение',
                             9: 'Сохранение', 10: 'Ошибка чтения', 11: 'Ошибка сохранения',
                             12: 'Обновлено', 13: 'Обновлено', 14: 'Обновляется', 15: 'Ошибка авторизации'}

        self.SYMBOL_TO_LATIN = {
            'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p',
            'х': '[', 'ъ': ']',
            'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';',
            'э': "'",
            'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n', 'ь': 'm', 'б': ',', 'ю': '.',  # '.': '/',
            'ї': ']', 'і': 's', 'є': "'",
        }
        self.MDAS_DATA_HANDLE_MSGS = {
            'Data error':
                f'Data error\n'
                f'Receiving wrong data from server. Try to check statistic later.',
            'Connection error':
                f'Connection error\n'
                f'Server not responding. Try to check statistic later.'
        }

        # self.UPDATE_FOLDER = '1JauaFxPrsksy3cuYiQ-VKoz3tv2dpO0x'

        self.load_or_generate_config()

    def upd_help_file_path(self):
        self.HELP_FILE_PATH = os.path.join(CONTENT_PATH, f'help_{self.LANGS[self.CURRENT_LANG].lower()}.txt')

    def set_error_signal(self, signal):
        self.error = signal

    # def convert_columns_to_nums(self):
    #     for list_name, columns in self.PRICE_SEARCH_COLUMN_SYMBOLS.items():
    #         self.PRICE_SEARCH_COLUMN_NUMBERS[list_name] = *(ord(letter.upper()) - 65 for letter in columns),
    #     # print(self.PRICE_SEARCH_COLUMN_NUMBERS)

    def get_color_from_style(self, style):
        return self.DK9_BG_COLORS[style[style.find(':') + 1: style.find(';')]]

    # @staticmethod
    # def set_desktop_path():
    #     return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\')

    def precalculate_color_diffs(self):
        self.P_BG_COLOR2 = self._precalculate_color_diff(self.P_BG_COLOR1)
        self.DK9_BG_P_COLOR2 = self._precalculate_color_diff(self.DK9_BG_P_COLOR1)
        self.DK9_BG_A_COLOR2 = self._precalculate_color_diff(self.DK9_BG_A_COLOR1)

    def _precalculate_color_diff(self, color: tuple):
        return \
            (color[0] - self.DK9_COL_DIFF if color[0] >= self.DK9_COL_DIFF else 0,
             color[1] - self.DK9_COL_DIFF if color[1] >= self.DK9_COL_DIFF else 0,
             color[2] - self.DK9_COL_DIFF if color[2] >= self.DK9_COL_DIFF else 0)

    def load_or_generate_config(self):
        config = configparser.ConfigParser()
        config.read(USER_CONFIG_FILE_PATH)
        if 'SETTINGS' in config:
            print(f'Reading {USER_CONFIG_FILE_PATH}')
            try:
                self.DK9_LOGIN = config['WEB DATABASE']['DK9_LOGIN']
                self.DK9_PASSWORD = config['WEB DATABASE']['DK9_PASSWORD']
                self.DK9_CACHING = True if config['WEB DATABASE']['DK9_CACHING'] == 'True' else False
                self.DK9_CACHING_PERIOD = int(config['WEB DATABASE']['DK9_CACHING_PERIOD'])

                self.CURRENT_LANG = int(config['CLIENT']['LANG'])
                self.BRANCH = int(config['CLIENT']['BRANCH'])
                self.FULLSCREEN = True if config['SETTINGS']['FULLSCREEN'] == 'True' else False
                # ALWAYS FALSE
                self.FILTER_SEARCH_RESULT = False
                # True if config['SETTINGS']['FILTER_SEARCH_RESULT'] == 'True' else False
                # self.SEARCH_BY_PRICE_MODEL = True if config['SETTINGS']['SEARCH_BY_PRICE_MODEL'] == 'True' else False
                # self.SHOW_COMPATIBILITY = True if config['SETTINGS']['SHOW_COMPATIBILITY'] == 'True' else False
                self.LATIN_SEARCH = True if config['SETTINGS']['LATIN_SEARCH'] == 'True' else False
                self.NARROW_SEARCH = True if config['SETTINGS']['NARROW_SEARCH'] == 'True' else False

                self.PRICE_COLORED = True if config['SETTINGS']['PRICE_COLORED'] == 'True' else False
                self.DK9_COLORED = True if config['SETTINGS']['DK9_COLORED'] == 'True' else False
                self.DK9_COL_DIFF = int(config['SETTINGS']['DK9_COL_DIFF'])
                self.TABLE_FONT_SIZE = int(config['SETTINGS']['TABLE_FONT_SIZE'])
                self.WORD_WRAP_DK9 = True if config['SETTINGS']['WORD_WRAP_DK9'] == 'True' else False
                self.WORD_WRAP_PRICE = True if config['SETTINGS']['WORD_WRAP_PRICE'] == 'True' else False

                self.INCOME_PARTS_MARGIN_PERC = int(config['SETTINGS']['INCOME_PARTS_MARGIN_PERC'])
                # self.WIDE_MONITOR = True if config['SETTINGS']['WIDE_MONITOR'] == 'True' else False
                # self.TABLE_COLUMN_SIZE_MAX = int(config['SETTINGS']['TABLE_COLUMN_SIZE_MAX'])
                # self.DK9_LOGIN_DATA = self.data()
            except Exception as _err:
                print(f'Error while trying to read/create config at:\n{USER_CONFIG_FILE_PATH}', _err)
                os.remove(USER_CONFIG_FILE_PATH)
                self.save_user_config()
        else:
            self.FIRST_START = True
            self.save_user_config()

    def c_data(self):
        return {
            'TextBoxName': self.DK9_LOGIN,
            'TextBoxPassword': self.DK9_PASSWORD,
            'ButtonLogin': 'Submit'
        }

    def save_user_config(self):
        print(f'Saving {USER_CONFIG_FILE_PATH}')
        config = configparser.ConfigParser()
        config['WEB DATABASE'] = {}
        config['WEB DATABASE']['DK9_LOGIN'] = str(self.DK9_LOGIN)
        config['WEB DATABASE']['DK9_PASSWORD'] = str(self.DK9_PASSWORD)
        config['WEB DATABASE']['DK9_CACHING'] = str(self.DK9_CACHING)
        config['WEB DATABASE']['DK9_CACHING_PERIOD'] = str(self.DK9_CACHING_PERIOD)

        config['CLIENT'] = {}
        config['CLIENT']['LANG'] = str(self.CURRENT_LANG)
        config['CLIENT']['BRANCH'] = str(self.BRANCH)

        config['SETTINGS'] = {}
        config['SETTINGS']['FULLSCREEN'] = str(self.FULLSCREEN)

        config['SETTINGS']['FILTER_SEARCH_RESULT'] = str(self.FILTER_SEARCH_RESULT)
        # config['SETTINGS']['SEARCH_BY_PRICE_MODEL'] = str(self.SEARCH_BY_PRICE_MODEL)
        # config['SETTINGS']['SHOW_COMPATIBILITY'] = str(self.SHOW_COMPATIBILITY)
        config['SETTINGS']['LATIN_SEARCH'] = str(self.LATIN_SEARCH)
        config['SETTINGS']['NARROW_SEARCH'] = str(self.NARROW_SEARCH)

        config['SETTINGS']['PRICE_COLORED'] = str(self.PRICE_COLORED)
        config['SETTINGS']['DK9_COLORED'] = str(self.DK9_COLORED)
        config['SETTINGS']['DK9_COL_DIFF'] = str(self.DK9_COL_DIFF)
        config['SETTINGS']['TABLE_FONT_SIZE'] = str(self.TABLE_FONT_SIZE)
        config['SETTINGS']['WORD_WRAP_DK9'] = str(self.WORD_WRAP_DK9)
        config['SETTINGS']['WORD_WRAP_PRICE'] = str(self.WORD_WRAP_PRICE)

        config['SETTINGS']['INCOME_PARTS_MARGIN_PERC'] = str(self.INCOME_PARTS_MARGIN_PERC)

        self.DK9_LOGIN_DATA = self.c_data()
        try:
            with open(USER_CONFIG_FILE_PATH, 'w') as conf:
                config.write(conf)
                print(f'Saved {USER_CONFIG_FILE_PATH}')
        except Exception as err:
            print(f'Error while trying to save config at:\n{USER_CONFIG_FILE_PATH}', err)
            # error.emit(f'Error while trying to save config at:\n{USER_CONFIG_FILE_PATH}', err)

    def r_data(self):
        return {
            'TextBoxName': self.LOGIN,
            'TextBoxPassword': self.PASSWORD,
            'ButtonLogin': 'Submit'
        }
