import os
import xlrd


# from MDA_content.windows import Messages as M


class Price:
    def __init__(self, C):
        self.PRICE_TRASH_IN_CELLS = C.PRICE_TRASH_IN_CELLS
        self.APPROVED = C.APPROVED
        self.message = ''
        self.DB = self._load_price(C.PATH, C.PRICE_PATH, C.PRICE_PARTIAL_NAME)
        print(f'{self.message}')

    def _load_price(self, PATH: str, PRICE_PATH: str, PRICE_PARTIAL_NAME: tuple):
        price_path_name, name = '', ''
        for name in os.listdir(PRICE_PATH):
            if name[-4:] == PRICE_PARTIAL_NAME[1] and PRICE_PARTIAL_NAME[0] in name:
                price_path_name = f'{PRICE_PATH}{name}'
                break
        if not price_path_name:
            for name in os.listdir(PATH):
                if name[-4:] == PRICE_PARTIAL_NAME[1] and PRICE_PARTIAL_NAME[0] in name:
                    price_path_name = f'{PATH}{name}'
                    break
        if price_path_name:
            self.message = name
            return xlrd.open_workbook(price_path_name, formatting_info=True)
        else:
            self.message = f'*{PRICE_PARTIAL_NAME[0]}*{PRICE_PARTIAL_NAME[1]} file not found'
            # self.ui.model_lable.setText('ОШИБКА! Файл "Прайс..xls" не найден')
            # self.ui.price_name.setText('Расположите файл "Прайс..xls" на рабочем столе')
            print(f'File not found:\n{PRICE_PARTIAL_NAME[0]}',
                  f'it must be on desktop or next to this app and have format:\n'
                  f'*{PRICE_PARTIAL_NAME[0]}*{PRICE_PARTIAL_NAME[1]}')
            # M.warning(f'File not found:\n{PRICE_PARTIAL_NAME[0]}',
            #           f'it must be on desktop or next to this app and have format:\n'
            #           f'*{PRICE_PARTIAL_NAME[0]}*{PRICE_PARTIAL_NAME[1]}')
            return None

    @staticmethod
    def get_row_in_pos(position: tuple):
        return position[0].row_values(position[1], 0, 9)  # ['Xiaomi Mi A2 M1804D2SG ', '', '', 0.0, '', '', '', '', '']

    def search_price_models(self, search_req: str, MODEL_LIST_SIZE: int, SMART_SEARCH: int):
        search_req_len = len(search_req)
        models = {}
        # print(self.DB.sheets())
        if not self.DB:
            return
        try:
            if not self.APPROVED:
                for sheet in self.DB:
                    if sheet.name == 'Samsung':
                        self.APPROVED = True
            for sheet in self.DB:
                # print(f'{sheet=}')
                for row_num in range(sheet.nrows):
                    cell_value = sheet.row_values(row_num, 0, 2)
                    # print(f'{cell_value=} {len(cell_value)=}')
                    if SMART_SEARCH and (not cell_value or not cell_value[0] or len(cell_value) < 2
                                         or cell_value[0] in self.PRICE_TRASH_IN_CELLS):
                        continue
                    # print(f'{cell_value[0]}')
                    name_cell = str(cell_value[0]).strip().lower()
                    a, b, = 0, len(name_cell)
                    while a < b:
                        found_pos = name_cell.find(search_req, a, b)
                        # print(f'{a=} {b=} {found_pos=} {name_cell=}')
                        if found_pos == -1:
                            break
                        # if search request > 3 symbols, cut everything from left
                        # for smaller, cut from both sides (more strict)
                        # print(f'{len(self.models)=} {self.models=} {name_cell=} {sheet=} {row_num=}')  # ERROR LOG
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
                                if len(models) < MODEL_LIST_SIZE:
                                    models[name_cell] = [sheet, row_num]
                                if len(models) >= MODEL_LIST_SIZE:
                                    return models
                                # print(f'=========={name_cell}==========')
                                break
                            else:
                                a += found_pos + search_req_len
                        else:
                            if len(models) < MODEL_LIST_SIZE:
                                models[name_cell] = [sheet, row_num]
                            if len(models) >= MODEL_LIST_SIZE:
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
