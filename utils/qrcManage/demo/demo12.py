import traceback

from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QFrame
import sys, os

from utils.qrcManage.demo.demo1 import PyRcc

print(os.getcwd(), 333333333333333333333)
print('\n'.join(sys.path))
sys.path.append('E:\\casuallyToDo')
from utils.qrcManage.setting import qrc

from PyQt5.QtGui import *
from PyQt5.QtCore import *

rcc = PyRcc()
rcc.loadPy(r'fir_last.py')
last = rcc


def exists():
    try:
        # from PyQt5.QtCore import QFile
        return QFile(srcPath).exists()
    except:
        traceback.print_exc()


class MainUi(QFrame):
    # border-image: url(:/static/image/black-1.png);
    
    # _style = """
    #     MainUi{
    #         background-color: #0000ff;
    #     }
    # """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # print(len(last.list_resources()))
        
        # static = last['static']
        # file = static.get_file('image/black-1.png')
        print(len(last.list_resources()))
        print(exists())
        self.setWindowIcon(QIcon(':/static/logo.png'))
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.resize(640, 480)
        self.setBorderImage(':/static/image/black-1.png')
        
        label = QLabel()
        # label.resize(100, 100)
        # label.setText('1111111111111111111111')
        print(' __init__, end ')
    
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
