import pyqtgraph as pg


class MyPlot(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setYRange(-60000, 60000, padding=0)

    def clear(self):
        self.ui.widget.canvas.ax.clear()
        self.ui.widget.canvas.draw()
        self.ui.widget_2.canvas.ax.clear()
        self.ui.widget_2.canvas.draw()
        self.ui.widget_3.canvas.ax.clear()
        self.ui.widget_3.canvas.draw()
        self.ui.widget_4.canvas.ax.clear()
        self.ui.widget_4.canvas.draw()


class Spec(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clear(self):
        self.ui.widget.canvas.ax.clear()
        self.ui.widget.canvas.draw()
        self.ui.widget_2.canvas.ax.clear()
        self.ui.widget_2.canvas.draw()
        self.ui.widget_3.canvas.ax.clear()
        self.ui.widget_3.canvas.draw()
        self.ui.widget_4.canvas.ax.clear()
        self.ui.widget_4.canvas.draw()
