from PyQt5 import QtCore, QtWidgets
from datetime import datetime

from PyQt5.QtChart import QLineSeries, QChart, QChartView, QBarCategoryAxis, QSplineSeries, QPieSeries, \
    QPieSlice
from PyQt5.QtCore import QPointF, Qt, pyqtSlot
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

from UI.window_settings import Ui_settings_window
from UI.window_help import Ui_Dialog
from UI.adv_search import Ui_Dialog as AdvSearchDialog
from UI.window_graphs import Ui_Dialog as GraphDialog


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

        self.ui.cb_branch.addItems(self.C.BRANCHES.values())
        self.ui.cb_branch.setCurrentIndex(self.C.BRANCH)

        self.ui.chk_fullscreen.setCheckState(2 if C.FULLSCREEN else 0)
        self.ui.zebra_contrast.setValue(C.DK9_COL_DIFF)
        self.ui.tables_font_size.setValue(C.TABLE_FONT_SIZE)
        self.ui.colored_web_table.setCheckState(2 if C.DK9_COLORED else 0)
        self.ui.colored_price_table.setCheckState(2 if C.PRICE_COLORED else 0)
        self.ui.word_wrap_web_table.setCheckState(2 if C.WORD_WRAP_DK9 else 0)
        self.ui.word_wrap_price_table.setCheckState(2 if C.WORD_WRAP_PRICE else 0)

        self.ui.chb_show_exact.setCheckState(2 if C.FILTER_SEARCH_RESULT else 0)
        self.ui.chb_price_name_only.setCheckState(2 if C.SEARCH_BY_PRICE_MODEL else 0)
        self.ui.chb_search_eng.setCheckState(2 if C.LATIN_SEARCH else 0)
        self.ui.chb_search_narrow.setCheckState(2 if C.NARROW_SEARCH else 0)

        self.ui.income_overprice_perc.setValue(C.INCOME_PARTS_MARGIN_PERC)
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
        cbi = self.ui.cb_branch.currentIndex()
        self.C.BRANCH = cbi if self.C.BRANCHES.get(cbi) else 0

        self.C.FULLSCREEN = True if self.ui.chk_fullscreen.checkState() == 2 else False

        self.C.DK9_COL_DIFF = self.ui.zebra_contrast.value()
        self.C.TABLE_FONT_SIZE = self.ui.tables_font_size.value()
        self.C.DK9_COLORED = True if self.ui.colored_web_table.checkState() == 2 else False
        self.C.PRICE_COLORED = True if self.ui.colored_price_table.checkState() == 2 else False
        self.C.WORD_WRAP_DK9 = True if self.ui.word_wrap_web_table.checkState() == 2 else False
        self.C.WORD_WRAP_PRICE = True if self.ui.word_wrap_price_table.checkState() == 2 else False

        self.C.FILTER_SEARCH_RESULT = True if self.ui.chb_show_exact.checkState() == 2 else False
        self.C.SEARCH_BY_PRICE_MODEL = True if self.ui.chb_price_name_only.checkState() == 2 else False
        self.C.LATIN_SEARCH = True if self.ui.chb_search_eng.checkState() == 2 else False
        self.C.NARROW_SEARCH = True if self.ui.chb_search_narrow.checkState() == 2 else False

        self.C.INCOME_PARTS_MARGIN_PERC = self.ui.income_overprice_perc.value()
        # C.WIDE_MONITOR = True if self.ui.wide_monitor.checkState() == 2 else False
        # C.TABLE_COLUMN_SIZE_MAX = self.ui.column_width_max.value()
        if self.C.BRANCH == 0:
            self.Parent.reset_stat_timer()
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


class GraphWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.Parent = Parent
        self.ui = GraphDialog()
        self.ui.setupUi(self)

        self.graphs_menu = {
            0: 'График запросов',
            1: 'Топ запросов'
        }

        self.smooth_graph = True
        self.current_graph = 0
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.GRAPH_SELECTOR = self.ui.cb_graph
        self.GRAPH_LAYOUT = self.ui.graph_layout
        self.brand_quantity_by_days = {}

        self.configurate_on_load()

        self.draw_graph()

    def configurate_on_load(self):
        available_years = {str(year): year for year in range(2023, self.current_year + 1)}
        available_months = {str(month_name): month + 1 for month, month_name in
                            enumerate(['январь', 'февраль', 'март',
                                       'апрель', 'май', 'июнь',
                                       'июль', 'август', 'сентябрь',
                                       'октябрь', 'ноябрь', 'декабрь'])}

        self.ui.cb_year.addItems(available_years.keys())
        self.ui.cb_year.setCurrentText(str(self.current_year))
        self.ui.cb_year.currentIndexChanged.connect(self.draw_graph)

        self.ui.cb_month.addItems(available_months.keys())
        self.ui.cb_month.setCurrentText([k for k, v in available_months.items() if v == self.current_month][0])
        self.ui.cb_month.currentIndexChanged.connect(self.draw_graph)

        self.ui.cb_graph.addItems(self.graphs_menu.values())
        self.ui.cb_graph.setCurrentText(self.graphs_menu[0])
        self.ui.cb_graph.currentIndexChanged.connect(self.change_graph)

        self.ui.cb_smooth.stateChanged.connect(self.change_smooth)

        self.ui.rb_year.setChecked(False)
        self.ui.rb_month.setChecked(True)
        # self.ui.cb_by_branches.setDisabled(True)

    def draw_graph(self):
        stat_data = {'year': 2023, 'month': 2, 'days': {
            1: {
                'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]},
                'Samsung': {'A500': [1, 1, 0], 'M215': [1, 0, 3]},
                'Huawei': {'Y5 2020': [1, 0, 0], 'Nova': [1, 2, 0]}
            },
            2: {
                'Xiaomi': {'mi8': [1, 0, 3], 'mi11': [5, 2, 1]},
                'Samsung': {'A500': [1, 0, 0], 'M215': [1, 0, 0]},
                'Huawei': {'Y5 2020': [1, 0, 3], 'Nova': [1, 2, 0]}
            },
            3: {
                'Xiaomi': {'mi8': [0, 1, 1], 'mi11': [1, 3, 1]},
                'Samsung': {'A500': [1, 0, 4], 'M215': [1, 0, 0]}
            },
            4: {
                'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]},
                'Samsung': {'A500': [1, 1, 0], 'M215': [1, 0, 3]},
                'Huawei': {'Y5 2020': [1, 0, 1], 'Nova': [1, 2, 0]}
            },
            5: {
                'LG': {'V700': [1, 0, 2], 'M320': [2, 0, 1]},
                'Xiaomi': {'mi8': [1, 0, 3], 'mi11': [2, 2, 1]},
                'Samsung': {'A500': [1, 0, 0], 'M215': [1, 0, 0]},
                'Huawei': {'Y5 2020': [1, 0, 0], 'Nova': [1, 2, 0]},
                'iPhone': {'X': [1, 0, 3]}
            },
            6: {
                'Xiaomi': {'mi8': [0, 1, 4], 'mi11': [1, 3, 1]},
                'Samsung': {'A500': [1, 2, 0], 'M215': [1, 0, 0]},
                'Huawei': {'Y5 2020': [1, 0, 3], 'Nova': [1, 2, 0]}
            },
            7: {
                'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]},
                'Samsung': {'A500': [1, 1, 0], 'M215': [1, 0, 3]},
                'Huawei': {'Y5 2020': [1, 0, 0], 'Nova': [1, 2, 0], 'Nova 2': [1, 2, 5], 'Nova 3c': [1, 2, 0]}
            },
            8: {
                'Xiaomi': {'mi8': [1, 0, 3], 'mi11': [5, 2, 1], 'Redmi Note 11 Pro Plus': [3, 0, 1]},
                'Samsung': {'A500': [1, 0, 0], 'M215': [1, 2, 0]},
                'Huawei': {'Y5 2020': [1, 0, 3], 'Nova': [0, 2, 0], 'Nova 5t': [0, 2, 0]}
            },
            9: {
                'Xiaomi': {'mi8': [0, 1, 1], 'mi11': [1, 3, 1]},
                'Samsung': {'A500': [1, 0, 4], 'M215': [3, 0, 0]},
                'OnePlus': {'Nord N200 5G': [1, 0, 2], 'OnePlus 9 Pro': [3, 0, 0]}
            },
            10: {
                'Xiaomi': {'mi8': [1, 2, 3], 'mi11': [5, 0, 1]},
                'Samsung': {'A500': [1, 1, 0], 'M215': [1, 1, 3]},
                'Huawei': {'Y5 2020': [1, 0, 1], 'Nova': [1, 5, 0]}
            },
            11: {
                'Xiaomi': {'mi8': [1, 0, 3], 'mi11': [2, 2, 1]},
                'Samsung': {'A500': [1, 0, 0], 'M215': [1, 0, 0]},
                'Huawei': {'Y5 2020': [1, 0, 0], 'Nova': [1, 2, 0]}
            },
            12: {
                'Xiaomi': {'mi8': [0, 1, 4], 'mi11': [1, 3, 1]},
                'Samsung': {'A500': [1, 2, 0], 'M215': [1, 0, 3]},
                'Huawei': {'Y5 2020': [1, 0, 3], 'Nova': [1, 2, 0]}
            }}}

        self.brand_quantity_by_days = {}
        for day, brand_stat in stat_data['days'].items():
            self.brand_quantity_by_days[day] = \
                {model: sum(sum(v) for v in quantity.values()) for model, quantity in brand_stat.items()}

        if self.current_graph == 0:
            self.draw_line_chart()
        if self.current_graph == 1:
            self.draw_donut_breakdown(stat_data)

    def change_graph(self):
        graph = self.GRAPH_SELECTOR.currentIndex()
        self.current_graph = graph
        self.draw_graph()

    def change_smooth(self):
        self.smooth_graph = True if self.ui.cb_smooth.checkState() == 2 else False
        self.draw_graph()

    @staticmethod
    def get_rgb_by_name(name):
        brand_lower = name.lower()
        g = 2 if len(name) >= 3 else -1
        return \
            int((ord(brand_lower[1]) - 97) * 9.8), \
            int((ord(brand_lower[g]) - 97) * 9.8), \
            int((ord(brand_lower[0]) - 97) * 9.8)

    def draw_line_chart(self):

        # unpacked_data = {'year': 2023, 'month': 1, 31: {
        #     'Xiaomi': {
        #         'mi8': [1, 2, 3],
        #         'mi11': [5, 0, 1]
        #     },
        #     'Samsung': {
        #         'A500': [1, 0, 0],
        #         'M215': [1, 0, 0]
        #     }}}

        max_requests = 0

        # print(f'{brand_quantity_by_days=}')

        brand_series = {}
        for day, brands in self.brand_quantity_by_days.items():
            for brand in brands.keys():
                if brands[brand] > max_requests:
                    max_requests = brands[brand]
                if not brand_series.get(brand):
                    if self.smooth_graph:
                        brand_series[brand] = QSplineSeries()
                    else:
                        brand_series[brand] = QLineSeries()
                    brand_series[brand].setName(brand)
                    brand_series[brand].setPen(QColor(*self.get_rgb_by_name(brand)))

        for day, brand_stat in self.brand_quantity_by_days.items():
            for brand, series in brand_series.items():
                if brand in brand_stat.keys():
                    brand_series[brand].append(day, brand_stat[brand])
                else:
                    brand_series[brand].append(day, 0)

        # self.series = QLineSeries()
        # # self.series.setPen(QPen(Qt.darkGreen, 2))
        # self.series.setPen(QColor(100, 100, 200))
        # # self.series.setBrush(Qt.green)
        # self.series.setName('123')
        # self.series.setPointsVisible(True)

        self.chart = QChart()
        # self.chart.legend().hide()
        for series in brand_series.values():
            self.chart.addSeries(series)
        self.chart.createDefaultAxes()
        self.chart.setTitle("Количество запросов по бренду в день")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(200)

        axis_y_length = (max_requests // 5) * 5 + 5
        axis_y = self.chart.axisY()
        axis_y.setRange(0, axis_y_length)
        axis_y.setTickCount(axis_y_length + 1)

        # categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        # cat_axis = QBarCategoryAxis()
        # cat_axis.append(categories)
        #
        # # self.chart.createDefaultAxes()
        # self.chart.setAxisX(cat_axis)
        # # self.chart.addAxis(cat_axis, Qt.AlignBottom)
        # # self.series.attachAxis(axis)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        # self.setCentralWidget(self._chart_view)
        self.GRAPH_LAYOUT.addChildWidget(self._chart_view)
        width = 1236
        height = 656
        self._chart_view.resize(width, height)

    def draw_donut_breakdown(self, stat_data):
        min_requests = 3

        donut_breakdown = DonutBreakdownChart()
        donut_breakdown.setAnimationOptions(QChart.AllAnimations)
        donut_breakdown.setAnimationDuration(100)
        donut_breakdown.setTitle("Соотношение запросов за месяц")
        donut_breakdown.legend().setAlignment(Qt.AlignRight)

        brands_models_stats = {}
        for day, brands in stat_data['days'].items():
            for brand, models in brands.items():
                if not brands_models_stats.get(brand):
                    brands_models_stats[brand] = {}
                for model, stats in models.items():
                    if not brands_models_stats[brand].get(model):
                        brands_models_stats[brand][model] = 0
                    brands_models_stats[brand][model] += sum(stats)

        # print(f'{brands_models_stats=}')
        brands_models_series = {}
        for brand, models_stat in brands_models_stats.items():
            brands_models_series[brand] = QPieSeries()
            brands_models_series[brand].setName(brand)
            # brands_models_series[brand].setPen(QColor(*self.get_rgb_by_name(brand)))
            for model, stat in models_stat.items():
                if stat < min_requests:
                    continue
                brands_models_series[brand].append(model, stat)
            donut_breakdown.add_breakdown_series(brands_models_series[brand], QColor(*self.get_rgb_by_name(brand)))

        chart_view = QChartView(donut_breakdown)
        chart_view.setRenderHint(QPainter.Antialiasing)

        # self.setCentralWidget(self._chart_view)
        self.GRAPH_LAYOUT.addChildWidget(chart_view)
        width = 1236
        height = 656
        chart_view.resize(width, height)


class DonutBreakdownChart(QChart):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags())
        self.main_series = QPieSeries()
        self.main_series.setPieSize(0.5)
        self.addSeries(self.main_series)

    def add_breakdown_series(self, breakdown_series, color):
        font = QFont("Arial", 8)

        # add breakdown series as a slice to center pie
        main_slice = MainSlice(breakdown_series)
        main_slice.set_name(breakdown_series.name())
        main_slice.setValue(breakdown_series.sum())
        self.main_series.append(main_slice)

        # customize the slice
        main_slice.setBrush(color)
        main_slice.setLabelVisible()
        main_slice.setLabelColor(Qt.white)
        main_slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)
        main_slice.setLabelFont(font)

        # position and customize the breakdown series
        breakdown_series.setPieSize(0.6)
        breakdown_series.setHoleSize(0.5)
        breakdown_series.setLabelsVisible()

        for pie_slice in breakdown_series.slices():
            color = QColor(color).lighter(115)
            pie_slice.setBrush(color)
            pie_slice.setLabelFont(font)
            label_arm_len = -0.10 + len(pie_slice.label())/20
            if label_arm_len > 0.6:
                label_arm_len = 0.6
            pie_slice.setLabelArmLengthFactor(label_arm_len)

        # add the series to the chart
        self.addSeries(breakdown_series)

        # recalculate breakdown donut segments
        self.recalculate_angles()

        # update customize legend markers
        self.update_legend_markers()

    def recalculate_angles(self):
        angle = 0
        slices = self.main_series.slices()
        for pie_slice in slices:
            breakdown_series = pie_slice.get_breakdown_series()
            breakdown_series.setPieStartAngle(angle)
            angle += pie_slice.percentage() * 360.0  # full pie is 360.0
            breakdown_series.setPieEndAngle(angle)

    def update_legend_markers(self):
        # go through all markers
        for series in self.series():
            markers = self.legend().markers(series)
            for marker in markers:
                if series == self.main_series:
                    # hide markers from main series
                    marker.setVisible(False)
                else:
                    # modify markers from breakdown series
                    label = marker.slice().label()
                    p = marker.slice().percentage() * 100
                    marker.setLabel(f"{label} {p:.2f}%")
                    marker.setFont(QFont("Arial", 8))


class MainSlice(QPieSlice):
    def __init__(self, breakdown_series, parent=None):
        super().__init__(parent)

        self.breakdown_series = breakdown_series
        self.name = None

        self.percentageChanged.connect(self.update_label)

    def get_breakdown_series(self):
        return self.breakdown_series

    def set_name(self, name):
        self.name = name

    def name(self):
        return self.name

    def update_label(self):
        p = self.percentage() * 100
        self.setLabel(f"{self.name} {p:.2f}%")
