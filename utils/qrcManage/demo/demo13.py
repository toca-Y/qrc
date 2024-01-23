import sys
import traceback

from PyQt5.Qt import *

from utils.qrcManage.setting import qrc

# qrc.load_cfg_py_rcc("test1.three")
# qrc.load_cfg_py_rcc("test1.two")
# qrc.load_cfg_py_rcc("first.last")
qrc.load_cfg_py_rcc("icon.icon")


class MainUi(QFrame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(QIcon(':/svg/行程.svg'))
        self.setBorderImage(':/svg/svg/list_自由活动.svg')
        
        self.resize(640, 480)
    
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
