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


class MainUi(QFrame):
    # border-image: url(:/static/image/black-1.png);
    
    # _style = """
    #     MainUi{
    #         background-color: #0000ff;
    #     }
    # """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # first = qrc['first']
        print('000000000000000000000000')
        # last = first.loadPyRCC('last', first)
        print(len(last.list_resources()))
        
        print('000000000000000000000000')
        # last.loadPy()
        print('000000000000000000000000')
        static = last['static']
        print('000000000000000000000000')
        file = static.get_file('image/black-1.png')
        print('000000000000000000000000')
        # print(last.list_resources())
        print(len(last.list_resources()))
        print(file.exists())
        print(11111111111)
        self.setWindowIcon(QIcon(':/static/logo.png'))
        print(222222222222222)
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        print(33333333333333)
        # self.setStyleSheet(self._style)
        print(444444444444444)
        self.resize(640, 480)
        print(555555555555555555)
        self.setBorderImage(':/static/image/black-1.png')
        print(66666666666666666)
        # print('len.data: ', len(str(file.data())))
        # pixmap = file.pixmap()
        # print(pixmap.isNull())
        print(777777777777777777777)
        label = QLabel(self)
        label.resize(100, 100)
        # label.setPixmap(pixmap)
        label.setText('1111111111111111111111')
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
    
    # sys.exit(app.exec_())
