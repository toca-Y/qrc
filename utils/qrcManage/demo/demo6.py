import sys
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QTableWidget, QGridLayout, QPushButton, QApplication, QHBoxLayout, \
    QTabWidget, QLabel, QTableWidgetItem, QAbstractItemView, QMessageBox, QFileDialog

from utils.qrcManage.demo.demo4 import TWFiles
from utils.qrcManage.demo.demo7 import InfoGet, TreeShow
from utils.qrcManage.error_model import *
from utils.qrcManage.setting import qrc, defaultCfg, ResourceCfg, defaultRcc, cfg_list

qrc.load_cfg_all_py_rcc(defaultCfg.name, ignore_error=True)
printExc.enable = False
button_fields = {
    'copy'  : ':/config/static/copy.svg',
    'jumpto': ':/config/static/jumpto.svg',
}

# print(qrc.load_cfg_py_rcc("icon.icon"))


class BaseFrame(QFrame):
    
    def __init__(self):
        super().__init__()
        
        self._init_argument()
        self._init_setting()
        self._init_view()
    
    def _init_argument(self):
        pass
    
    def _init_setting(self):
        pass
    
    def _init_view(self):
        pass
    
    @classmethod
    def add_clipboardText(cls, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    @classmethod
    def get_clipboardText(cls):
        clipboard = QApplication.clipboard()
        da = clipboard.mimeData()
        return da.text()
    
    @classmethod
    def get_drop_files(cls, a0):
        from urllib.parse import unquote
        file_list = []
        urls = a0.mimeData().urls()
        for url in urls:
            file_url = url.toString()
            
            if file_url.startswith("file:///"):  # 本地路径
                file_path = unquote(file_url.replace("file:///", ""))
            elif file_url.startswith("file://"):  # 网络路径
                file_path = unquote(file_url.replace("file:", ""))
            else:
                raise Exception(f'不支持的文件拖入类型:{file_url}')
            file_list.append(file_path)
        return file_list


class BaseLayer(BaseFrame):
    name = 'layer'
    column = 4
    _head = None
    _values = None
    
    def _init_argument(self):
        self.main_layout = QVBoxLayout(self)
        self.top_operate = QFrame()
        self.top_layout = QGridLayout(self.top_operate)
        self.tw = QTableWidget()
        self.pb_refresh = self.BTN('刷新')
    
    def _init_setting(self):
        self.pb_refresh.clicked.connect(self.refresh)
    
    def _init_view(self):
        self.main_layout.addWidget(self.top_operate)
        self.main_layout.addWidget(self.tw)
        self.refresh()
    
    def refresh(self):
        self.load_tw_header()
        self.load_tw_info(self.info())
    
    def BTN(self, *args, **kwargs) -> 'QPushButton':
        btn = QPushButton(*args, **kwargs)
        self.add_btn(btn)
        return btn
    
    def add_btn(self, btn):
        layout = self.top_layout
        count = layout.count()
        row = count // self.column
        col = count % self.column
        layout.addWidget(btn, row, col, 1, 1)
    
    def load_tw_header(self):
        header = self.tw_header()
        if not header:
            return
        self.tw.setColumnCount(len(header))
        for col, (field, name) in enumerate(header.items()):
            self.head[col] = field
            self.head[field] = col
            name = name or field
            self.tw.setHorizontalHeaderItem(col, QTableWidgetItem(name))
    
    def load_tw_info(self, infos):
        if not infos:
            return
        cols = self.tw.columnCount()
        self._values = infos
        self.tw.setRowCount(len(infos))
        for row, info in enumerate(infos):
            for col in range(cols):
                field: str = self.head.get(col)
                if not field:
                    continue
                if field.endswith('&') and field.count('&') == 2:
                    btn_field = field.split('&')[1]
                    ac_field = field.split('&')[0]
                    
                    self.load_buttons(row, col, ac_field, btn_field)
                else:
                    val = info.get(field) or ''
                    item = QTableWidgetItem(str(val))
                    self.tw.setItem(row, col, item)
    
    def load_buttons(self, row, col, field, btn_field):
        btn = QPushButton('')
        btn.row = row
        btn.field = field
        btn.clicked.connect(self.slot_tw_button)
        if not btn_field:
            btn.setText('-->')
        else:
            icon_name = button_fields.get(btn_field)
            if icon_name:
                btn.setIcon(QIcon(icon_name))
        
        self.tw.setCellWidget(row, col, btn)
        return btn
    
    def layerList(self) -> 'LayerList':
        layer_list = self.parent().parent().parent()
        return layer_list
    
    def row_info(self, row) -> dict:
        if row >= len(self.values):
            raise f'查询行数超范围0-{len(self.values) - 1}:{row}'
        return self.values[row]
    
    def select_rows(self) -> '[int]':
        items = self.tw.selectedItems()
        rows = []
        for item in items:
            row = item.row()
            if row not in rows:
                rows.append(row)
        return rows
    
    def layerName(self):
        pass
    
    def layerIndex(self):
        pass
    
    def info(self):
        pass
    
    def tw_header(self) -> dict:
        return
    
    def button_callback(self, row, field, button):
        assert isinstance(row, int) and isinstance(field, str), f'按键响应参数错误int, str:{type(row), type(field)}'
    
    # SLOT
    def slot_tw_button(self):
        button = self.sender()
        if not isinstance(button, QPushButton):
            return
        row = button.row
        field = button.field
        self.button_callback(row, field, button)
    
    @property
    def head(self):
        if not isinstance(self._head, dict):
            self._head = {}
        return self._head
    
    @property
    def values(self):
        if not isinstance(self._values, list):
            self._values = []
        return self._values


class LayerFile(BaseLayer):
    name = ''
    
    def __init__(self, prefix, rcc: 'RCC'):
        self.qresource = rcc[prefix]
        super().__init__()
    
    def _init_argument(self):
        super()._init_argument()
        self.pb_add = self.BTN('新增文件')
        self.pb_delete = self.BTN('删除')
        self.pb_paste_svg = self.BTN('粘贴SVG')
        self.pb_show_files = self.BTN('全显示')
        self.pb_save = self.BTN('保存')
    
    def _init_setting(self):
        super()._init_setting()
        self.setAcceptDrops(True)
        self.tw.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pb_add.clicked.connect(self.slot_add_file)
        self.pb_delete.clicked.connect(self.slot_delete_file)
        self.pb_save.clicked.connect(self.slot_save_file)
        
        self.pb_paste_svg.clicked.connect(self.slot_paste_svg)
        self.pb_show_files.clicked.connect(self.slot_show_files)
        
        self.pb_save.setVisible(False)
        self.pb_save.setAutoFillBackground(True)
    
    def _init_view(self):
        super()._init_view()
    
    def dropEvent(self, a0) -> None:
        files = self.get_drop_files(a0)
        ok, info = InfoGet.get({'dir': '文件存放目录'})
        if not ok:
            return
        file_prefix = info.get('dir', )
        self.qresource.addFiles(files, file_prefix, )
        self.refresh()
        self.pb_save.setVisible(True)
    
    def dragEnterEvent(self, a0) -> None:
        a0.accept()
    
    def layerName(self):
        return f'文件({self.qresource.prefix})'
    
    def layerIndex(self):
        return f'resource: {self.qresource.rcc.rcCfg.name}-{self.qresource.rcc.name}-{self.qresource.prefix}'
    
    def info(self):
        infos = []
        for rcc in self.qresource.list():
            infos.append(rcc.info)
        return infos
    
    def tw_header(self) -> dict:
        return {
            'name'                : '文件名',
            'dir'                 : '目录',
            'show'                : '资源显示',
            'copy_scrPath&copy&'  : '资源路径',
            'setBorderImage&copy&': 'setBorderImage',
        }
    
    def button_callback(self, row, field, button):
        super().button_callback(row, field, button)
        if field == 'copy_scrPath':
            info = self.row_info(row)
            srcPath = info['srcPath']
            self.add_clipboardText(srcPath)
            button.setText('已复制!')
            QTimer.singleShot(2000, lambda text='-->': button.setText(text))
        elif field == 'setBorderImage':
            info = self.row_info(row)
            srcPath = info['srcPath']
            text = f"self.setBorderImage('{srcPath}')\n"
            self.add_clipboardText(text)
            button.setText('已复制!')
            QTimer.singleShot(2000, lambda text='-->': button.setText(text))
    
    def slot_add_file(self):
        files, filter_str = QFileDialog.getOpenFileNames(self, '新增文件', '', '*')
        if not files:
            return
        self.qresource.addFiles(files, )
        self.refresh()
        self.pb_save.setVisible(True)
    
    def slot_delete_file(self):
        rows = self.select_rows()
        if not rows:
            return
        row = rows[0]
        row_info = self.row_info(row)
        src_path = row_info.get('src_path')
        self.qresource.removeFile(src_path)
        self.refresh()
        self.pb_save.setVisible(True)
    
    def slot_paste_svg(self):
        text = self.get_clipboardText()
        if not text:
            return
        if not text.startswith('<svg'):
            return QMessageBox.information(self, '提示', '复制内容不符合SVG格式: <svg')
        
        ok, info = InfoGet.get({'dir': '文件存放目录', 'name': '文件名称(不含.svg)'}, {'dir': 'static', 'name': 'abc'})
        if not ok:
            return
        dir_ = info.get('dir')
        name = info.get('name')
        svg_name = f'{name}.svg'
        file = self.qresource.file(svg_name, dir_)
        file.write(text)
        self.refresh()
        self.pb_save.setVisible(True)
    
    def slot_show_files(self):
        self.tw_files = TWFiles(self.qresource.files)
        self.tw_files.show()
    
    def slot_save_file(self):
        self.qresource.rcc.save()
        self.pb_save.setVisible(False)


class LayerQResource(BaseLayer):
    name = '资源'
    
    def __init__(self, rcc_name, cfg: ResourceCfg):
        self.rcc = cfg.loadQrcRCC(rcc_name, cfg)
        super().__init__()
    
    def _init_argument(self):
        super()._init_argument()
        self.pb_add = self.BTN('新增')
        self.pb_delete = self.BTN('删除')
        self.pb_load_py = self.BTN('加载Py')
        self.pb_savePy = self.BTN('保存Py')
    
    def _init_setting(self):
        super()._init_setting()
        self.tw.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pb_add.clicked.connect(self.slot_add_resource)
        self.pb_savePy.clicked.connect(self.slot_save_py_info)
        self.pb_load_py.clicked.connect(self.slot_load_py)
    
    def _init_view(self):
        super()._init_view()
    
    def layerName(self):
        return f'资源({self.rcc.name})'
    
    def layerIndex(self):
        return f'rcc: {self.rcc.rcCfg.name}-{self.rcc.name}'
    
    def info(self):
        infos = []
        for rcc in self.rcc.list():
            infos.append(rcc.info)
        return infos
    
    def tw_header(self) -> dict:
        return {
            'prefix'              : '前缀',
            'to_qresource&jumpto&': '查看文件'
        }
    
    def button_callback(self, row, field, button):
        super().button_callback(row, field, button)
        if field == 'to_qresource':
            info = self.row_info(row)
            prefix = info['prefix']
            self.layerList().addLayer(LayerFile(prefix, self.rcc))
    
    def slot_add_resource(self):
        ok, info = InfoGet.get({'prefix': '资源前缀'})
        if not ok:
            return
        prefix = info.get('prefix')
        self.rcc.addResource(prefix)
        self.refresh()
    
    def slot_save_py_info(self):
        self.rcc.toPy()
    
    def slot_load_py(self):
        try:
            py_rcc = self.rcc.rcCfg.loadPyRCC(self.rcc.name, self.rcc.rcCfg, load_py=True)
        except Exception as e:
            return QMessageBox.information(self, '提示', f'加载py错误: {e}')


class LayerRcc(BaseLayer):
    name = '配置'
    
    def __init__(self, cfg_name=None):
        self.cfg = qrc[cfg_name]
        super().__init__()
    
    def _init_argument(self):
        super()._init_argument()
        self.pb_add = self.BTN('新增')
        self.pb_delete = self.BTN('删除')
        self.pb_tree = self.BTN('树状结构')
    
    def _init_setting(self):
        super()._init_setting()
        self.tw.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pb_add.clicked.connect(self.slot_add_rcc)
        self.pb_delete.clicked.connect(self.slot_delete_rcc)
        self.pb_tree.clicked.connect(self.slot_tree_info)
    
    def _init_view(self):
        super()._init_view()
    
    def layerName(self):
        return f'配置({self.cfg.name})'
    
    def layerIndex(self):
        return f'cfg: {self.cfg.name}'
    
    def info(self):
        infos = []
        for rcc in self.cfg.list():
            infos.append(rcc.info)
        return infos
    
    def tw_header(self) -> dict:
        return {
            'name'                : '名称',
            'file'                : '资源文件',
            'py_file'             : 'Py文件',
            'to_qresource&jumpto&': '查看资源',
            'copy_load_py&copy&'  : '资源导入',
        }
    
    def button_callback(self, row, field, button):
        super().button_callback(row, field, button)
        if field == 'to_qresource':
            info = self.row_info(row)
            name = info['name']
            self.layerList().addLayer(LayerQResource(name, self.cfg))
        elif field == 'copy_load_py':
            info = self.row_info(row)
            cfg_name = self.cfg.name
            rcc_name = info.get('name')
            load_text = f'qrc.load_cfg_py_rcc("{cfg_name}.{rcc_name}")\n'
            self.add_clipboardText(load_text)
    
    def slot_add_rcc(self):
        ok, info = InfoGet.get({'name': '资源名称'})
        if not ok:
            return
        name = info.get('name')
        
        rcc = self.cfg[name]
        if rcc:
            return QMessageBox.information(self, '提示', f'已存在:{name}')
        from utils.qrcManage.demo.demo1 import QrcRcc
        
        rcc = QrcRcc(name, self.cfg)
        self.cfg.addRcc(rcc)
        qrc.save()
        self.refresh()
    
    def slot_delete_rcc(self):
        rows = self.select_rows()
        if not rows:
            return
        row = rows[0]
        row_info = self.row_info(row)
        name = row_info.get('name')
        self.cfg.removeRcc(name)
        qrc.save()
        self.refresh()
    
    def slot_tree_info(self):
        self.tree = TreeShow(self.cfg, all_expand=True)
        self.tree.show()


class LayerCfg(BaseLayer):
    name = '配置列表'
    
    def _init_argument(self):
        super()._init_argument()
        self.pb_add = self.BTN('新增')
        self.pb_change = self.BTN('编辑')
        self.pb_delete = self.BTN('删除')
        self.pb_save_cfg = self.BTN('保存配置')
    
    def _init_setting(self):
        super()._init_setting()
        self.tw.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.pb_add.clicked.connect(self.slot_add_cfg)
        self.pb_change.clicked.connect(self.slot_change_cfg)
        self.pb_delete.clicked.connect(self.slot_delete_cfg)
        self.pb_save_cfg.clicked.connect(qrc.save)
    
    def _init_view(self):
        super()._init_view()
    
    def layerName(self):
        return '配置列表'
    
    def layerIndex(self):
        return ''
    
    def info(self):
        infos = []
        for cfg in qrc.list():
            infos.append(cfg.info)
        return infos
    
    def tw_header(self) -> dict:
        return {
            'name'                  : '配置名称',
            'rccList'               : '资源列表',
            'resource_dir'          : '资源目录',
            'py_qrc_prefix'         : 'Py资源前缀',
            'load_dir'              : 'Py加载目录',
            'to_rcc&jumpto&'        : '查看配置',
            'copy_load_all_py&copy&': '全导入',
        }
    
    def button_callback(self, row, field, button):
        super().button_callback(row, field, button)
        if field == 'to_rcc':
            info = self.row_info(row)
            name = info.get('name')
            self.layerList().addLayer(LayerRcc(name))
        elif field == 'copy_load_all_py':
            info = self.row_info(row)
            name = info.get('name')
            load_text = f'qrc.load_cfg_all_py_rcc("{name}")'
            self.add_clipboardText(load_text)
        else:
            pass
    
    # SLOT
    def slot_add_cfg(self):
        header = self.tw_header()
        header.pop('rccList', None)
        for name in list(header):
            if name.endswith('&'):
                header.pop(name, None)
        
        ok, info = InfoGet.get(header)
        if not ok:
            return
        cfg = ResourceCfg(**info)
        qrc.save()
        self.refresh()
    
    def slot_change_cfg(self):
        rows = self.select_rows()
        if not rows:
            return
        row = rows[0]
        
        pass
    
    def slot_delete_cfg(self):
        rows = self.select_rows()
        if not rows:
            return
        row = rows[0]
        row_info = self.row_info(row)
        name = row_info.get('name')
        ok = QMessageBox.question(self, '提示', f'确认删除配置:{name}') == QMessageBox.Yes
        if ok:
            try:
                qrc.removeCfg(name)
            except Exception as e:
                printExc()
                return QMessageBox.information(self, '提示', f'删除失败: {e}')
        self.refresh()


class LayerList(BaseFrame):
    
    def _init_argument(self):
        super()._init_argument()
        self.main_layout = QVBoxLayout(self)
        self.tab = QTabWidget()
    
    def _init_setting(self):
        super()._init_setting()
        self.setGeometry(450, 150, 1080, 720)
        self.tab.setTabsClosable(True)
        
        self.tab.tabCloseRequested.connect(self.slot_close_request)
    
    def _init_view(self):
        super()._init_view()
        self.main_layout.addWidget(self.tab)
    
    def addLayer(self, layer: BaseLayer):
        layer_index = layer.layerIndex()
        exists_layer = self.getLayerByIndex(layer_index)
        if not exists_layer:
            exists_layer = layer
            self.tab.addTab(layer, layer.layerName())
        
        self.tab.setCurrentWidget(exists_layer)
    
    def getLayerByIndex(self, layer_index):
        for index in range(self.tab.count()):
            widget: BaseLayer = self.tab.widget(index)
            if widget.layerIndex() == layer_index:
                return widget
    
    # SLOT
    def slot_close_request(self, index):
        if index == 0:
            return
        widget: BaseLayer = self.tab.widget(index)
        layer_index = widget.layerIndex()
        
        self.tab.removeTab(index)


if __name__ == '__main__':
    """
    Main run
    """
    
    app = QApplication(sys.argv)
    
    ui = LayerList()
    ui.show()
    ui.addLayer(LayerCfg())
    
    sys.exit(app.exec_())
