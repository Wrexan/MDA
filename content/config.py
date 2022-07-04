import os
import configparser


class Config:
    def __init__(self):
        self.user_config_name = 'user_config.ini'
        self.price_config_name = 'price_config.ini'

        # ====================MENU====================
        self.STRICT_SEARCH = 2
        self.LATIN_SEARCH = 2
        self.MODEL_LIST_REVERSED = False

        self.PATH = os.path.dirname(os.path.realpath(__file__))
        self.DK9_LOGIN = ''
        self.DK9_PASSWORD = ''

        self.MODEL_LIST_SIZE = 5

        # tables
        self.PRICE_COLORED = True  # work slower if True
        self.DK9_COLORED = True  # work slower if True
        self.DK9_COL_DIFF = 14  # difference of odd/even bg
        self.TABLE_FONT_SIZE = 12

        # ============================================
        # =============APP SETTINGS====================
        # ====================MENU====================
        self.STRICT_SEARCH = 2
        self.LATIN_SEARCH = 2
        self.MODEL_LIST_REVERSED = False
        # ====================PRICE====================
        self.STRICT_SEARCH_LEN = 2  # start search after 2 symbols
        self.PRICE_SEARCH_COLUMN_SYMBOLS = {'+': 'BCFGH',
                                            'Alcatel': 'BCDE',
                                            'Asus-тел': 'XBFG',
                                            'Asus-планш': 'XBDGH',
                                            'BlackBerry': 'ABCFG',
                                            'Blackview': 'XBEF',
                                            'Fly': 'XBCHI',
                                            'doogee': 'XBCDE',
                                            'HTC': 'BCEFH',
                                            'Huawei': 'XBGHIJ',
                                            'iPad': 'XAFGI',
                                            'iPhone': 'XBHI',
                                            'Lenovo': 'XBFGH',
                                            'LG': 'BCDI',
                                            'Meizu': 'XBEFG',
                                            'Motorola': 'XBJKQ',
                                            'Nokia': 'BCGHJ',
                                            'Nomi': 'XBCEF',
                                            'OPPO': 'BCFGH',
                                            'OnePlus': 'BCFGH',
                                            'Oukitel': 'BCFGL',
                                            'PIXEL': 'BCFGH',
                                            'Realme': 'BCFGH',
                                            'Samsung': 'BCGH',
                                            'Sony': 'XBFGH',
                                            'Tecno': 'BCFG',
                                            'vivo': 'BCDEF',
                                            'TP-Link': 'BCDE',
                                            'XIAOMI': 'XBFG',
                                            'ZTE': 'BCFGH',
                                            }
        self.PRICE_SEARCH_COLUMN_NUMBERS = {}
        self.convert_columns_to_nums()
        self.PRICE_TRASH_IN_CELLS = ('/', '\\', 'MI2/Mi2s', 'MI2a', 'mi3', 'Mi 9t', 'Mi Max 3',
                                     'Red rice', 'Redmi 3', 'Redmi 4x', 'Redmi 6', 'Redmi 7', 'Redmi 7a',
                                     'Redmi 8', 'Redmi 8a', 'Redmi Note 4', 'Redmi Note 5', 'Redmi Note 6',
                                     'Redmi Note 6 Pro', 'Redmi Note 7', 'Redmi Note 8', 'Redmi note 9', 'Redmi Note 6')
        self.PRICE_PATH = self.set_desktop_path()
        self.PRICE_PARTIAL_NAME = ('Прайс', '.xls')

        # ====================DK9====================
        # Preparing background colors for DK9
        self.DK9_BG_P_COLOR1 = (204, 204, 255)
        self.DK9_BG_P_COLOR2 = \
            (self.DK9_BG_P_COLOR1[0] - self.DK9_COL_DIFF if self.DK9_BG_P_COLOR1[0] >= self.DK9_COL_DIFF else 0,
             self.DK9_BG_P_COLOR1[1] - self.DK9_COL_DIFF if self.DK9_BG_P_COLOR1[1] >= self.DK9_COL_DIFF else 0,
             self.DK9_BG_P_COLOR1[2] - self.DK9_COL_DIFF if self.DK9_BG_P_COLOR1[2] >= self.DK9_COL_DIFF else 0)
        self.DK9_BG_A_COLOR1 = (204, 255, 153)
        self.DK9_BG_A_COLOR2 = \
            (self.DK9_BG_A_COLOR1[0] - self.DK9_COL_DIFF if self.DK9_BG_A_COLOR1[0] >= self.DK9_COL_DIFF else 0,
             self.DK9_BG_A_COLOR1[1] - self.DK9_COL_DIFF if self.DK9_BG_A_COLOR1[1] >= self.DK9_COL_DIFF else 0,
             self.DK9_BG_A_COLOR1[2] - self.DK9_COL_DIFF if self.DK9_BG_A_COLOR1[2] >= self.DK9_COL_DIFF else 0)

        self.DK9_BG_COLORS = {'GreenYellow': (173, 255, 47),
                              'LightBlue': (173, 216, 230),
                              'Goldenrod': (218, 165, 32),
                              'Red': (255, 80, 80),
                              }
        self.DK9_LOGIN_URL = "http://dimkak9-001-site1.htempurl.com/Login.aspx"
        self.DK9_SEARCH_URL = "http://dimkak9-001-site1.htempurl.com/AllInOne.aspx"
        self.DK9_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Firefox/10.0'}

        self.DK9_LOGIN_DATA = {
            'TextBoxName': self.DK9_LOGIN,
            'TextBoxPassword': self.DK9_PASSWORD,
            'ButtonLogin': 'Submit',
        }

        self.handle_config()

    def convert_columns_to_nums(self):
        for list_name, columns in self.PRICE_SEARCH_COLUMN_SYMBOLS.items():
            self.PRICE_SEARCH_COLUMN_NUMBERS[list_name] = *(ord(letter.upper())-65 for letter in columns),
        # print(self.PRICE_SEARCH_COLUMN_NUMBERS)

    @staticmethod
    def set_desktop_path():
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\')

    def handle_config(self):
        config = configparser.ConfigParser()
        config.read(f"{self.user_config_name}")
        if 'SETTINGS' in config:
            print(f'Reading {self.user_config_name}')
            self.DK9_LOGIN = config['WEB DATABASE']['DK9_LOGIN']
            self.DK9_PASSWORD = config['WEB DATABASE']['DK9_PASSWORD']
            self.MODEL_LIST_SIZE = int(config['SETTINGS']['MODEL_LIST_SIZE'])
            self.PRICE_COLORED = bool(config['SETTINGS']['PRICE_COLORED'])
            self.DK9_COLORED = bool(config['SETTINGS']['DK9_COLORED'])
            self.DK9_COL_DIFF = int(config['SETTINGS']['DK9_COL_DIFF'])
            self.TABLE_FONT_SIZE = int(config['SETTINGS']['TABLE_FONT_SIZE'])
        else:
            self.save_user_config()

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
        print(f'Saving {self.user_config_name}')
        config = configparser.ConfigParser()
        config['WEB DATABASE'] = {}
        config['WEB DATABASE']['DK9_LOGIN'] = str(self.DK9_LOGIN)
        config['WEB DATABASE']['DK9_PASSWORD'] = str(self.DK9_PASSWORD)
        config['SETTINGS'] = {}
        config['SETTINGS']['MODEL_LIST_SIZE'] = str(self.MODEL_LIST_SIZE)
        config['SETTINGS']['PRICE_COLORED'] = str(self.PRICE_COLORED)
        config['SETTINGS']['DK9_COLORED'] = str(self.DK9_COLORED)
        config['SETTINGS']['DK9_COL_DIFF'] = str(self.DK9_COL_DIFF)
        config['SETTINGS']['TABLE_FONT_SIZE'] = str(self.TABLE_FONT_SIZE)

        with open(self.user_config_name, 'w') as conf:
            config.write(conf)
            print(f'Saved {self.user_config_name}')