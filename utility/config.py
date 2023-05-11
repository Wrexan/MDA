import os
import configparser
from win32comext.shell import shell, shellcon

from secured.confidential_data import *


class Config:
    FILTER_SEARCH_RESULT = None

    def __init__(self):
        self.error = None
        self.PATH = f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}\\'
        self.CONTENT_PATH = f'{self.PATH}content\\'
        self.MDAS_PATH = f'{self.PATH}mdas\\'
        self.LANG_PATH = f'{self.CONTENT_PATH}languages\\'

        self.LOGO = f'{self.CONTENT_PATH}MDA.ico'
        self.USER_CONFIG = f'{self.CONTENT_PATH}user_config.ini'

        self.CURRENT_LANG = 1
        self.LANGS: tuple
        self.upd_langs()
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
        self.SEARCH_BY_PRICE_MODEL = True
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

        self.INCOME_PARTS_MARGIN_PERC = 4

        # ====================PRICE====================
        self.PRICE_PATH = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\')
        self.PRICE_PATH_ALT = f'{shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)}\\'
        self.PRICE_GD_PATH = ''
        # self.PRICE_CONFIG = f'{self.CONTENT_PATH}price_config.ini'
        self.NARROW_SEARCH_LEN = 2  # start search from 2 symbols
        self.APPROVED = False
        self.PRICE_SEARCH_COLUMN_SYMBOLS = {'+': 'BFG',
                                            # 'Alcatel': 'BCDE',
                                            # 'Asus-тел': 'XBFG',
                                            'Asus-планш': 'BDG',
                                            # 'BlackBerry': 'ABCFG',
                                            # 'Blackview': 'XBEF',
                                            # 'Fly': 'XBCHI',
                                            # 'doogee': 'XBCDE',
                                            # 'HTC': 'BCEFH',
                                            # 'Huawei': 'XBGHIJ',
                                            # 'iPad': 'XAFGI',
                                            # 'iPhone': 'XBHI',
                                            # 'Lenovo': 'XBFGH',
                                            # 'LG': 'BCDI',
                                            # 'Meizu': 'XBEFG',
                                            # 'Motorola': 'XBJKQ',
                                            # 'Nokia': 'BCGHJ',
                                            # 'Nomi': 'XBCEF',
                                            # 'OPPO': 'BCFGH',
                                            # 'OnePlus': 'BCFGH',
                                            # 'Oukitel': 'BCFGL',
                                            # 'PIXEL': 'BCFGH',
                                            # 'Realme': 'BCFGH',
                                            # 'Samsung': 'BCGH',
                                            # 'Sony': 'XBFGH',
                                            # 'Tecno': 'BCFG',
                                            # 'vivo': 'BCDEF',
                                            # 'TP-Link': 'BCDE',
                                            # 'XIAOMI': 'XBFG',
                                            # 'ZTE': 'BCFGH',
                                            }
        self.PRICE_SEARCH_COLUMN_NUMBERS = {}
        self.convert_columns_to_nums()
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

        self.DK9_TABLE_NAMES = (' ЗАПЧАСТИ - ', ' АКСЕССУАРЫ - ')

        self.DK9_LOGIN, self.LOGIN = '', ''
        self.DK9_PASSWORD, self.PASSWORD = '', ''
        self.DK9_LOGIN_DATA = {}

        self.DK9_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Firefox/10.0'}

        # self.DK9_LOGIN_DATA = self.data()

        self.WEB_STATUSES = {0: 'Нет соединения', 1: 'Подключение...', 2: 'Подключен',
                             3: 'Перенаправление', 4: 'Запрос отклонен', 5: 'Ошибка сервера',
                             6: 'Ошибка авторизации', 7: 'Ошибка соединения'}

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
        self.HELP_FILE_PATH = f'{self.CONTENT_PATH}help_{self.LANGS[self.CURRENT_LANG].lower()}.txt'

    def upd_langs(self):
        self.LANGS = (*os.listdir(f'{self.LANG_PATH}'),)

    def set_error_signal(self, signal):
        self.error = signal

    def convert_columns_to_nums(self):
        for list_name, columns in self.PRICE_SEARCH_COLUMN_SYMBOLS.items():
            self.PRICE_SEARCH_COLUMN_NUMBERS[list_name] = *(ord(letter.upper()) - 65 for letter in columns),
        # print(self.PRICE_SEARCH_COLUMN_NUMBERS)

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
        config.read(self.USER_CONFIG)
        if 'SETTINGS' in config:
            print(f'Reading {self.USER_CONFIG}')
            try:
                self.DK9_LOGIN = config['WEB DATABASE']['DK9_LOGIN']
                self.DK9_PASSWORD = config['WEB DATABASE']['DK9_PASSWORD']
                self.CURRENT_LANG = int(config['CLIENT']['LANG'])
                self.BRANCH = int(config['CLIENT']['BRANCH'])
                self.FULLSCREEN = True if config['SETTINGS']['FULLSCREEN'] == 'True' else False
                # ALWAYS FALSE
                self.FILTER_SEARCH_RESULT = False
                # True if config['SETTINGS']['FILTER_SEARCH_RESULT'] == 'True' else False
                self.SEARCH_BY_PRICE_MODEL = True if config['SETTINGS']['SEARCH_BY_PRICE_MODEL'] == 'True' else False
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
                print(f'Error while trying to read/create config at:\n{self.USER_CONFIG}', _err)
                os.remove(self.USER_CONFIG)
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

    # def save_user_config(self):
    #     config = configparser.ConfigParser()
    #     config.add_section('WEB DATABASE')
    #     print(f'{config=} {type(config)=}')
    #     config.set('WEB DATABASE', 'dk9_login', str(self.DK9_LOGIN))
    #     config.set('WEB DATABASE', 'DK9_PASSWORD', str(self.DK9_PASSWORD))
    #     config.add_section('SETTINGS')
    #     config.set('SETTINGS', 'MODEL_LIST_SIZE', str(self.MODEL_LIST_SIZE))
    #     config.set('SETTINGS', 'PRICE_COLORED', str(self.PRICE_COLORED))
    #     config.set('SETTINGS', 'DK9_COLORED', str(self.DK9_COLORED))
    #     config.set('SETTINGS', 'DK9_COL_DIFF', str(self.DK9_COL_DIFF))
    #     config.set('SETTINGS', 'TABLE_FONT_SIZE', str(self.TABLE_FONT_SIZE))

    def save_user_config(self):
        print(f'Saving {self.USER_CONFIG}')
        config = configparser.ConfigParser()
        config['WEB DATABASE'] = {}
        config['WEB DATABASE']['DK9_LOGIN'] = str(self.DK9_LOGIN)
        config['WEB DATABASE']['DK9_PASSWORD'] = str(self.DK9_PASSWORD)

        config['CLIENT'] = {}
        config['CLIENT']['LANG'] = str(self.CURRENT_LANG)
        config['CLIENT']['BRANCH'] = str(self.BRANCH)

        config['SETTINGS'] = {}
        config['SETTINGS']['FULLSCREEN'] = str(self.FULLSCREEN)

        config['SETTINGS']['FILTER_SEARCH_RESULT'] = str(self.FILTER_SEARCH_RESULT)
        config['SETTINGS']['SEARCH_BY_PRICE_MODEL'] = str(self.SEARCH_BY_PRICE_MODEL)
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
            with open(self.USER_CONFIG, 'w') as conf:
                config.write(conf)
                print(f'Saved {self.USER_CONFIG}')
        except Exception as err:
            print(f'Error while trying to save config at:\n{self.USER_CONFIG}', err)
            # error.emit(f'Error while trying to save config at:\n{self.USER_CONFIG}', err)

    def r_data(self):
        return {
            'TextBoxName': self.LOGIN,
            'TextBoxPassword': self.PASSWORD,
            'ButtonLogin': 'Submit'
        }
