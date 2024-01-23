import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidget, QVBoxLayout, QApplication, QTableWidgetItem, QWidget, QFrame, QLabel, \
    QGridLayout, QPushButton, QToolTip

from utils.qrcManage.demo.demo1 import RCC
from utils.qrcManage.setting import ResourceCfg, qrc


class FileView(QFrame):
    _style = """
        FileView{
            margin: 2;
            border-radius: 6px;
            background-color: rgb(223, 246, 221);
        }
        QLabel#label_name{
            background-color: #123456;
            color: rgb(255, 255, 255);
            font: 7pt "微软雅黑";
            margin: 2;
        }
        QLabel#label_name:disabled{
            background-color: rgb(209, 209, 209);
            color: rgb(0, 0, 0);

        }
    """
    _fixedSize = 100, 100
    
    def __init__(self, file):
        self.file = str(file or '')
        super().__init__()
        self.load()
    
    def mousePressEvent(self, a0) -> None:
        child = self.childAt(a0.pos())
        if not child:
            return
        
        if child.objectName() == 'label_name' and child.isEnabled():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.file)
            child.setEnabled(False)
            old_text = child.text()
            child.setText('已复制!')
            
            QTimer.singleShot(2000, lambda: (child.setEnabled(True), child.setText(old_text)))
    
    def load(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        label_icon = QLabel(objectName="label_icon")
        label_name = QLabel(objectName="label_name")
        layout.addWidget(label_icon)
        layout.addWidget(label_name)
        label_icon.setAlignment(Qt.AlignCenter)
        label_name.setMaximumHeight(24)
        self.setStyleSheet(self._style)
        self.setFixedSize(*self._fixedSize)
        self.load_icon(label_icon, label_name, self.file)
    
    @classmethod
    def load_icon(cls, label_icon: QLabel, label_name: QLabel, file):
        file = str(file or '')
        
        p_file = Path(str(file))
        suffix = p_file.suffix
        label_icon.setToolTip(f'{file}')
        if suffix in ['.png', '.ico', '.svg']:
            pixmap = QIcon(file).pixmap(50, 50)
            label_icon.setPixmap(pixmap)
        else:
            label_icon.setText(suffix.upper())
        label_name.setText(f'{p_file.name}')
        label_name.setToolTip('点击复制')


class TWFiles(QTableWidget):
    _style = """
        TWFiles::item{
            border: 0;
        }
    """
    
    def __init__(self, files, filter_=None, col=6):
        super().__init__()
        self.files = files
        self.resize(720, 480)
        self.setShowGrid(False)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setDefaultSectionSize(FileView._fixedSize[0])
        self.verticalHeader().setDefaultSectionSize(FileView._fixedSize[1])
        self.setColumnCount(col)
        self.setStyleSheet(self._style)
        self.load_files()
    
    def load_files(self):
        cols = self.columnCount()
        self.setRowCount(len(self.files) // cols + 1)
        for index, file in enumerate(self.files):
            col = index % cols
            row = index // cols
            self.setCellWidget(row, col, FileView(file))


class QRCUiManager(QWidget):
    cfg_header = ['配置', '名称', 'RCC数量', 'RCC']
    rcc_header = ['RCC', '名称', '']
    resource_header = ['资源', '前缀', ]
    file_header = ['文件', '名称', '路径', ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._init_argument()
        self._init_setting()
        self._init_view()
    
    def _init_argument(self):
        self.layout_main = QVBoxLayout(self)
        self.top_frame = QFrame()
        self.top_layout = QGridLayout(self.top_frame)
        self.tw_info = QTableWidget()
        
        self.pb_open_sysFile = QPushButton('系统文件')
        self.pb_forward = QPushButton()
        self.pb_backward = QPushButton()
    
    def _init_setting(self):
        self.resize(640, 480)
        self.setWindowIcon(QIcon(':/qt-project.org/qmessagebox/images/qtlogo-64.png'))
        
        self.pb_forward.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/right-32.png'))
        self.pb_backward.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/left-32.png'))
        
        self.top_layout.setContentsMargins(2, 2, 2, 2)
        self.pb_open_sysFile.clicked.connect(self.slot_btn_open_sysFile)
    
    def _init_view(self):
        self.layout_main.addWidget(self.top_frame)
        self.layout_main.addWidget(self.tw_info)
        
        self.top_layout.addWidget(self.pb_open_sysFile, 0, 0, 1, 2)
        self.top_layout.addWidget(self.pb_backward, 1, 0, 1, 1)
        self.top_layout.addWidget(self.pb_forward, 1, 1, 1, 1)
    
    def load_cfg(self):
        header = self.cfg_header
        self.tw_info.setColumnCount(len(header))
        self.tw_info.clear()
        self.tw_info.setHorizontalHeaderLabels(header)
        for row, cfg in enumerate(qrc.list()):
            self.tw_info.insertRow(self.tw_info.rowCount())
            self.tw_info.setItem(row, 0, QTableWidgetItem())
            self.tw_info.setItem(row, 1, QTableWidgetItem(cfg.name))
            self.tw_info.setItem(row, 2, QTableWidgetItem(len(cfg.list()).__str__()))
    
    def load_rcc(self):
        pass
    
    def load_resource(self):
        pass
    
    def load_file(self):
        pass
    
    # SLOT
    # -/-//-/-/-//-/-//-/-/-/-/-/-/-/-/-/-/-/-/-//-/-/-/-/-/-/-//-//-/-/-/-/-/-//-/-/-/-/--/-/-/-//-/-/-/-/-/-/-/-//-/-/
    def slot_btn_open_sysFile(self):
        self.tw_files = TWFiles(RCC.list_resources('qt-project.org'))
        self.tw_files.show()


if __name__ == '__main__':
    """
    Main run
    """
    
    app = QApplication(sys.argv)
    
    ui = QRCUiManager()
    ui.show()
    ui.load_cfg()
    # print(RCC.list_resources())
    sys.exit(app.exec_())
