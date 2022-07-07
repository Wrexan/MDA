from PyQt5.QtWidgets import QMessageBox


class Messages:
    @staticmethod
    def warning(title: str, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(f'{title}\n\nMessage:  {str(msg)}')
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
