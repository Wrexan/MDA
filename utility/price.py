import os
import traceback
from enum import IntEnum

import xlrd
from xlrd import Book

from utility.config import PRICE_PATH, PRICE_PATH_ALT, PROJECT_PATH


class PriceColumns(IntEnum):
    model: int = 0
    work_type: int = 1
    price: int = 5
    compatible_model: int = 5
    compatible_part: int = 6
    note: int = 7


MAX_PRICE_COLUMNS = int(max(PriceColumns)) + 1


class Price:
    # 0: 'Не загружен', 1: 'Не найден', 2: 'Загрузка',
    # 3: 'Ошибка загрузки', 4: 'Чтение', 5: 'Ошибка чтения'
    S_NOT_LOADED, S_NOT_FOUND, S_LOADING, S_LOADING_ERROR, S_READING, S_READING_ERROR, S_OK = 0, 1, 2, 3, 4, 5, 6

    def __init__(self, C):
        self.C = C
        self.SMART_SEARCH: bool = False
        self.NAME: str = ''
        self.DB: Book or None = None
        self.APPROVED: bool = C.APPROVED or False
        self.BRANDS: list = []

    def load_price(self, progress, status, error) -> None:
        status.emit(self.S_READING)
        progress.emit(10)
        try:
            price_path_name, self.NAME = self.search_price_in_path_tuple((PRICE_PATH,
                                                                          PRICE_PATH_ALT,
                                                                          PROJECT_PATH))
            progress.emit(30)

            if price_path_name:
                progress.emit(50)
                self.DB = xlrd.open_workbook(price_path_name, formatting_info=True)
                self.BRANDS = self.get_brands()
                progress.emit(90)
                status.emit(self.S_OK)
                print(f'Price loaded: {price_path_name}')
            else:
                status.emit(self.S_NOT_FOUND)
                error.emit((f'File not found: "*{self.C.PRICE_PARTIAL_NAME[0]}*{self.C.PRICE_PARTIAL_NAME[1]}"',
                            f'{self.C.PRICE_ABSENT_ERROR_TEXT}'))
                # self.NAME = f'*{self.PRICE_PARTIAL_NAME[0]}*{self.PRICE_PARTIAL_NAME[1]} file not found'
                # self.ui.model_lable.setText('ОШИБКА! Файл "Прайс..xls" не найден')
                # self.ui.price_name.setText('Расположите файл "Прайс..xls" на рабочем столе')
                print(f'File not found:\n{self.C.PRICE_PARTIAL_NAME[0]}',
                      f'it must be on desktop or next to this app and have format:\n'
                      f'*{self.C.PRICE_PARTIAL_NAME[0]}*{self.C.PRICE_PARTIAL_NAME[1]}')
                # M.warning(f'File not found:\n{PRICE_PARTIAL_NAME[0]}',
                #           f'it must be on desktop or next to this app and have format:\n'
                #           f'*{PRICE_PARTIAL_NAME[0]}*{PRICE_PARTIAL_NAME[1]}')
                self.DB = None
        except Exception as _err:
            status.emit(self.S_READING_ERROR)
            error.emit((f'Error while trying to load price:\n'
                        f'{self.NAME}',
                        f'{traceback.format_exc()}'))

    def search_price_in_path_tuple(self, path_list: tuple):
        for path in path_list:
            if os.path.exists(path):
                for name in os.listdir(path):
                    if name[-4:] == self.C.PRICE_PARTIAL_NAME[1] and self.C.PRICE_PARTIAL_NAME[0] in name:
                        return os.path.join(path, name), name
        return None, None

    def get_brands(self):
        brands = []
        a = False
        if self.DB:
            try:
                for sheet in self.DB:
                    if sheet.name[0].isascii():
                        brands.append(sheet.name.casefold())
                    if sheet.name == 'Samsung':
                        a = True
            except Exception as err:
                print(f'Price file is wrong or damaged: {err}')
        if not a:
            raise AssertionError(f'Price file is wrong or damaged')
        self.C.APPROVED = True
        return brands

    # @staticmethod
    # def get_row_in_pos(sheet: Sheet, row_num: int):
    #     return sheet.row_values(row_num, 0, MAX_PRICE_COLUMNS)  # position[1], 0, 9
        # ['Xiaomi Mi A2 M1804D2SG ', '', '', 0.0, '', '', '', '', '']

    def search_price_models(self, search_req: str, MODEL_LIST_SIZE: int, exact: bool = False):
        search_req_len = len(search_req)
        models = {}  # {manufacturer: {model: [sheet, ruw_num],...}...}
        # print(f'{search_req=} {MODEL_LIST_SIZE=}')
        if not self.DB:
            return
        try:
            for sheet in self.DB:  # Lists cycle
                # print(f'{sheet=}')
                manufacturer = sheet.name
                if manufacturer in self.C.MANUFACTURER_BLACKLIST:
                    continue
                # if manufacturer in self.C.PRICE_SEARCH_COLUMN_NUMBERS.keys():
                #     compat_model_column = self.C.PRICE_SEARCH_COLUMN_NUMBERS[manufacturer][1]
                # else:
                #     compat_model_column = self.C.PRICE_SEARCH_COLUMN_NUMBERS['+'][1]
                # print(f'{compat_model_column=}')

                for row_num in range(sheet.nrows):  # Rows cycle
                    row_values = sheet.row_values(row_num, 0, 7)
                    row_values_len = len(row_values)
                    if not row_values or not row_values[0] or (row_values[0] in self.C.PRICE_TRASH_IN_CELLS):
                        continue
                    # print(f'{sheet.row_values(row_num, 0, 7)=}')
                    # if SMART_SEARCH and (not cell_value or not cell_value[0] or len(cell_value) < 2
                    #                      or cell_value[0] in self.C.PRICE_TRASH_IN_CELLS):
                    #     continue
                    # print(f'{cell_value[0]}')
                    # print(f'{cell_value=}')
                    name_cell = str(row_values[0]).strip().lower()
                    # print(f'{name_cell=}')
                    a, b, = 0, len(name_cell)
                    while a < b:
                        found_pos = name_cell.find(search_req, a, b)
                        if found_pos == -1:
                            break
                        # print(f'{a=} {b=} {found_pos=} {name_cell=} {manufacturer=}')
                        if exact and (found_pos > 1 and (
                                manufacturer in name_cell and found_pos > len(manufacturer) + 2
                        )):
                            break
                        # print(f'GOOD {name_cell=}')
                        if manufacturer not in models:
                            models[manufacturer] = {}
                        # Getting main model to redirect, if present
                        if PriceColumns.compatible_model < row_values_len:
                            compat_model_name = row_values[PriceColumns.compatible_model]
                            if isinstance(compat_model_name, str):
                                compat_model_name: str = compat_model_name.strip().lower()
                                # ru ru, en ru, ru en, en en  -  separating trash
                                if compat_model_name.startswith('см', 0, 2) \
                                        or compat_model_name.startswith('cм', 0, 2) \
                                        or compat_model_name.startswith('сm', 0, 2) \
                                        or compat_model_name.startswith('cm', 0, 2):
                                    compat_model_name = compat_model_name[2:].strip()
                            else:
                                compat_model_name = ''
                        else:
                            compat_model_name = ''
                        # print(f'{compat_model_name=}')
                        # print(f'{len(models)=} {models=} {name_cell=} {sheet=} {row_num=}')  # ERROR LOG
                        if self.SMART_SEARCH:
                            ok = False
                            if found_pos == 0 or name_cell[found_pos - 1] in "/\\ ":
                                ok = True
                            # print(f'{len(models)=} {models=} {name_cell=} {sheet=} {row_num=}')
                            if ok:
                                if len(models[manufacturer]) < MODEL_LIST_SIZE and name_cell:
                                    models[manufacturer][name_cell] = [sheet, row_num, compat_model_name]
                                # if len(models[manufacturer]) >= MODEL_LIST_SIZE:
                                #     return models
                                # print(f'=========={name_cell}==========')
                                break
                            else:
                                a += found_pos + search_req_len
                        else:
                            if len(models[manufacturer]) < MODEL_LIST_SIZE and name_cell:
                                models[manufacturer][name_cell] = [sheet, row_num, compat_model_name]
                            # if len(models[manufacturer]) >= MODEL_LIST_SIZE:
                            #     # print(f'{models=}')
                            #     return models
                            break
                # if manufacturer in models and models[manufacturer] == {}:
                #     del models[manufacturer]
            return models
        except Exception as err:
            print(f'Error while searching:  {search_req}\n',
                  f'Found cells:  {models}\n'
                  f'Message:  {err}\n'
                  f'VARS:  {manufacturer=} {name_cell=} {row_num=} {row_values=} {models[manufacturer]=}\n'
                  f'{traceback.format_exc()}')
            # M.warning(f'Error while searching:\n{search_req}',
            #           f'Found cells:\n{models}\n'
            #           f'Message:\n{err}')
            return
