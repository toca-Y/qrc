import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.qrcManage.demo.demo1 import PyRcc

# import utils.qrcManage.local
# import fir_last

rcc = PyRcc()
rcc.loadPy(r'fir_last.py')
static = rcc['static']


class MainUi(QFrame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        file = static.get_file('image/black-1.png')

        self.resize(640, 480)
        self.setWindowIcon(QIcon(':/static/logo.png'))

        # self.setBorderImage(':/static/image/background1.png')
        # self.setBorderImage(':/static/image/abc.png')
        # self.setBorderImage(':/static/image/abc.png')
        # self.setBorderImage(':/static/image/abc.png')
        self.setBorderImage(':/static/image/black-1.png')
    
    def setBorderImage(self, url):
        class_name = self.__class__.__name__
        self.setStyleSheet(
                """%s{
                    border-image: url(%s);
                    }""" % (class_name, url))


if __name__ == '__main__':
    """
    Main run
    """
    
    app = QApplication(sys.argv)
    
    ui = MainUi()
    ui.show()
    
    sys.exit(app.exec_())
