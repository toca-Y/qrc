import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QDialog, QFormLayout, QLabel, QLineEdit, QApplication, QPushButton, QTreeWidget, \
    QTreeWidgetItem


class InfoGet(QDialog):
    
    def __init__(self, fields, info=None):
        super().__init__()
        info = info or {}
        self.fields = fields
        self.info = info
        self.field_labels = {}
        layout = QFormLayout(self)
        for field, name in fields.items():
            val = info.get(field) or ''
            label = QLabel(name)
            line_edit = QLineEdit(val)
            layout.addRow(label, line_edit)
            self.field_labels[field] = line_edit
        affirm = QPushButton('确认')
        affirm.clicked.connect(self.accept)
        layout.addRow('', affirm)
    
    def change_info(self):
        info = {}
        change_info = {}
        for field, label in self.field_labels.items():
            value = label.text()
            old_value = self.info.get(field)
            info[field] = value
            if value != old_value:
                change_info[field] = value
        return info, change_info
    
    @classmethod
    def get(cls, fields, info=None):
        view = InfoGet(fields, info)
        if view.exec_() == QDialog.Accepted:
            info, change_info = view.change_info()
            return True, info
        return False, None


class TreeShow(QTreeWidget):
    
    def __init__(self, obj, all_expand=False):
        self.obj = obj
        super().__init__()
        self.load()
        self.setColumnCount(2)
        self.itemExpanded.connect(self.slot_itemExp)
        if all_expand:
            self.expandAll()
    
    def load(self):
        self._load_item(self.obj)
    
    def _load_item(self, obj, topLevelItem: QTreeWidgetItem = None):
        if topLevelItem:
            for index in range(topLevelItem.childCount()):
                item = topLevelItem.child(index)
                topLevelItem.removeChild(item)

        for o, name in obj.treeInfo:
            
            item = QTreeWidgetItem()
            item.obj = o
            item.setText(1, name)
            if o:
                item.addChild(QTreeWidgetItem())
            if topLevelItem:
                topLevelItem.addChild(item)
            else:
                self.addTopLevelItem(item)
    
    def slot_itemExp(self, item):
        obj = getattr(item, 'obj', None)
        if not obj:
            return
        self._load_item(obj, item)

        pass


if __name__ == '__main__':
    """
    Main run
    """
    
    app = QApplication(sys.argv)
    fi = {
        'name'         : '配置名称',
        'rccList'      : '资源列表',
        'resource_dir' : '资源目录',
        'py_qrc_prefix': 'Py资源前缀',
        'load_dir'     : 'Py加载目录',
        'to_rcc&&'     : '查看配置'
    }
    print(InfoGet.get(fi, ))
