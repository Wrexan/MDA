import os
import xlrd


# from MDA_content.windows import Messages as M


class Price:
    # 0: 'Не загружен', 1: 'Не найден', 2: 'Загрузка',
    # 3: 'Ошибка загрузки', 4: 'Чтение', 5: 'Ошибка чтения'
    S_NOT_LOADED, S_NOT_FOUND, S_LOADING, S_LOADING_ERROR, S_READING, S_READING_ERROR, S_OK = 0, 1, 2, 3, 4, 5, 6

    def __init__(self, C):
        self.C = C
        # self.PATH: str = C.PATH
        # self.PRICE_PATH: str = C.PRICE_PATH
        # self.PRICE_PARTIAL_NAME: tuple = C.PRICE_PARTIAL_NAME
        # self.PRICE_TRASH_IN_CELLS: set = C.PRICE_TRASH_IN_CELLS
        self.NAME = ''
        # self.message = ''
        self.DB = None
        self.APPROVED = C.APPROVED or self.approve()

    def load_price(self, progress, status, error) -> None:
        status.emit(self.S_READING)
        price_path_name, name = '', ''
        try:
            for name in os.listdir(self.C.PRICE_PATH):
                if name[-4:] == self.C.PRICE_PARTIAL_NAME[1] and self.C.PRICE_PARTIAL_NAME[0] in name:
                    price_path_name = f'{self.C.PRICE_PATH}{name}'
                    break
            if not price_path_name:
                for name in os.listdir(self.C.PATH):
                    if name[-4:] == self.C.PRICE_PARTIAL_NAME[1] and self.C.PRICE_PARTIAL_NAME[0] in name:
                        price_path_name = f'{self.C.PATH}{name}'
                        break
            if price_path_name:
                self.NAME = name
                self.DB = xlrd.open_workbook(price_path_name, formatting_info=True)
                status.emit(self.S_OK)
                print(f'Price loaded: {price_path_name}')
            else:
                status.emit(self.S_NOT_FOUND)
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
            error.emit((f'Error {type(_err)=} while trying to load price:', _err))
            print(f'Error while trying to load price: {_err}')

    def approve(self):
        if self.DB:
            try:
                for sheet in self.DB:
                    if sheet.name == 'Samsung':
                        return True
            except Exception as err:
                print(f'Price is wrong or damaged: {err}')
        return False

    @staticmethod
    def get_row_in_pos(position: tuple):
        return position[0].row_values(position[1], 0, 7)  # position[1], 0, 9
        # ['Xiaomi Mi A2 M1804D2SG ', '', '', 0.0, '', '', '', '', '']

    def search_price_models(self, search_req: str, MODEL_LIST_SIZE: int, SMART_SEARCH: bool, STRICT_SEARCH: bool):
        search_req_len = len(search_req)
        models = {}  # {manufacturer: {model: [sheet, ruw_num],...}...}
        # print(self.DB.sheets())
        if not self.DB:
            return
        try:
            for sheet in self.DB:  # Lists cycle
                # print(f'{sheet=}')
                manufacturer = sheet.name
                if manufacturer in self.C.MANUFACTURER_BLACKLIST:
                    continue

                for row_num in range(sheet.nrows):  # Rows cycle
                    cell_value = sheet.row_values(row_num, 0, 3)
                    if not cell_value[0] or (cell_value[0] in self.C.PRICE_TRASH_IN_CELLS):
                        continue
                    # if SMART_SEARCH and (not cell_value or not cell_value[0] or len(cell_value) < 2
                    #                      or cell_value[0] in self.C.PRICE_TRASH_IN_CELLS):
                    #     continue
                    # print(f'{cell_value[0]}')
                    # print(f'{cell_value=}')
                    name_cell = str(cell_value[0]).strip().lower()
                    a, b, = 0, len(name_cell)
                    while a < b:
                        found_pos = name_cell.find(search_req, a, b)
                        # print(f'{a=} {b=} {found_pos=} {name_cell=}')
                        if found_pos == -1:
                            break
                        if manufacturer not in models:
                            models[manufacturer] = {}
                        # if search request > 3 symbols, cut everything from left
                        # for smaller, cut from both sides (more strict)
                        # print(f'{len(models)=} {models=} {name_cell=} {sheet=} {row_num=}')  # ERROR LOG
                        if SMART_SEARCH:
                            ok = False
                            if found_pos == 0 or name_cell[found_pos - 1] in "/\\ ":
                                ok = True
                            # elif (found_pos + search_req_len == b
                            #       or name_cell[found_pos + search_req_len] in '/\\ '
                            #       or search_req[-1] == ' ') \
                            #         and (search_req_len < 6 and found_pos > 0 and name_cell[found_pos - 1] not in '/\\ '):
                            #     ok = True
                            # if (search_req_len > 2  # and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
                            #         or (search_req_len < 3 and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
                            #             and (found_pos + search_req_len == b or
                            #                  name_cell[found_pos + search_req_len] in '/\\ ' or
                            #                  search_req[-1] == ' '))):
                            # le = len(models)
                            # print(f'{len(models)=} {models=} {name_cell=} {sheet=} {row_num=}')
                            if ok:
                                if len(models[manufacturer]) < MODEL_LIST_SIZE:
                                    models[manufacturer][name_cell] = [sheet, row_num, cell_value[2]]
                                if len(models[manufacturer]) >= MODEL_LIST_SIZE:
                                    return models
                                # print(f'=========={name_cell}==========')
                                break
                            else:
                                a += found_pos + search_req_len
                        else:
                            if len(models[manufacturer]) < MODEL_LIST_SIZE:
                                models[manufacturer][name_cell] = [sheet, row_num, cell_value[2]]
                            if len(models[manufacturer]) >= MODEL_LIST_SIZE:
                                # print(f'{models=}')
                                return models
                            break
            return models
        except Exception as err:
            print(f'Error while searching:\n{search_req}',
                  f'Found cells:\n{models}\n'
                  f'Message:\n{err}')
            # M.warning(f'Error while searching:\n{search_req}',
            #           f'Found cells:\n{models}\n'
            #           f'Message:\n{err}')
            return

    # def search_price_models(self, search_req: str, MODEL_LIST_SIZE: int, SMART_SEARCH: int):
    #     search_req_len = len(search_req)
    #     models = {}
    #     # print(self.DB.sheets())
    #     if not self.DB:
    #         return
    #     try:
    #         # if not self.APPROVED:
    #         #     for sheet in self.DB:
    #         #         if sheet.name == 'Samsung':
    #         #             self.APPROVED = True
    #         for sheet in self.DB:
    #             # print(f'{sheet=}')
    #             for row_num in range(sheet.nrows):
    #                 cell_value = sheet.row_values(row_num, 0, 2)
    #                 # print(f'{cell_value=} {len(cell_value)=}')
    #                 if SMART_SEARCH and (not cell_value or not cell_value[0] or len(cell_value) < 2
    #                                      or cell_value[0] in self.PRICE_TRASH_IN_CELLS):
    #                     continue
    #                 # print(f'{cell_value[0]}')
    #                 name_cell = str(cell_value[0]).strip().lower()
    #                 a, b, = 0, len(name_cell)
    #                 while a < b:
    #                     found_pos = name_cell.find(search_req, a, b)
    #                     # print(f'{a=} {b=} {found_pos=} {name_cell=}')
    #                     if found_pos == -1:
    #                         break
    #                     # if search request > 3 symbols, cut everything from left
    #                     # for smaller, cut from both sides (more strict)
    #                     # print(f'{len(self.models)=} {self.models=} {name_cell=} {sheet=} {row_num=}')  # ERROR LOG
    #                     if SMART_SEARCH:
    #                         ok = False
    #                         if found_pos == 0 or name_cell[found_pos - 1] in "/\\ ":
    #                             ok = True
    #                         # elif (found_pos + search_req_len == b
    #                         #       or name_cell[found_pos + search_req_len] in '/\\ '
    #                         #       or search_req[-1] == ' ') \
    #                         #         and (search_req_len < 6 and found_pos > 0 and name_cell[found_pos - 1] not in '/\\ '):
    #                         #     ok = True
    #                         # if (search_req_len > 2  # and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
    #                         #         or (search_req_len < 3 and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
    #                         #             and (found_pos + search_req_len == b or
    #                         #                  name_cell[found_pos + search_req_len] in '/\\ ' or
    #                         #                  search_req[-1] == ' '))):
    #                         # le = len(models)
    #                         # print(f'{len(models)=} {models=} {name_cell=} {sheet=} {row_num=}')
    #                         if ok:
    #                             if len(models) < MODEL_LIST_SIZE:
    #                                 models[name_cell] = [sheet, row_num]
    #                             if len(models) >= MODEL_LIST_SIZE:
    #                                 return models
    #                             # print(f'=========={name_cell}==========')
    #                             break
    #                         else:
    #                             a += found_pos + search_req_len
    #                     else:
    #                         if len(models) < MODEL_LIST_SIZE:
    #                             models[name_cell] = [sheet, row_num]
    #                         if len(models) >= MODEL_LIST_SIZE:
    #                             return models
    #                         break
    #         return models
    #     except Exception as err:
    #         print(f'Error while searching:\n{search_req}',
    #               f'Found cells:\n{models}\n'
    #               f'Message:\n{err}')
    #         # M.warning(f'Error while searching:\n{search_req}',
    #         #           f'Found cells:\n{models}\n'
    #         #           f'Message:\n{err}')
    #         return
