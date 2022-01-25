import sys
import xlrd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QSpacerItem, QSizePolicy
from window_main import Ui_MainWindow

# if __name__ == '__main__':
# app = QApplication(sys.argv)
# win = QMainWindow()
# ui = Ui_MainWindow()
# ui.setupUi(win)
# win.show()


strict_search = True
price_path = ''
price_file = 'price.xls'


# price = xlrd.open_workbook(price_path + price_file, formatting_info=True)

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        print(sys.path[0] + '\\' + price_path + price_file)
        self.price_db = xlrd.open_workbook(sys.path[0] + '\\' + price_path + price_file, formatting_info=True)
        self.models = {}
        self.ui = Ui_MainWindow()
        self.initUI()

    def initUI(self):
        # ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # text = self.input_search

        self.ui.input_search.textChanged[str].connect(self.search_price_models)
        self.ui.table_left.setHorizontalHeaderLabels(['Виды работ', 'Цена', 'Примечание'])
        self.ui.table_right.setHorizontalHeaderLabels(['Тип', 'Фирма', 'Модель',	'Примечание',
                                                      'Цена', 'К-во', 'Дата', 'Где'])
        # self.ui.scrollAreaWidgetContents.layout().addWidget(QPushButton('123'))

    def search_price_models(self, search_req):
        search_req_len = len(search_req)
        if search_req_len < 2: return
        search_req = search_req.lower()  # input('Введите модель: ').lower()
        # print(search_req)
        self.models = {}
        for sheet in self.price_db:
            for row_num in range(sheet.nrows):
                name_cell = str(sheet.row_values(row_num, 0, 1)[0]).strip().lower()
                a, b, = 0, len(name_cell)
                while a < b:
                    found_pos = name_cell.find(search_req, a, b)
                    # print(f'{a=} {b=} {found_pos=} {name_cell=}')
                    if found_pos == -1: break
                    if found_pos == 0 or name_cell[found_pos - 1] in "/\\ ": \
                            # and \
                        # (found_pos + search_req_len == b or
                        #  name_cell[found_pos + search_req_len] in '/\\ ' or
                        #  search_req[-1] == ' '):
                        # print(f'FOUND============={name_cell=}')

                        if len(self.models) < 5:
                            self.models[name_cell] = [sheet, row_num]
                            # print(f'{sheet=}')

                        # print(f'=========={name_cell}==========')
                        break
                    else:
                        a += found_pos + search_req_len
        self.upd_model_buttons()

    def upd_model_buttons(self):
        lay = self.ui.scrollAreaWidgetContents.layout()
        self.clear_layout(lay)

        le = len(self.models)
        for model in self.models.keys():
            print(self.models.get(model))
            b = QPushButton(model)
            b.clicked.connect(lambda: self.upd_price_table(self.models.get(model)))
            lay.addWidget(b)
            le -= 1
        # self.ui.scroll_models.setLayout(lay)

    def upd_price_table(self, position):
        for sheet in self.price_db:
            # print(f'{sheet=}')
            if sheet == position[0]:
                # for row in sheet.nrows:
                #     name_cell = str(sheet.row_values(row, 0, 1)[0]).strip().lower()
                #     a, b, = 0, len(name_cell)
                #     if name_cell == model:
                row = sheet.row_values(position[1], 0, 6)
                # print(f'{row=}')
                for i in range(position[1], sheet.nrows - 1):
                    print(row)
                    if i < sheet.nrows:
                        row = sheet.row_values(i + 1, 0, 6)
                        if row[0] != '':
                            return
                    else:
                        return


    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                # print(child.widget())
                child.widget().deleteLater()

    def take_price_repairs(self, sheet, row_num):
        row = sheet.row_values(row_num, 0, 6)
        for i in range(row_num, sheet.nrows - 1):
            print(row)
            if i < sheet.nrows:
                row = sheet.row_values(i + 1, 0, 6)
                if row[0] != '':
                    break
            else:
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
