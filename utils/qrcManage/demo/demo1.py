import importlib
import os
import shutil
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Union

from utils.qrcManage.error_model import *


class File:
    def __init__(self, resource, src_path):
        self.resource: qresource = resource
        self.src_path = src_path
    
    def exists(self) -> bool:
        try:
            from PyQt5.QtCore import QFile
            return QFile(self.srcPath).exists()
        except:
            printExc()
    
    def icon(self) -> "QIcon":
        from PyQt5.QtGui import QIcon
        
        icon = QIcon(self.srcPath)
        return icon
    
    def pixmap(self) -> "QPixmap":
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(self.srcPath)
        return pixmap
    
    def data(self) -> bytes:
        from PyQt5.QtCore import QResource
        data = QResource(self.srcPath).data()
        return data
    
    def read(self):
        try:
            import os
            with open(self.localPath, 'r') as f:
                return f.read()
        except FileNotFoundError:
            printExc()
            return ''
    
    def write(self, data: str):
        try:
            print(self.localPath)
            Path(self.localPath).parent.mkdir(parents=True, exist_ok=True)
            with open(self.localPath, 'w') as f:
                f.write(data)
            print(self.src_path)
        except:
            printExc()
            return
    
    def awrite(self, data: str):
        try:
            Path(self.localPath).parent.mkdir(parents=True, exist_ok=True)
            with open(self.localPath, 'a+') as f:
                f.write(data)
        except:
            printExc()
            return
    
    def savePy(self):
        self.resource.rcc.toPy()
    
    def delete(self):
        self.localPath.unlink(missing_ok=True)
    
    @classmethod
    def file_exists(cls, path):
        from PyQt5.QtCore import QFile
        return QFile(path).exists()
    
    @property
    def info(self):
        p_scr_path = Path(self.src_path)
        return {
            'name'    : p_scr_path.name,
            'dir'     : p_scr_path.parent.as_posix(),
            'src_path': self.src_path,
            'srcPath' : self.srcPath
        }
    
    @property
    def srcPath(self) -> str:
        return f':{self.prefix}/{self.src_path}'
    
    @property
    def localPath(self) -> Path:
        return Path(self.resource.rcc.root_dir).joinpath(self.src_path)
    
    @property
    def tarPath(self):
        return self.src_path
    
    @property
    def prefix(self):
        return self.resource.prefix
    
    def __str__(self):
        return self.srcPath


class qresource:
    _files = None
    prefix = None
    rcc = None
    
    def __init__(self, prefix: str, rcc: 'RCC'):
        assert isinstance(prefix, str), '类型错误: str'
        assert isinstance(rcc, RCC), '类型错误: str'
        self.rcc: "RCC" = rcc
        if prefix:
            if not prefix.startswith('/'):
                prefix = '/' + prefix
            self.prefix = prefix
    
    def __getitem__(self, item) -> 'File':
        return File(self, item)
    
    def addFile(self, file, file_prefix: str = '', name=None, reload=False):
        # file_prefix: 文件路径
        
        p_file = Path(file)
        file_name = p_file.name
        qrc_file = name or file_name
        if file_prefix:
            qrc_file = f'{file_prefix}/{file_name}'
        
        target_file = self.rcc.root_dir.joinpath(qrc_file)
        existed_file = self.get_file(qrc_file)
        
        if existed_file:
            if not Path(target_file).exists():
                self.files.remove(existed_file)
            else:
                if not reload:
                    print('已存在')
                    return
                else:
                    self.files.remove(existed_file)
        
        if reload \
                or p_file != target_file \
                or not target_file.exists() \
                or p_file.stat().st_size != target_file.stat().st_size:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            # shutil.copy2(p_file, target_file, )
            try:
                shutil.copyfile(p_file, target_file, )
            except shutil.SameFileError:
                # 文件是同一个
                print('文件是同一个')
        self._add_file(qrc_file)
    
    def addFiles(self, files, file_prefix='', reload=True):
        for file in files:
            self.addFile(file, file_prefix, reload=reload)
    
    def file(self, file_name, file_prefix: str = '') -> 'File':
        
        qrc_file = file_name
        if file_prefix:
            qrc_file = f'{file_prefix}/{file_name}'
        existed_file = self.get_file(qrc_file)
        if not existed_file:
            self._add_file(qrc_file)
        return self[qrc_file]
    
    def _add_file(self, qrc_file):
        self.files.append(File(self, qrc_file))
    
    def get_file(self, qrc_file) -> 'File':
        for file in self.files:
            if qrc_file == file.tarPath:
                return file
    
    def list(self):
        return self.files
    
    def removeFile(self, file: Union[str, 'File']):
        if not file:
            return
        if isinstance(file, File):
            file_obj = file
        else:
            file_obj = self.get_file(file)
        if not file_obj:
            return
        file_obj.delete()
        try:
            self.files.remove(file_obj)
        except Exception as e:
            raise Exception(f'删除失败: {e}')
    
    def delete(self):
        for file in self.files:
            self.removeFile(file)
    
    @property
    def files(self) -> List[File]:
        if not self._files:
            self._files = []
        return self._files
    
    @property
    def treeInfo(self):
        return [
            (None, file.src_path)
            for file in self.files
        ]
    
    @property
    def info(self):
        return {
            'prefix': self.prefix
        }
    
    def __eq__(self, other: str):
        return self.prefix.strip('/') == str(other).strip('/')
    
    def __str__(self):
        files = [str(file) for file in self.files]
        return f'<{self.prefix}: ({len(self.files)})-[{", ".join(files)}]>'


class RCC:
    name = None
    _resources = None
    _rcCfg = None
    
    _old_rcc_str = None
    
    def __init__(self, name='resource', rcCfg=None):
        self.name = name
        self._rcCfg = rcCfg
    
    def __getitem__(self, item) -> 'qresource':
        assert isinstance(item, str), '错误的类型: '
        resource = self.get_resource(item)
        if not resource:
            resource = self.addResource(item)
        return resource
    
    def addResource(self, resource: Union[str, qresource]) -> 'qresource':
        if isinstance(resource, qresource):
            qrc = resource
            qrc.rcc = self
            existed_qrc = self.get_resource(qrc.prefix)
        elif isinstance(resource, str):
            existed_qrc = self.get_resource(resource)
            if existed_qrc:
                qrc = existed_qrc
            else:
                qrc = qresource(resource, self)
        else:
            raise TypeError('错误的类型')
        if existed_qrc:
            print('qrc已存在')
            del qrc
            return existed_qrc
        else:
            self.resources.append(qrc)
            return qrc
    
    def loadQrc(self, qrc_file, ignore_parse_errors=False):
        try:
            tree = ET.parse(qrc_file)
        except Exception as e:
            if ignore_parse_errors:
                return
            raise QRCFileReadError(f'{e}')
        
        self.resources.clear()
        root = tree.getroot()
        for prefix_child in root:
            prefix = prefix_child.get('prefix')
            resource = qresource(prefix, self)
            for file in prefix_child:
                text = file.text
                resource._add_file(text)
            self.resources.append(resource)
        self._old_rcc_str = self.__str__()
    
    def loadPy(self, ):
        pass
    
    def _get_pyeD_file(self):
        return self._get_py_generate_file(['.py', '.pyd', '.so'])
    
    def _get_py_file(self):
        return self._get_py_generate_file(['.py'])
    
    def _get_py_generate_file(self, suffix_list):
        py_filename = f'{self.rcCfg.py_qrc_prefix}_{self.name}.*'
        p_dir = Path(self.root_dir)
        for file in p_dir.glob(py_filename):
            if file.suffix in suffix_list:
                return file
    
    def get_resource(self, prefix) -> 'qresource':
        for resource in self.resources:
            if resource == prefix:
                return resource
    
    def list(self):
        return self.resources
    
    def removeResource(self, resource: Union[str, 'qresource']):
        if isinstance(resource, qresource):
            resource_obj = resource
        else:
            resource_obj = self.get_resource(resource)
            if not resource_obj:
                raise Exception('前缀资源信息不存在')
        self.resources.remove(resource_obj)
        resource.delete()
    
    def delete(self):
        for resource in self.resources:
            self.removeResource(resource)
        
        # qrc delete
        self.file.unlink(missing_ok=True)
        
        # .py delete
        py_file = self._get_py_file()
        if py_file:
            py_file.unlink(missing_ok=True)
    
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
    
    @property
    def treeInfo(self):
        return [
            (resource, resource.prefix)
            for resource in self.resources
        ]
    
    @property
    def info(self):
        return {
            'name'   : self.name,
            'file'   : self.file,
            'py_file': self._get_py_file()
        }
    
    @property
    def file(self):
        file_name = f'{self.name}.qrc'
        file = Path(self.root_dir).joinpath(file_name)
        return file
    
    @property
    def resources(self) -> List[qresource]:
        if not self._resources:
            self._resources = []
        return self._resources
    
    @property
    def xml(self):
        root = ET.Element("RCC")
        for resource in self.resources:
            
            prefix_child = ET.SubElement(root, 'qresource')
            prefix_child.set('prefix', resource.prefix)
            for file in resource.files:
                file_child = ET.SubElement(prefix_child, 'file')
                file_child.text = file.tarPath
        return root
    
    @property
    def rcCfg(self):
        from utils.qrcManage.setting import ResourceCfg
        
        return self._rcCfg or ResourceCfg.instance()
    
    @property
    def root_dir(self) -> 'Path':
        return Path(self.rcCfg.resource_dir).joinpath(self.name)
    
    def __str__(self):
        content = '\n\t'.join([str(qrc) for qrc in self.resources])
        return f"{{\n: {self.name}\n\t{content}\n}}"


class QrcRcc(RCC):
    name = None
    
    def __init__(self, name='resource', rcCfg=None, load_qrc=True, ignore_parse_errors=False):
        super().__init__(name=name, rcCfg=rcCfg)
        self._rcCfg = rcCfg
        if load_qrc:
            self.loadQrc(self.file, ignore_parse_errors)
        self.rcCfg.addRcc(self)
    
    def __getitem__(self, item):
        return super().__getitem__(item)
    
    def loadQrc(self, qrc_file=None, ignore_parse_errors=False):
        qrc_file = qrc_file or self.file
        if not Path(qrc_file).exists():
            return
        super().loadQrc(qrc_file, ignore_parse_errors)
    
    def save(self, to_py=True, qrc_save=True):
        xml = self.xml
        Path(self.file).parent.mkdir(parents=True, exist_ok=True)
        tree = ET.ElementTree(xml)
        tree.write(self.file)
        
        if to_py:
            self.toPy()
        
        if qrc_save:
            from utils.qrcManage.setting import ResourceCfg, qrc
            
            qrc.save()
    
    def toPy(self):
        qrc_filename = self.file
        p_pyrcc5 = Path(sys.exec_prefix).joinpath('Scripts/pyrcc5.exe')
        if not p_pyrcc5.exists():
            raise FileExistsError('pyrcc转化工具不存在')
        py_filename = f'{self.rcCfg.py_qrc_prefix}_{qrc_filename.stem}.py'
        
        py_file = Path(self.root_dir).joinpath(py_filename)
        Path(py_file).parent.mkdir(parents=True, exist_ok=True)
        cmd = f'{p_pyrcc5} {qrc_filename} -o {py_file}'
        print(cmd)
        os.system(cmd)


class PyRcc(RCC):
    
    def __init__(self, name='resource', rcCfg=None, load_py=False, check_exists=True):
        super().__init__(name=name, rcCfg=rcCfg)
        if check_exists:
            py_file = self._get_pyeD_file()
            if not py_file:
                raise PyRccFileNotExists(rcCfg.name, name)
        if load_py:
            self.loadPy()
    
    def loadPy(self, py_file=None):
        
        if not py_file:
            py_file = self._get_pyeD_file()
        if not py_file:
            print('py资源文件不存在')
            return
        load_py.load_py(py_file, self)


class load_py:
    resource_list = []
    
    @classmethod
    def start_load(cls):
        cls.resource_list = RCC.list_resources()
    
    @classmethod
    def end_load(cls):
        new_resource_list = RCC.list_resources()
        files = []
        for file in new_resource_list:
            if file not in cls.resource_list:
                if file.count('/') < 2:
                    continue
                files.append(file)
        return files
    
    @classmethod
    def load_files_to_rcc(cls, files, rcc):
        for file in files:
            p1, prefix, file_text = file.split('/', 2)
            resource = rcc[prefix]
            resource._add_file(file_text)
    
    @classmethod
    def load_py(cls, py_file, rcc=None):
        if rcc:
            return cls.load_py_and_load(py_file, rcc)
        
        p_file = Path(py_file)
        module_name = p_file.stem
        import_list = [module_name]
        for parent in p_file.parents:
            if parent.name:
                import_list.insert(0, parent.name)
        import_name = '.'.join(import_list)
        print(f'import {import_name}')
        __import__(import_name)
    
    @classmethod
    def load_py_and_load(cls, py_file, rcc):
        cls.start_load()
        cls.load_py(py_file)
        files = cls.end_load()
        cls.load_files_to_rcc(files, rcc)


def demoNew():
    rcc = QrcRcc(ignore_parse_errors=True)
    print(rcc)
    qrc = rcc['static']
    qrc.addFile('demo3.py', reload=True)
    qrc.addFile('abc.txt')
    qrc.addFile(r'E:\casuallyToDo\utils\qrcManage\demo\icon\logo.png', name='logo')
    rcc.save()
    rcc.toPy()


def demoUse():
    rcc = PyRcc(load_py=True)
    qrc = rcc['static']
    file = qrc.get_file('abc.txt')
    print(file.data())
    file = qrc.get_file('demo3.py')
    print(file.data())


if __name__ == '__main__':
    """
    Main run
    """
    from PyQt5.QtCore import QFile
    
    demoNew()
    # demoUse()
