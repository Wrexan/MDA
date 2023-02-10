from datetime import datetime
from PyQt5 import QtCore, QtWidgets

from PyQt5.QtChart import QLineSeries, QChart, QChartView, QSplineSeries, QPieSeries, \
    QPieSlice, QBarSet, QPercentBarSeries, QBarCategoryAxis, QAbstractAxis, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush

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
            0: 'Топ за весь период',
            1: 'График по количеству',
            2: 'График в процентах'
        }

        self.min_req_limit = 3
        self.smooth_graph = True
        self.current_graph = 0

        self.GRAPH_SELECTOR = self.ui.cb_graph
        self.GRAPH_LAYOUT = self.ui.graph_layout
        self.brand_quantity_by_points = {}
        self.stat_data = None
        self.current_chart_view = None

        self.graph_loaders = {
            'month': self.MDAS.load_month_statistic,
            'year': self.MDAS.load_year_statistic,
        }
        self.current_graph_loader = self.graph_loaders['month']

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

        self.ui.rb_year.clicked.connect(self.load_year_graph)
        self.ui.rb_month.clicked.connect(self.load_month_graph)

        self.ui.sb_min.setValue(self.min_req_limit)
        self.ui.sb_min.valueChanged.connect(self.update_graph)
        # self.ui.cb_by_branches.setDisabled(True)

    def load_month_graph(self):
        if self.current_graph_loader != self.graph_loaders['month']:
            self.current_graph_loader = self.graph_loaders['month']
            self.reload_draw_graph()

    def load_year_graph(self):
        if self.current_graph_loader != self.graph_loaders['year']:
            self.current_graph_loader = self.graph_loaders['year']
            self.reload_draw_graph()

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

        self.stat_data = self.current_graph_loader(self.year_to_show, self.month_to_show)
        self.update_graph()

    def update_graph(self):
        graph = self.GRAPH_SELECTOR.currentIndex()
        self.current_graph = graph
        self.smooth_graph = True if self.ui.cb_smooth.checkState() == 2 else False
        self.min_req_limit = self.ui.sb_min.value()
        self.draw_graph()

    def draw_graph(self):
        if not self.stat_data:
            self.stat_data = self.current_graph_loader(self.year_to_show, self.month_to_show)

        if not self.stat_data or not self.stat_data['points']:
            return

        self.brand_quantity_by_points = {}
        for point, brand_stat in self.stat_data['points'].items():
            self.brand_quantity_by_points[int(point)] = \
                {model: sum(sum(v) for v in quantity.values()) for model, quantity in brand_stat.items()}
            # _unsorted_model_quantity = \
            #     {model: sum(sum(v) for v in quantity.values()) for model, quantity in brand_stat.items()}
            # self.brand_quantity_by_points[int(point)] = \
            #     dict(sorted(_unsorted_model_quantity.items(), key=lambda x: x[1], reverse=True))
        # print(f'{self.brand_quantity_by_points=}')

        if self.current_chart_view:
            self.GRAPH_LAYOUT.removeWidget(self.current_chart_view)

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
        if self.current_graph == 2:
            self.ui.sb_min.setVisible(False)
            self.ui.lbl_min.setVisible(False)
            self.ui.cb_smooth.setVisible(False)
            self.draw_percent_bar_chart()

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

        # print(f'{brand_quantity_by_points=}')

        brand_series = {}
        for point, brands in self.brand_quantity_by_points.items():
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
                    brand_series[brand].hovered.connect(self.show_tip_line)
                    # brand_series[brand].setPen(QColor(*self.get_rgb_by_name(brand)))
                    # brand_series[brand].setPointsVisible(True)

        for point, brand_stat in self.brand_quantity_by_points.items():
            for brand, series in brand_series.items():
                if brand in brand_stat.keys():
                    reqs = brand_stat[brand]
                else:
                    reqs = 0
                brand_series[brand].append(point, reqs)
                if not self.smooth_graph:
                    brand_series[brand].setPointsVisible(True)

        # self.series = QLineSeries()
        # # self.series.setPen(QPen(Qt.darkGreen, 2))
        # self.series.setPen(QColor(100, 100, 200))
        # # self.series.setBrush(Qt.green)
        # self.series.setName('123')
        # self.series.setPointsVisible(True)

        chart = QChart()
        # self.chart.legend().hide()
        for series in brand_series.values():
            chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle(f"Количество запросов по бренду за "
                       f"{self.available_months[self.month_to_show]} "
                       f"{self.year_to_show}")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAnimationDuration(200)

        axis_y_length = (max_requests // 5) * 5 + 5
        axis_y = chart.axisY()
        axis_y.setRange(0, axis_y_length)
        axis_y.setTickCount(axis_y_length + 1)
        axis_y.setLabelFormat("%i")

        axis_x_length = self.stat_data['period_length']
        axis_x = chart.axisX()
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

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.current_chart_view = QChartView(chart)
        self.current_chart_view.setRenderHint(QPainter.Antialiasing)

        # self.setCentralWidget(self._chart_view)
        self.GRAPH_LAYOUT.addChildWidget(self.current_chart_view)
        width = 1236
        height = 656
        self.current_chart_view.resize(width, height)

    def draw_donut_breakdown(self, stat_data):
        donut_breakdown = DonutBreakdownChart()
        # donut_breakdown.setAnimationOptions(QChart.AllAnimations)
        # donut_breakdown.setAnimationDuration(100)
        donut_breakdown.setTitle(f"Соотношение кол-ва запросов за весь "
                                 f"{self.available_months[self.month_to_show]} "
                                 f"{self.year_to_show}")
        donut_breakdown.legend().setAlignment(Qt.AlignRight)

        brands_models_stats = {}
        for point, brands in stat_data['points'].items():
            for brand, models in brands.items():
                if not brands_models_stats.get(brand):
                    brands_models_stats[brand] = {'overall_quantity': 0, 'models': {}}
                for model, stats in models.items():
                    if not brands_models_stats[brand]['models'].get(model):
                        brands_models_stats[brand]['models'][model] = 0
                    model_quantity = sum(stats)
                    brands_models_stats[brand]['models'][model] += model_quantity
                    brands_models_stats[brand]['overall_quantity'] += model_quantity
        for brand, brand_stats in brands_models_stats.items():
            # print(f'{brands_models_stats[brand]["models"]=}')
            brands_models_stats[brand]['models'] = \
                dict(sorted(brand_stats['models'].items(), key=lambda x: x[1], reverse=True))
        brands_models_stats = \
            dict(sorted(brands_models_stats.items(), key=lambda x: x[1]['overall_quantity'], reverse=True))
        # print(f'{brands_models_stats=}')

        # print(f'{brands_models_stats=}')
        brands_models_series = {}
        for brand, models_stat in brands_models_stats.items():
            brands_models_series[brand] = QPieSeries()
            brands_models_series[brand].setName(brand)
            # brands_models_series[brand].hovered.connect(donut_breakdown.show_tip)
            brands_models_series[brand].hovered.connect(self.show_tip)
            # brands_models_series[brand].setPen(QColor(*self.get_rgb_by_name(brand)))
            for model, stat in models_stat['models'].items():
                if stat < self.min_req_limit:
                    continue
                brands_models_series[brand].append(model, stat)
            donut_breakdown.add_breakdown_series(
                brands_models_series[brand], QColor(*self.get_rgb_by_name(brand)))

        self.current_chart_view = QChartView(donut_breakdown)
        self.current_chart_view.setRenderHint(QPainter.Antialiasing)

        # self.setCentralWidget(self._chart_view)
        self.GRAPH_LAYOUT.addChildWidget(self.current_chart_view)
        width = 1236
        height = 656
        self.current_chart_view.resize(width, height)

    def draw_percent_bar_chart(self):
        brand_series = {}
        # brush = QBrush()
        for point in range(1, self.stat_data['period_length'] + 1):
            brands = self.brand_quantity_by_points.get(point)
            if brands:
                # for point, brands in self.brand_quantity_by_points.items():
                for brand in brands.keys():
                    if not brand_series.get(brand):
                        brand_series[brand] = QBarSet(brand)
                        # brand_series[brand].setName(brand)
                        # brush.setColor(QColor(*self.get_rgb_by_name(brand)))
                        brand_series[brand].setBrush(QColor(*self.get_rgb_by_name(brand)))
                        brand_series[brand].setLabel(brand)
                        brand_series[brand].hovered.connect(self.show_tip_bar)
            else:
                self.brand_quantity_by_points[point] = {}

        for point in range(1, self.stat_data['period_length'] + 1):
            brand_stat = self.brand_quantity_by_points.get(point)
        #     if brand_stat:
        # for point, brand_stat in self.brand_quantity_by_points.items():
            # if brand_stat:
            for brand, series in brand_series.items():
                if brand in brand_stat.keys():
                    reqs = brand_stat[brand]
                else:
                    reqs = 0
                brand_series[brand].append(float(reqs))

        series = QPercentBarSeries()
        # print(f'{len(brand_series.values())=}')
        for series_set in brand_series.values():
            series.append(series_set)

        chart = QChart()
        chart.addSeries(series)
        # chart.createDefaultAxes()
        chart.setTitle(f"Соотношение запросов по бренду за "
                       f"{self.available_months[self.month_to_show]} "
                       f"{self.year_to_show}")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAnimationDuration(200)

        # axis_y_length = 100
        # axis_y = chart.axisY()
        # axis_y.setRange(0, axis_y_length)
        # axis_y.setTickCount(axis_y_length + 1)
        # axis_y.setLabelFormat("%i")

        axis_x_length = 31
        axis_x = QValueAxis()
        axis_x.setRange(1, axis_x_length)
        axis_x.setTickCount(axis_x_length + 1)
        axis_x.setLabelFormat("%i")
        chart.setAxisX(axis_x)

        # categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        # axis = QBarCategoryAxis()
        # axis.append(categories)
        # chart.createDefaultAxes()
        # chart.addAxis(axis, Qt.AlignBottom)
        # series.attachAxis(axis)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.current_chart_view = QChartView(chart)
        self.current_chart_view.setRenderHint(QPainter.Antialiasing)

        self.GRAPH_LAYOUT.addChildWidget(self.current_chart_view)
        width = 1236
        height = 656
        self.current_chart_view.resize(width, height)

    def show_tip_line(self, state):
        part = self.sender()
        if state:
            # part.setColor(part.color().darker(150))
            self.setToolTip(part.name())
        else:
            # part.setColor(part.color().lighter(150))
            self.setToolTip('')

    def show_tip_bar(self, state):
        part = self.sender()
        if state:
            part.setColor(part.color().darker(150))
            self.setToolTip(f'{part.label()} - {int(part.sum())} шт')
        else:
            part.setColor(part.color().lighter(150))
            self.setToolTip('')

    def show_tip(self, part, state):
        if state:
            # self.setToolTip(f'{part.label()} {(part.percentage() * 100):.1f}%')
            self.setToolTip(f'{part.label()} - {int(part.value())} шт')
            part.setBrush(part.color().darker(150))
        else:
            self.setToolTip('')
            part.setBrush(part.color().lighter(150))


class DonutBreakdownChart(QChart):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags())
        self.main_series = QPieSeries()
        self.main_series.setPieSize(0.5)
        self.main_series.hovered.connect(self.show_tip)
        self.addSeries(self.main_series)

    def show_tip(self, part, state):
        if state:
            self.setToolTip(part.label())
            part.setBrush(part.color.darker(150))
        else:
            self.setToolTip('')
            part.setBrush(part.color)

    def add_breakdown_series(self, breakdown_series, color):
        font = QFont("Arial", 8)

        # add breakdown series as a slice to center pie
        main_slice = MainSlice(breakdown_series)
        main_slice.set_name(breakdown_series.name())
        main_slice.setValue(breakdown_series.sum())
        self.main_series.append(main_slice)

        # customize the slice
        main_slice.color = color
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
            # pie_slice.setLabel(f'{pie_slice.label()} {pie_slice.percentage()}')
            # pie_slice.setLabel(f'{pie_slice.label()} {pie_slice.percentage():.1f}%')
            color = QColor(color).lighter(105)
            pie_slice.color = color
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
        self.update_legend_markers(breakdown_series)

    def recalculate_angles(self):
        angle = 0
        slices = self.main_series.slices()
        for pie_slice in slices:
            breakdown_series = pie_slice.get_breakdown_series()
            breakdown_series.setPieStartAngle(angle)
            angle += pie_slice.percentage() * 360.0  # full pie is 360.0
            breakdown_series.setPieEndAngle(angle)

    def update_legend_markers(self, model_quantity):
        # go through all markers
        for series in self.series():
            markers = self.legend().markers(series)
            for marker in markers:
                if series == self.main_series:
                    # hide markers from main series
                    marker.setVisible(False)
                else:
                    p = marker.slice().percentage() * 100
                    if p < 10:
                        marker.setVisible(False)
                        continue
                    # modify markers from breakdown series
                    slice = marker.slice()
                    # print(f'{self.main_series.children()[0].name=}')

                    # brand_name = series.name()
                    # brand_percent = 0
                    # for child_series in self.main_series.children():
                    #     if child_series.name == brand_name:
                    #         brand_percent = child_series.percentage()
                    #         # print(f'{brand_percent=}')
                    #         continue
                    # # print(f'{series.name()=}')
                    # # print(f'{series.percentage()=}')
                    # p = marker.slice().percentage() * brand_percent * 100
                    # if p < 5:
                    #     marker.setVisible(False)
                    #     continue
                    # marker.setLabel(f"{label} {p:.1f}%")
                    # print(f'{series.count()=} {series.sum()=}  {series.name()} {label}')
                    # print(f'{marker.slice().value()}')
                    # print(f'{series.chart()=} {series.children()=} {series.slices()=} ')
                    marker.setLabel(f"{int(slice.value())} шт {slice.label()}")
                    marker.setFont(QFont("Arial", 10, 75))


class MainSlice(QPieSlice):
    def __init__(self, breakdown_series, parent=None):
        super().__init__(parent)

        self.breakdown_series = breakdown_series
        self.name = None
        self.color = None

        self.percentageChanged.connect(self.update_label)

    def get_breakdown_series(self):
        return self.breakdown_series

    def set_name(self, name):
        self.name = name

    def name(self):
        return self.name

    def update_label(self):
        p = self.percentage() * 100
        self.setLabel(f"{self.name} {p:.1f}%")
