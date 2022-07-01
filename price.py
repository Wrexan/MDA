import os
import xlrd


class Price:
    def __init__(self, PRICE_PATH: str, PRICE_PARTIAL_NAME: tuple, PRICE_TRASH_IN_CELLS: tuple):
        self.PRICE_TRASH_IN_CELLS = PRICE_TRASH_IN_CELLS
        self.message = ''
        self.DB = self._load_price(PRICE_PATH, PRICE_PARTIAL_NAME)
        print(f'{self.message}')

    def _load_price(self, PRICE_PATH, PRICE_PARTIAL_NAME):
        price_name = ''
        for name in os.listdir(PRICE_PATH):
            if name[-4:] == PRICE_PARTIAL_NAME[1] and PRICE_PARTIAL_NAME[0] in name:
                price_name = name
                break
        if price_name:
            self.message = price_name
            return xlrd.open_workbook(PRICE_PATH + price_name, formatting_info=True)
        else:
            # self.ui.model_lable.setText('ОШИБКА! Файл "Прайс..xls" не найден')
            # self.ui.price_name.setText('Расположите файл "Прайс..xls" на рабочем столе')
            self.message = 'Расположите файл "Прайс..xls" на рабочем столе'
            return None

    def get_row_by_model(self, position: tuple):
        return position[0].row_values(position[1], 0, 9)  # ['Xiaomi Mi A2 M1804D2SG ', '', '', 0.0, '', '', '', '', '']

    def search_price_models(self, search_req: str, MODEL_LIST_SIZE: int):
        search_req_len = len(search_req)
        models = {}
        # print(self.PRICE_DB.sheets())
        for sheet in self.DB:
            # print(f'{sheet=}')
            for row_num in range(sheet.nrows):
                cell_value = sheet.row_values(row_num, 0, 2)
                # print(f'{cell_value=} {len(cell_value)=}')
                if not cell_value or not cell_value[0] or len(cell_value) < 2 \
                        or cell_value[0] in self.PRICE_TRASH_IN_CELLS:
                    continue
                # print(f'{cell_value[0]}')
                name_cell = str(cell_value[0]).strip().lower()
                a, b, = 0, len(name_cell)
                while a < b:
                    found_pos = name_cell.find(search_req, a, b)
                    # print(f'{a=} {b=} {found_pos=} {name_cell=}')
                    if found_pos == -1: break
                    # if search request > 3 symbols, cut everything from left
                    # for smaller, cut from both sides (more strict)
                    # print(f'{len(self.models)=} {self.models=} {name_cell=} {sheet=} {row_num=}')  # ERROR LOG
                    if (search_req_len > 2  # and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
                            or (search_req_len < 3 and (found_pos == 0 or name_cell[found_pos - 1] in "/\\ ")
                                and (found_pos + search_req_len == b or
                                     name_cell[found_pos + search_req_len] in '/\\ ' or
                                     search_req[-1] == ' '))):
                        # le = len(models)
                        # print(f'{len(models)=} {models=} {name_cell=} {sheet=} {row_num=}')
                        if len(models) < MODEL_LIST_SIZE:
                            models[name_cell] = [sheet, row_num]
                        if len(models) >= MODEL_LIST_SIZE:
                            return models

                        # print(f'=========={name_cell}==========')
                        break
                    else:
                        a += found_pos + search_req_len
        return models
