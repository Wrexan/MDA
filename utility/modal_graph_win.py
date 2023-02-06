from datetime import datetime
from PyQt5 import QtCore, QtWidgets

from PyQt5.QtChart import QLineSeries, QChart, QChartView, QSplineSeries, QPieSeries, \
    QPieSlice
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from UI.window_graphs import Ui_Dialog as GraphDialog


class GraphWindow(QtWidgets.QDialog):
    def __init__(self, C, Parent, MDAS):
        super().__init__(None,
                         # QtCore.Qt.WindowSystemMenuHint |
                         # QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowCloseButtonHint
                         )
        self.Parent = Parent
        self.MDAS = MDAS
        self.ui = GraphDialog()
        self.ui.setupUi(self)

        self.year_current = datetime.now().year
        self.month_current = datetime.now().month
        self.year_to_show = self.year_current
        self.month_to_show = self.month_current
        self.available_years = {str(year): year for year in range(2023, self.year_to_show + 1)}
        self.available_months = {month + 1: str(month_name) for month, month_name in
                                 enumerate(['январь', 'февраль', 'март',
                                            'апрель', 'май', 'июнь',
                                            'июль', 'август', 'сентябрь',
                                            'октябрь', 'ноябрь', 'декабрь'])}

        self.graphs_menu = {
            0: 'Топ запросов',
            1: 'График запросов'
        }

        self.min_req_limit = 3
        self.smooth_graph = True
        self.current_graph = 0

        self.GRAPH_SELECTOR = self.ui.cb_graph
        self.GRAPH_LAYOUT = self.ui.graph_layout
        self.brand_quantity_by_days = {}
        self.stat_data = None

        self.configurate_on_load()

        self.draw_graph()

    def configurate_on_load(self):
        self.ui.cb_year.addItems(self.available_years.keys())
        self.ui.cb_year.setCurrentText(str(self.year_to_show))
        self.ui.cb_year.currentIndexChanged.connect(self.reload_draw_graph)

        self.ui.cb_month.addItems(self.available_months.values())
        self.ui.cb_month.setCurrentText(self.available_months[self.month_to_show])
        self.ui.cb_month.currentIndexChanged.connect(self.reload_draw_graph)

        self.ui.cb_graph.addItems(self.graphs_menu.values())
        self.ui.cb_graph.setCurrentText(self.graphs_menu[0])
        self.ui.cb_graph.currentIndexChanged.connect(self.update_graph)

        self.ui.cb_smooth.stateChanged.connect(self.update_graph)

        self.ui.rb_year.setChecked(False)
        self.ui.rb_month.setChecked(True)

        self.ui.sb_min.setValue(self.min_req_limit)
        self.ui.sb_min.valueChanged.connect(self.update_graph)
        # self.ui.cb_by_branches.setDisabled(True)

    def reload_draw_graph(self):
        self.year_to_show = int(self.ui.cb_year.currentText())
        self.month_to_show = self.ui.cb_month.currentIndex() + 1
        # go back from future to now
        if self.year_to_show > self.year_current \
                or self.year_to_show == self.year_current and self.month_to_show > self.month_current:
            self.year_to_show = self.year_current
            self.month_to_show = self.month_current
            # self.ui.cb_year.setCurrentText(str(self.year_to_show))
            # self.ui.cb_month.setCurrentText([k for k, v in self.available_months.items() if v == self.month_to_show][0])

        self.stat_data = self.MDAS.load_statistic(self.year_to_show, self.month_to_show)
        self.update_graph()

    def update_graph(self):
        graph = self.GRAPH_SELECTOR.currentIndex()
        self.current_graph = graph
        self.smooth_graph = True if self.ui.cb_smooth.checkState() == 2 else False
        self.min_req_limit = self.ui.sb_min.value()
        self.draw_graph()

    def draw_graph(self):
        if not self.stat_data:
            self.stat_data = self.MDAS.load_statistic(self.year_to_show, self.month_to_show)

        if not self.stat_data['days']:
            return

        self.brand_quantity_by_days = {}
        for day, brand_stat in self.stat_data['days'].items():
            self.brand_quantity_by_days[int(day)] = \
                {model: sum(sum(v) for v in quantity.values()) for model, quantity in brand_stat.items()}

        if self.current_graph == 0:
            self.ui.sb_min.setVisible(True)
            self.ui.lbl_min.setVisible(True)
            self.ui.cb_smooth.setVisible(False)
            self.draw_donut_breakdown(self.stat_data)
        if self.current_graph == 1:
            self.ui.sb_min.setVisible(False)
            self.ui.lbl_min.setVisible(False)
            self.ui.cb_smooth.setVisible(True)
            self.draw_line_chart()

    @staticmethod
    def get_rgb_by_name(name):
        brand_lower = name.lower()
        red = int((ord(brand_lower[0]) - 97) * 9.8)
        # g = 2 if len(name) >= 3 else -1
        # print(f'{red=}')
        # blue = 255 - red
        # green = int((ord(brand_lower[g]) - 97) * 9.8)
        # b = 1 if len(name) >= 3 else -1
        blue = int((ord(brand_lower[1]) - 97) * 9.8)
        green = int((ord(brand_lower[-1]) - 97) * 9.8)
        # green = int((ord(brand_lower[-1]) - 87) * 7.08)
        # print(f'{red=} {green=} {blue=} ')
        return red, green, blue

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

        pen = QPen()
        pen.setWidth(2)

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
                    pen.setColor(QColor(*self.get_rgb_by_name(brand)))
                    brand_series[brand].setPen(pen)
                    # brand_series[brand].setPen(QColor(*self.get_rgb_by_name(brand)))
                    # brand_series[brand].setPointsVisible(True)

        for day, brand_stat in self.brand_quantity_by_days.items():
            for brand, series in brand_series.items():
                if brand in brand_stat.keys():
                    reqs = brand_stat[brand]
                else:
                    reqs = 0
                brand_series[brand].append(day, reqs)
                if not self.smooth_graph:
                    brand_series[brand].setPointsVisible(True)

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
        self.chart.setTitle(f"Количество запросов по бренду за "
                            f"{self.available_months[self.month_to_show]} "
                            f"{self.year_to_show}")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(200)

        axis_y_length = (max_requests // 5) * 5 + 5
        axis_y = self.chart.axisY()
        axis_y.setRange(0, axis_y_length)
        axis_y.setTickCount(axis_y_length + 1)
        axis_y.setLabelFormat("%i")

        axis_x_length = 31
        axis_x = self.chart.axisX()
        axis_x.setRange(1, axis_x_length)
        axis_x.setTickCount(axis_x_length + 1)
        axis_x.setLabelFormat("%i")

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
        donut_breakdown = DonutBreakdownChart()
        # donut_breakdown.setAnimationOptions(QChart.AllAnimations)
        # donut_breakdown.setAnimationDuration(100)
        donut_breakdown.setTitle(f"Соотношение кол-ва запросов за "
                                 f"{self.available_months[self.month_to_show]} "
                                 f"{self.year_to_show}")
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
                if stat < self.min_req_limit:
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
            label_arm_len = -0.10 + len(pie_slice.label()) / 20
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
