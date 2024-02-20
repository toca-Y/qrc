import json
import shutil
import traceback
from pathlib import Path
from typing import List, Union, Dict

from utils.qrcManage.error_model import *

_resource_instance = None
_cfg_list: Dict[str, 'ResourceCfg'] = {}

qrc_root_dir = 'qrcResource'

_default_field = 'default'


def set_resource(resource: 'ResourceCfg'):
    global _resource_instance
    _resource_instance = resource


def cfg_list():
    return {**_cfg_list}


class QrcExtends:
    _old_data = None
    
    def __getitem__(self, item) -> 'ResourceCfg':
        if isinstance(item, ResourceCfg):
            return item
        return _cfg_list.get(item)
    
    def list(self) -> List['ResourceCfg']:
        return list(_cfg_list.values())
    
    def load(self):
        try:
            read_txt = default_config.read()
            data = json.loads(read_txt)
        except:
            printExc()
            data = []
        self._old_data = data
        for info in data:
            ResourceCfg.load(info)
    
    def save(self):
        data = self.info
        if data == self._old_data:
            return
        self._old_data = data
        dump_data = json.dumps(data)
        default_config.write(dump_data)
        
        defaultRcc.save(qrc_save=False)
    
    @classmethod
    def cfg_list(cls):
        return cfg_list()
    
    @classmethod
    def load_cfg_all_py_rcc(cls, cfg_name, ignore_error=False):
        cfg = _cfg_list.get(cfg_name)
        if not cfg:
            raise IndexError(f'未知的资源配置: {cfg_name}')
        for rcc_name in cfg.rccList:
            try:
                cfg.loadPyRCC(rcc_name, cfg, check_exists=True, load_py=True)
            except Exception as e:
                printExc()
                if not ignore_error:
                    raise e
    
    @classmethod
    def load_cfg_py_rcc(cls, name: str) -> 'PyRcc':
        # name: default.resource
        if not name.count('.') == 1:
            raise ValueError(f'错误的导入名称: {name}')
        cfg_name, rcc_name = name.split('.')
        cfg = _cfg_list.get(cfg_name)
        if not cfg:
            raise IndexError(f'未知的资源配置: {cfg_name}')
        if rcc_name not in cfg.rccList:
            raise IndexError(f'未知的资源: {rcc_name}')
        rcc = cfg.loadPyRCC(rcc_name, cfg, check_exists=True, load_py=True)
        return rcc
    
    @classmethod
    def removeCfg(cls, cfg: Union[str, 'ResourceCfg']):
        cfg_name = cfg
        if isinstance(cfg, ResourceCfg):
            cfg_name = cfg.name
        if cfg_name == _default_field:
            raise Exception('默认配置不可以删除')
        cfg = _cfg_list.pop(cfg_name, None)
        cfg.delete()
    
    @property
    def info(self):
        return [
            cfg.info
            for name, cfg in _cfg_list.items()
            if name != _default_field
        ]


class ResourceCfg:
    name = None
    _resource_dir = 'defaultCfg'
    _load_dir = ''
    _py_qrc_prefix = 'qrc'
    
    _rcc_list = None
    
    def __init__(self, name, resource_dir=None, load_dir=None, py_qrc_prefix=None, **kwargs):
        self.name = name
        self.resource_dir = resource_dir or name or self._resource_dir
        # self.load_dir = load_dir or self._load_dir
        self.py_qrc_prefix = py_qrc_prefix or self._py_qrc_prefix
        _cfg_list[name] = self
    
    def __getitem__(self, item):
        return self.rccList.get(item)
    
    def addRcc(self, rcc):
        self.rccList[rcc.name] = rcc
    
    def list(self) -> List['RCC']:
        return list(self.rccList.values())
    
    def removeRcc(self, rcc: Union[str, 'RCC']):
        from utils.qrcManage.demo.demo1 import RCC
        
        if isinstance(rcc, RCC):
            rcc_obj = rcc
        else:
            rcc_obj = self[rcc]
            if not rcc_obj:
                raise Exception('资源信息不存在')
        self.rccList.pop(rcc_obj.name, None)
        rcc_obj.delete()
    
    def delete(self):
        for rcc in list(self.rccList.values()):
            self.removeRcc(rcc)
        if self._resource_dir:
            shutil.rmtree(self.resource_dir, ignore_errors=True)
    
    @classmethod
    def load(cls, info: dict) -> 'ResourceCfg':
        assert isinstance(info, dict), f'类型错误dict:{type(info)}'
        cfg = ResourceCfg(info.get('name'))
        cfg.resource_dir = info.get('resource_dir')
        # cfg.load_dir = info.get('load_dir')
        cfg.py_qrc_prefix = info.get('py_qrc_prefix')
        rccList = info.get('rccList') or []
        for rcc_name in rccList:
            rcc = cls.loadQrcRCC(rcc_name, cfg)
            cfg.addRcc(rcc)
        return cfg
    
    @classmethod
    def loadQrcRCC(cls, name, cfg):
        
        from utils.qrcManage.demo.demo1 import QrcRcc
        rcc = cfg.rccList.get(name)
        if not rcc:
            rcc = QrcRcc(name, rcCfg=cfg)
            cfg.rccList[name] = rcc
        return rcc
    
    @classmethod
    def loadPyRCC(cls, name, cfg, check_exists=False, load_py=False, ):

        from utils.qrcManage.demo.demo1 import PyRcc
        rcc = PyRcc(name, rcCfg=cfg, check_exists=check_exists, load_py=load_py)
        return rcc
    
    @property
    def treeInfo(self):
        return [
            (rcc, name)
            for name, rcc in self.rccList.items()
        ]
    
    @property
    def info(self):
        return {
            'name'         : self.name,
            'rccList'      : list(self.rccList.keys()),
            'resource_dir' : self._resource_dir,
            # 'load_dir'     : self.load_dir,
            'py_qrc_prefix': self.py_qrc_prefix
        }
    
    @property
    def resource_dir(self):
        return f'{qrc_root_dir}/{self._resource_dir}'
    
    @resource_dir.setter
    def resource_dir(self, value):
        self._resource_dir = value
    
    @property
    def load_dir(self):
        return self._load_dir
    
    @load_dir.setter
    def load_dir(self, value):
        self._load_dir = value
    
    @property
    def py_qrc_prefix(self):
        return self._py_qrc_prefix
    
    @py_qrc_prefix.setter
    def py_qrc_prefix(self, value):
        self._py_qrc_prefix = value
    
    @property
    def rccList(self) -> dict:
        if not isinstance(self._rcc_list, dict):
            self._rcc_list = {}
        return self._rcc_list
    
    @classmethod
    def instance(cls):
        global _resource_instance
        # if not isinstance(_resource_instance, ResourceCfg):
        #     _resource_instance = ResourceCfg()
        return _resource_instance
    
    @classmethod
    def instanceResourceDir(cls):
        return ResourceCfg.instance().resource_dir


defaultCfg = ResourceCfg(_default_field, 'defaultCfg')
defaultRcc = defaultCfg.loadQrcRCC('resource', defaultCfg)
resource = defaultRcc['config']
default_config = resource.file('config.json')

qrc_icon = defaultCfg.loadQrcRCC('qrc_icon', defaultCfg)

_resource_instance = defaultCfg
qrc = QrcExtends()

qrc.load()


def resourceDir():
    return ResourceCfg.instance().resource_dir
