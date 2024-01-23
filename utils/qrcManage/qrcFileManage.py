import os
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def load_qt_qrc(qrc_file) -> dict:
    res_data = {}
    tree = ET.parse(qrc_file)
    root = tree.getroot()
    for prefix_child in root:
        prefix = prefix_child.get('prefix')
        files = res_data.setdefault(prefix, [])
        for file in prefix_child:
            text = file.text
            files.append(text)
    return res_data


def save_qt_qrc(source_json, filename):
    qresource_name = 'qresource'
    root = ET.Element("RCC")
    
    for prefix, files in source_json.items():
        prefix_child = ET.SubElement(root, qresource_name)
        prefix_child.set('prefix', prefix)
        for file in files:
            file_child = ET.SubElement(prefix_child, 'file')
            file_child.text = file
    
    tree = ET.ElementTree(root)
    tree.write(filename)


class QRCFile:
    _json_data = None
    
    def __init__(self, filename):
        self.filename = filename
        self.p_root = Path(self.filename).parent
        self.reload()
    
    def add_qrc_file(self, prefix: str, file, name=None, dir_='static', cover=False):
        if prefix.startswith('/'):
            prefix = prefix[1:]
        # 添加资源文件
        if isinstance(file, list):
            for index, a0 in enumerate(file):
                a1 = None
                if name and isinstance(name, list) and len(name) > index:
                    a1 = name[index]
                self.add_qrc_file(prefix, a0, a1)
        else:
            p_file = Path(file)
            not_copy = False
            
            if not p_file.exists():
                raise FileExistsError(f'文件不存在: {file}')
            if not name:
                name = p_file.name
            
            target_file = self.p_root.joinpath(dir_, name)
            file_name = target_file.relative_to(self.p_root).as_posix()
            if target_file.exists():
                if target_file == p_file:
                    not_copy = True
                elif cover:
                    target_file.unlink(missing_ok=True)
                else:
                    raise FileExistsError(f'目标文件已存在: {target_file}')
            target_file.parent.mkdir(0, True, True)
            if not not_copy:
                shutil.copy2(p_file, target_file)
            files = self.data.setdefault('/' + prefix, [])
            if file_name not in files:
                files.append(file_name)
                self.save()
    
    def toPy(self, qrc_filename=None, py_filename=None):
        qrc_filename = qrc_filename or self.filename
        p_pyrcc5 = Path(sys.exec_prefix).joinpath('Scripts/pyrcc5.exe')
        if not p_pyrcc5.exists():
            raise FileExistsError('pyrcc转化工具不存在')
        if not py_filename:
            py_filename = str(qrc_filename).split('.', 1)[0] + '.py'
        cmd = f'{p_pyrcc5} {qrc_filename} -o {py_filename}'
        os.system(cmd)
    
    def reload(self):
        try:
            data = load_qt_qrc(self.filename)
        except:
            data = {}
        self._json_data = data
    
    def save(self):
        save_qt_qrc(self._json_data, self.filename)
    
    def saveAs(self, filename):
        save_qt_qrc(self._json_data, filename)
    
    @property
    def data(self):
        if not isinstance(self._json_data, dict):
            self._json_data = {}
        return self._json_data


class Resource(str):
    def __init__(self, src_path):
        self.src_path = src_path
    
    def exists(self) -> bool:
        from PyQt5.QtCore import QFile
        return QFile(self.src_path).exists()
    
    def icon(self) -> "QIcon":
        from PyQt5.QtGui import QIcon
        
        icon = QIcon(self.src_path)
        return icon
    
    def pixmap(self) -> "QPixmap":
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(self.src_path)
        return pixmap
    
    def data(self) -> bytes:
        from PyQt5.QtCore import QResource
        data = QResource(self.src_path).data()
        return data
    
    def __str__(self):
        return self.src_path


class ResourceDir:
    pa = None
    name = 'static'
    prefix = None
    
    def __init__(self, prefix, name, pa=None):
        self.prefix = prefix
        self.name = name
        self.pa: QRCFileManager = pa
    
    def __getitem__(self, item) -> Resource:
        return self.get_resource(item)
    
    def set_parent(self, pa) -> 'ResourceDir':
        self.pa = pa
        return self
    
    def add_file(self, file, name=None, cover=True):
        self.pa.add_qrc_file(self.prefix, file, name=name, dir_=self.name, cover=cover)
    
    def get_resource(self, name) -> Resource:
        src_path = f':/{self.prefix}/{self.name}/{name}'
        return Resource(src_path)
    
    def copy(self):
        return self.__class__(prefix=self.prefix, name=self.name)
    
    def search(self, search_text='*'):
        res_list = []
        name_start = f':/{self.prefix}/{self.name}'
        resource_list = self.list_resources(name_start, f'*{search_text}*')
        for resource in resource_list:
            res_list.append(Resource(resource))
        return res_list
    
    @classmethod
    def list_resources(cls, name: str = None, filter_text='*'):
        resource_path = ":/"  # Adjust this path based on your resource structure
        resource_list = []
        if name:
            if not name.startswith(resource_path):
                resource_path = resource_path + name
            else:
                resource_path = name
        
        from PyQt5.QtCore import QDirIterator, QDir
        
        dir_iterator = QDirIterator(resource_path, [filter_text], QDir.Files, QDirIterator.Subdirectories)
        
        while dir_iterator.hasNext():
            file_name = dir_iterator.next()
            resource_list.append(file_name)
        return resource_list


class QRCFileManager(QRCFile):
    static = ResourceDir('static', 'static')
    
    def __init__(self, name: str, save_file=None):
        if not name.endswith('.qrc'):
            name += '.qrc'
        self.save_file = save_file
        super().__init__(name)
        self._load_src()
    
    def __setattr__(self, key, value):
        if isinstance(value, ResourceDir):
            if not value.pa:
                value.set_parent(self)
        super().__setattr__(key, value)
    
    def _load_src(self):
        for name in dir(self.__class__):
            src = getattr(self, name)
            if isinstance(src, ResourceDir):
                src = src.copy()
                src.set_parent(self)
                setattr(self, name, src)
    
    def toPy(self, qrc_filename=None, py_filename=None):
        py_filename = py_filename or self.save_file
        super().toPy(qrc_filename, py_filename)


class DemoLocalQRC(QRCFileManager):
    icon = ResourceDir('static', 'icon')
    image = ResourceDir('static', 'image')
    
    pass


local_qrc = DemoLocalQRC('local', save_file=Path(__file__).parent.joinpath('local.py'))


class A:
    name = '12'
    age = 23
    
    pass


if __name__ == '__main__':
    """
    Main run
    """
    # print(dir(DemoLocalQRC))
    # print(dir(QRCFileManager))
    # print(DemoLocalQRC.__dict__)
    # local_qrc.icon.add_file(r'F:\downloads_file\Chrome Download\稿定抠图.png', 'logo.png')
    # local_qrc.image.add_file(r"E:\NewCode\Camel\Erp-Gui\background.png", 'camel_background.png')
    # local_qrc.image.add_file(r"E:\NewCode\Camel\Erp-Gui\background.png", 'camel_background.png')
    local_qrc.image.add_file(r"E:\casuallyToDo\utils\qrcManage\demo\FirstQRC\image\black-1.png", 'abc.png')
    local_qrc.toPy()
    
    # import local
    # print(local_qrc.icon['logo.png'].exists())
