from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication

from utils.qrcManage.setting import qrc
import sys

# from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
# from PyQt5.QtCore import *


class MainUi(QWidget):
    _style = """
        MainUi{
            border-image: url(:/static/image/black-1.png);
            background-color: #0000ff;
        }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first = qrc['first']
        last = first.loadPyRCC('last', first)
        last.loadPy()
        static = last['static']
        file = static.get_file('image/black-1.png')
        print(file.exists())
        self.setWindowIcon(QIcon(':/static/logo.png'))
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.setStyleSheet(self._style)
        self.resize(640, 480)
        self.start()
    
    def start(self):
        pass


if __name__ == '__main__':
    """
    Main run
    """
    
    app = QApplication(sys.argv)
    
    ui = MainUi()
    ui.show()
    
    sys.exit(app.exec_())
