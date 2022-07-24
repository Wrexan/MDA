import sys
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject


class Worker(QThread):
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress'] = self.signals.progress
        self.kwargs['error'] = self.signals.error
        self.kwargs['status'] = self.signals.status

    @pyqtSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as _err:
            # traceback.print_exc()
            # App.error(f'Error while executing thread using:\n{self.args}\n{self.kwargs}', err)
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, _err))  # traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    status = pyqtSignal(int)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
