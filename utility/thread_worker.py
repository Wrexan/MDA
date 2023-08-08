import sys
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject


class Worker(QThread):
    def __init__(self):
        """Creates worker for thread. Use add_task() to add method to execution queue."""
        super(Worker, self).__init__()
        self.queue: dict = {}
        self.max_priority: int = 0
        # self.args = args
        # self.kwargs = kwargs
        # self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress'] = self.signals.progress
        # self.kwargs['error'] = self.signals.error
        # self.kwargs['status'] = self.signals.status

    @staticmethod
    def get_signals():
        return WorkerSignals()

    def add_task(self, func, signals, priority: int = 0, *args, **kwargs):
        """Adds task to queue by priority.
        First will be executed all tasks with 0 priority, then with 1 and so on.
        Use priorities to run most important first when resolving thread concurrency."""
        if self.max_priority < priority:
            self.max_priority = priority
        if not self.queue.get(priority):
            self.queue[priority] = []
        # Add the callback to our kwargs
        kwargs['progress'] = signals.progress
        kwargs['error'] = signals.error
        kwargs['status'] = signals.status
        self.queue[priority].append({'func': func, 'args': args, 'signals': signals, 'kwargs': kwargs})
        # print(f'Add task with priority: {priority} |Queue: {self.queue}')

    @pyqtSlot()
    def run(self):

        # print('Starting worker')
        for priority in range(self.max_priority + 1):
            tasks = self.queue.get(priority)
            if tasks:
                for task in tasks:
                    func = task['func']
                    args = task['args']
                    kwargs = task['kwargs']
                    signals = task['signals']
                    try:
                        # print(f'-> thread[{priority}]: "{func.__name__}" running')
                        result = func(*args, **kwargs)
                        # print(f'<- thread[{priority}]: "{func.__name__}" finishing')
                    except Exception as _err:
                        print(f'Worker error: {_err}')
                        # traceback.print_exc()
                        # App.error(f'Error while executing thread using:\n{self.args}\n{self.kwargs}', err)
                        exc_type, value = sys.exc_info()[:2]
                        signals.error.emit((exc_type, value, _err))  # traceback.format_exc()))
                    else:
                        signals.result.emit(result)  # Return the result of the processing
                    finally:
                        # print(f'Worker finished')
                        signals.finished.emit()  # Done


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    status = pyqtSignal(int)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
